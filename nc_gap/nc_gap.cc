/*
-------------------------------------------------------------------------
OBJECT NAME:	nc_gap.cc

FULL NAME:	Locate netCDF Time Gaps

DESCRIPTION:	

COPYRIGHT:	University Corporation for Atmospheric Research, 2011
-------------------------------------------------------------------------
*/

#include <cstdlib>
#include <ctime>
#include <iomanip>
#include <string>
#include <cstring>

#include <netcdfcpp.h>

using namespace std;

static bool checkWholeFile = false;	// Just check when speed above 25 m/s (take-off).
static bool checkDerived = false;	// 
static bool gapGreaterThan = false;	// Only check for gaps greater than minGap
static bool gapLessThan = false;	// Only check for gaps less than maxGap

static int maxGap = 0;
static int minGap = 0;

void processArgs(char **argv);

/* -------------------------------------------------------------------- */
void
usage()
{
  cerr << "netCDF to IWG1.\n  Usage: nc_gap [-a] file.nc\n";
  cerr << "    Scan a netCDF file for time gaps and output gaps by variable.\n";
  cerr << "    -a : Check whole file.  By default only check GSF/TAS above 25 m/s.\n";
  cerr << "    -d : Include derived variables.  By default derived variables are skipped.\n";
  cerr << "    -l maxGap : Check for gaps less than maxGap seconds.\n";
  cerr << "    -g minGap : Check for gaps greater than minGap seconds.\n";
  exit(1);
}

time_t
startTime(NcVar *var)
{
  static time_t st = 0;

  if (st == 0)
  {
    // Get start time from Time units attribute.
    struct tm ft;
    NcAtt *time_units = var->get_att("units");
    strptime(time_units->as_string(0), "seconds since %F %T %z", &ft);
    st = mktime(&ft);
  }

  return st;
}

string
formatTime(NcVar *var, float *data, size_t index)
{
  char buffer[128];
  // Get start time, add Time data offset, and generate an ascii timestamp.
  time_t recordTime = startTime(var) + (time_t)data[index];
  struct tm *rt = gmtime(&recordTime);
  strftime(buffer, 128, "%H:%M:%S", rt);
  return buffer;
}


size_t
printStartTimes(NcFile & inFile, NcVar *timeVar, float *time_data)
{
  cout	<< "Start time data file : " << formatTime(timeVar, time_data, 0) << ", "
	<< timeVar->num_vals() << " seconds long.\n";

  if (checkWholeFile)
    return 0;

  // Get ground speed.
  NcVar *gspdVar =  inFile.get_var("GSPD");	// New INS name for ground speed.
  if (gspdVar == 0)
    gspdVar =  inFile.get_var("GSF");	// Old INS name for ground speed.
  if (gspdVar == 0)
    gspdVar = inFile.get_var("TASX");

  if (gspdVar == 0)
  {
    cerr << "GSPD, GSF, and TASX not found\n";
    return 0;
  }

  float *gspd_data = new float[gspdVar->num_vals()];
  gspdVar->get(gspd_data, gspdVar->edges());

  size_t spd_indx;
  for (spd_indx = 0; spd_indx < gspdVar->num_vals(); ++spd_indx)
  {
    if (gspd_data[spd_indx] > 5.0)
    {
      cout << "Start taxiing : " << formatTime(timeVar, time_data, spd_indx) << endl;
      break;
    }
  }

  for (; spd_indx < gspdVar->num_vals(); ++spd_indx)
  {
    if (gspd_data[spd_indx] > 25.0)
    {
      cout << "Start take-off : " << formatTime(timeVar, time_data, spd_indx) << endl;
      break;
    }
  }
  return spd_indx;
}

int
main(int argc, char *argv[])
{
  if (argc < 2)
    usage();

  processArgs(argv);

  NcFile inFile(argv[argc-1]);

  if (!inFile.is_valid())
  {
    cerr << "nc_gap: Failed to open input file, exiting.\n";
    return 1;
  }

  putenv((char *)"TZ=UTC");     // Perform all time calculations at UTC.
  NcError * ncErr = new NcError(NcError::silent_nonfatal);

  // Get time variable and data.
  NcVar *timeVar =  inFile.get_var("Time");
  float *time_data = new float[timeVar->num_vals()];
  timeVar->get(time_data, timeVar->edges());

  int start_indx = printStartTimes(inFile, timeVar, time_data);

  for (int i = 0; i < inFile.num_vars(); ++i)
  {
    NcVar *var = inFile.get_var(i);

    if (!var || !var->is_valid())
      continue;

    if (var->num_dims() > 1)	// Stick to time-series scalars for the time being.
      continue;

    // Are we skipping derived?
    if (checkDerived == false && var->get_att("Dependencies"))
      continue;


    float *data = new float[var->num_vals()];
    var->get(data, var->edges());

    for (int j = start_indx; j < var->num_vals(); ++j)
    {
      if (data[j] == -32767.0)	// Get missing value first.
      {
        int start = j;
        for (; j < var->num_vals() && data[j] == -32767.0; ++j)
          ;

        int gap = j-start;
        if ((gapLessThan && gap > maxGap) || (gapGreaterThan && gap < minGap))
          continue;

        cout << left << setw(20) << var->name();
        cout << formatTime(timeVar, time_data, start);
        cout << " - " << formatTime(timeVar, time_data, (j-1)) << " : ";
        if (gap == var->num_vals())
          cout << " whole flight.\n";
        else
          cout << setw(6) << gap << " seconds\n";
      }
    }

    delete [] data;
  }

}


void
processArgs(char **argv)
{
  while (*++argv)
    if ((*argv)[0] == '-')
      switch ((*argv)[1])
      {
        case 'a':
          checkWholeFile = true;	// normally just check starting at take-off
          break;

        case 'd':
          checkDerived = true;
          break;

        case 'l':
          gapLessThan = true;
          ++argv;
          maxGap = atoi(*argv);
          break;

        case 'g':
          gapGreaterThan = true;
          ++argv;
          minGap = atoi(*argv);
          break;

        case 'h':
          usage();
          break;
      }
}
