#include <iomanip>
#include <iostream>

#include <cstdlib>
#include <ctime>
#include <cstring>

#include <netcdf>

using namespace std;
using namespace netCDF;


float *
getData(NcFile * file, const char * name, size_t * step)
{
  NcDim dim;
  NcVar var = file->getVar(name);
  *step = 1;

  if (var.isNull())		// Variable does not exist.
  {
    cerr << "No variable " << name << "?" << endl;
    return 0;
  }

  // Figure out how many dimensions variable has
  int ndims = var.getDimCount();
  if (ndims > 1)
  {
    for (int i = 1; i < ndims; ++i)
      *step *= var.getDim(i).getSize();
  }

  float *data = new float[var.getDim(0).getSize() * *step];
  var.getVar(data);

  if (data == 0)
  {
    cerr << "No data for variable " << name << "?" << endl;
    return 0;
  }

  return data;
}


time_t
getStartTime(NcVar & time_var)
{
  NcVarAtt unit_att, frmt_att;
  try {
    unit_att = time_var.getAtt("units");
  } catch (netCDF::exceptions::NcException& e)
  {
    cerr << "Units attribute not present for time variable.\n";
    return 0;
  }

  try {
    frmt_att = time_var.getAtt("strptime_format");
  } catch (netCDF::exceptions::NcException& e) { }


  char units[128], format[128];
  unit_att.getValues(units);
  if (frmt_att.isNull())
    strcpy(format, "seconds since %F %T %z");
  else
    frmt_att.getValues(format);

  struct tm StartFlight;
  memset(&StartFlight, 0, sizeof(struct tm));
  StartFlight.tm_isdst = -1;
  strptime(units, format, &StartFlight);

  time_t start_t = mktime(&StartFlight);
  if (start_t <= 0)
    cerr << "Problem decoding units from Time variable, _start = " << start_t << endl;

  return start_t;
}


int
main(int argc, char *argv[])
{
  int	indx = 1;
  float	speed_cutoff = 25.0;	// Default ground speed for takeoff/landing. WOW uses 0.5
  char	variable[32] = "WOW_A";
  float	delta = 1.0; //Default for speed variables. For WOW, we use -1.0
  size_t step;
  bool	nimbus_output = false;
  bool	debug = false;
  bool  no_round_time = false;


  // Check arguments / usage.
  if (argc < 2)
  {
    cerr << "Print out take-off and landing times from a netCDF file. Uses weight on wheels.\n Use -v to specify speed variable and take speed above 25 m/s.\n\n";
    cerr << "Usage: flt_time [-d] [-s] [-r] [-v variable] netcdf_file\n";
    cerr << "Currently, cannot change cutoff value if selecting speed variable.\n";
    cerr << "-d debug output\n";
    cerr << "-s for nimbus setup file output ti=hh:mm:ss-hh:mm:ss\n";
    cerr << "-r to turn off rounding of time from the -s option.\n";
    exit(1);
  }

  while (argv[indx][0] == '-')
  {
    if (strcmp(argv[indx], "-d") == 0)
    {
      ++indx;
      debug = true;
    }
    else
    if (strcmp(argv[indx], "-s") == 0)
    {
      ++indx;
      nimbus_output = true;
    }
    else
    if (strcmp(argv[indx], "-r") == 0)
    {
      ++indx;
      no_round_time = true;
    }
    //Removing speed cutoff option until we can support -t and -v together
    // else
    // if (strcmp(argv[indx], "-t") == 0)
    // {
    //   ++indx;
    //   speed_cutoff = atof(argv[indx++]);
    // }
    else
    if (strcmp(argv[indx], "-v") == 0)
    {
      ++indx;
      strcpy(variable,argv[indx++]);
      if (strncmp(variable, "WOW", 3) == 0)
      {
      speed_cutoff = .5;
      delta = -1.0; // For Takeoff apply speed_cutoff when passes value decreasing
      }
    }
  }
  if (no_round_time && !nimbus_output)
  {
    cerr << "Option -r (no rounding) is only valid with -s (nimbus output).\n";
    exit(1);
  }


  putenv((char *)"TZ=UTC");     // Force all time routines to work in UTC.

  // Open NetCDF file
  NcFile *ncFile;
  try
  {
    ncFile = new NcFile(argv[indx], NcFile::read);
  } catch (netCDF::exceptions::NcException& e)
  {
    cerr << "Could not open NetCDF file '" << argv[indx] << "' for reading.\n";
    return 1;
  }

  NcGroupAtt project = ncFile->getAtt("project");
  if (project.isNull())
  {
    // If :project not present, look for :ProjectName
    project = ncFile->getAtt("ProjectName");
    if (project.isNull())
    {
      cerr << "Neither global variable :project nor :ProjectName present in file.\n";
      return 0;
    }
  }

  NcGroupAtt flight = ncFile->getAtt("FlightNumber");
  if (flight.isNull())
  {
    cerr << "Global variable :FlightNumber not present in file.\n";
    return 0;
  }

  if (!nimbus_output)
  {
    std::string proj, fl;
    project.getValues(proj);
    flight.getValues(fl);
    cout << argv[indx] << ":" << proj << ":" << fl << ":\n";
  }

  float *time_data = getData(ncFile, "Time", &step);
  if (time_data == 0)
  {
    cerr << "Variable Time not present in file.\n";
    return 0;
  }

  // If user specified variable, use that.
  // Try weight on wheels first, then ground speed, otherwise airspeed.
  // Update speed_cutoff and delta if variable is WOW
  float *speed_data = getData(ncFile, variable, &step);
  if (speed_data == 0)
  {
    strcpy(variable, "GSPD");
    speed_data = getData(ncFile, variable, &step);
    if (speed_data == 0)
    {
      strcpy(variable, "TASX");
      speed_data = getData(ncFile, variable, &step);
    }
  }
  // Set speed_cutoff and delta if variable is WOW
  if (strncmp(variable, "WOW", 3) == 0)
  {
    speed_cutoff = .5;
    delta = -1.0;
  }
  if (!nimbus_output)
    cout << "Using variable " << variable << "\n";

  if (time_data == 0 || speed_data == 0)
    return 1;

  // Get flight start time. = FileStartTime + first Time[Offset] value.
  NcVar time_var = ncFile->getVar("Time");
  time_t start_t = getStartTime(time_var) + (int)time_data[0];
  time_t start = 0, end = 0;	// What come up with.

  if (start_t <= 0)
  {
    cerr << "Invalid start time, fatal.\n";
    return 1;
  }

  // Locate Start of Flight
  long i;
  long j=0;
  long nValues = time_var.getDim(0).getSize();
  for (i = 0; i < nValues; ++i)
  {
    j += step;

    if (debug)
      cerr << i << " " << j << " " << speed_data[j] << "\n";

    if (((delta > 0.0 && speed_data[j] > speed_cutoff) || (delta < 0.0 && speed_data[j] < speed_cutoff)) && speed_data[j] != -32767.0)
    {
      start = start_t + i;

      if (debug)
        cout << "take-off indx = " << start << " " << j << endl;

      break;
    }
  }

  // Increment index to move us forward in time to make sure TAS stays
  // above threshold.
  i += 60;
  j += 60*step;

  // Locate End of Flight
  for (; i < nValues; ++i)
  {
    j += step;

    if (((delta > 0.0 && speed_data[j] < speed_cutoff) || (delta < 0.0 && speed_data[j] > speed_cutoff)) && speed_data[j] != -32767.0)
    {
      end = start_t + i;

      if (debug)
        cout << "landing indx = " << end << " " << i << endl;

      break;
    }
  }


  if (nimbus_output)
  {
    int shh, ehh, smm, emm, sss, ess; //keep track of seconds for no rounding
    struct tm * tt = gmtime(&start);
    shh = tt->tm_hour; smm = tt->tm_min; sss = tt->tm_sec;
    tt = gmtime(&end);
    ehh = tt->tm_hour; emm = tt->tm_min; ess = tt->tm_sec;
    if (!no_round_time)
     { 
      //round start time to nearest minute
      emm =emm+1;
      if (ehh < shh) ehh += 24;
      if (emm > 59) { emm -= 60; ehh += 1; }

      cout << "ti=" << setfill('0') << setw(2) << shh << ":";
      cout << setfill('0') << setw(2) << smm << ":00-";
      cout << setfill('0') << setw(2) << ehh << ":";
      cout << setfill('0') << setw(2) << emm << ":00\n";
    }
   else{
    if (ehh < shh) ehh += 24; // handle day wrap
    cout << "ti=" << setfill('0') << setw(2) << shh << ":";
    cout << setfill('0') << setw(2) << smm << ":";
    cout << setfill('0') << setw(2) << sss << "-";
    cout << setfill('0') << setw(2) << ehh << ":";
    cout << setfill('0') << setw(2) << emm << ":";
    cout << setfill('0') << setw(2) << ess << "\n";
   } 
  }
  else
  {
      cout << "Takeoff: " << ctime(&start);
      cout << "Landing: " << ctime(&end);
  }


  if (speed_data[0] > 80.0)
    cout	<< endl << " First TAS value is " << speed_data[0]
		<< "m/s, incomplete netCDF file?" << endl;

  if (speed_data[nValues * step-1] > 80.0)
    cout << endl << " Last TAS value is " << speed_data[nValues-1]
	<< "m/s, incomplete netCDF file?" << endl;

  delete time_data;
  delete speed_data;
  delete ncFile;
}

