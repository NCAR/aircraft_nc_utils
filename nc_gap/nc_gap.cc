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

#include <netcdf>


static bool checkWholeFile = false;	// Just check when speed above 25 m/s (take-off).
static bool checkDerived = false;	// 
static bool gapGreaterThan = false;	// Only check for gaps greater than minGap
static bool gapLessThan = false;	// Only check for gaps less than maxGap

static int maxGap = 0;
static int minGap = 0;

void processArgs(char **argv);

using namespace std;
using namespace netCDF;


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
startTime(NcVar &var)
{
  static time_t st = 0;

  if (st == 0)
  {
    // Get start time from Time units attribute.
    struct tm ft;
    char frmt[128];
    NcVarAtt time_units = var.getAtt("units");
    time_units.getValues(frmt);
    strptime(frmt, "seconds since %F %T %z", &ft);
    ft.tm_isdst = -1;
    st = mktime(&ft);
  }

  return st;
}

string
formatTime(NcVar &var, float *data, size_t index)
{
  char buffer[128];
  // Get start time, add Time data offset, and generate an ascii timestamp.
  time_t recordTime = startTime(var) + (time_t)data[index];
  struct tm *rt = gmtime(&recordTime);
  strftime(buffer, 128, "%H:%M:%S", rt);
  return buffer;
}


float *
printStartTimes(NcFile *inFile, NcVar &timeVar, float *time_data)
{
  cout	<< "File start time : " << formatTime(timeVar, time_data, 0) << ", "
	<< timeVar.getDim(0).getSize() << " seconds long.\n";

  if (checkWholeFile)
    return 0;

  // Get ground speed.
  NcVar gspdVar =  inFile->getVar("GSPD");	// New INS name for ground speed.
  if (gspdVar.isNull())
    gspdVar =  inFile->getVar("GSF");	// Old INS name for ground speed.
  if (gspdVar.isNull())
    gspdVar = inFile->getVar("TASX");

  if (gspdVar.isNull())
  {
    cerr << "GSPD, GSF, and TASX not found\n";
    return 0;
  }

  int nValues = gspdVar.getDim(0).getSize();
  float *gspd_data = new float[nValues];
  gspdVar.getVar(gspd_data);

  size_t spd_indx;
  for (spd_indx = 0; spd_indx < nValues; ++spd_indx)
  {
    if (gspd_data[spd_indx] > 5.0)
    {
      cout << "Start taxiing   : " << formatTime(timeVar, time_data, spd_indx) << endl;
      break;
    }
    gspd_data[spd_indx] = 0.0;	// zero out any pre-take-off missing data.
  }

  for (; spd_indx < nValues; ++spd_indx)
  {
    if (gspd_data[spd_indx] > 25.0)
    {
      cout << "Take-off        : " << formatTime(timeVar, time_data, spd_indx) << endl;
      break;
    }
  }
  for (spd_indx = nValues - 1 ; spd_indx > 0; --spd_indx)
  {
    if (gspd_data[spd_indx] < 5.0)
      gspd_data[spd_indx] = 0.0;	// zero out an trailing missing values.

    if (gspd_data[spd_indx] > 25.0)
    {
      cout << "Landing         : " << formatTime(timeVar, time_data, spd_indx) << endl;
      break;
    }
  }
  cout	<< "File end time   : " << formatTime(timeVar, time_data, nValues-1) << endl;

  return gspd_data;
}

int
main(int argc, char *argv[])
{
  if (argc < 2)
    usage();

  processArgs(argv);

  NcFile * inFile = new NcFile(argv[argc-1], NcFile::read);

  if (inFile->isNull())
  {
    cerr << "nc_gap: Failed to open input file, exiting.\n";
    return 1;
  }

  putenv((char *)"TZ=UTC");     // Perform all time calculations at UTC.

  // Get time variable and data.
  NcVar timeVar =  inFile->getVar("Time");
  float *time_data = new float[timeVar.getDim(0).getSize()];
  timeVar.getVar(time_data);

  float *speed_data = printStartTimes(inFile, timeVar, time_data);

  std::multimap<std::string, NcVar> vars = inFile->getVars();
  for (auto it = vars.begin(); it != vars.end(); ++it)
  {
    NcVar var = it->second;

    if (var.getDimCount() > 1)	// Stick to time-series scalars for the time being.
      continue;

    // Are we skipping derived?
    if (checkDerived == false)
    {
      try {
        NcVarAtt att = var.getAtt("Dependencies");
        continue;
      } catch (netCDF::exceptions::NcException& e) { }
    }


    int numValues = var.getDim(0).getSize();
    float *data = new float[numValues];
    var.getVar(data);

    for (int j = 0; j < numValues; ++j)
    {
      if (speed_data && speed_data[j] >= 0.0 && speed_data[j] < 20.0)
        continue;

      if (data[j] == -32767.0)	// Get missing value first.
      {
        int start = j;
        for (; j < numValues && data[j] == -32767.0; ++j)
          ;

        int gap = j-start;
        if ((gapLessThan && gap > maxGap) || (gapGreaterThan && gap < minGap))
          continue;

        cout << left << setw(20) << var.getName();
        cout << formatTime(timeVar, time_data, start);
        cout << " - " << formatTime(timeVar, time_data, (j-1)) << " : ";
        if (gap == numValues)
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
