#include <cstdlib>
#include <ctime>
#include <cstring>

#include <netcdfcpp.h>

using namespace std;


NcValues *
getData(NcFile * file, const char * name, long int * step)
{
  NcDim * dim;
  NcVar * var = file->get_var(name);
  *step =1;
  
  if (var == 0)		// Variable does not exist.
    return 0;

  // Figure out how many dimensions variable has
  int ndims=var->num_dims();
  if (ndims > 1)
  {
    for (int i=1; i < ndims; ++i)
    {
      dim = var->get_dim(i);
      *step *= dim->size();
    }
  }

  if (var == 0 || var->is_valid() == false)
  {
    cerr << "No variable " << name << "?" << endl;
    return 0;
  }

  NcValues * data = var->values();

  if (data == 0)
  {
    cerr << "No data for variable " << name << "?" << endl;
    return 0;
  }

  return data;
}


time_t
getStartTime(NcVar * time_var)
{
  NcAtt * unit_att = time_var->get_att("units");
  NcAtt * frmt_att = time_var->get_att("strptime_format");

  if (unit_att == 0 || unit_att->is_valid() == false)
  {
    cerr << "Units not present for time variable.\n";
    return 0;
  }

  char format[1000];
  if (frmt_att == 0 || frmt_att->is_valid() == false)
    strcpy(format, "seconds since %F %T %z");
  else
    strcpy(format, frmt_att->as_string(0));

  struct tm StartFlight;
  strptime(unit_att->as_string(0), format, &StartFlight);

  time_t start_t = mktime(&StartFlight);
  if (start_t <= 0)
    cerr << "Problem decoding units from Time variable, _start = " << start_t << endl;

  return start_t;
}


int
main(int argc, char *argv[])
{
  int indx = 1;
  float speed_cutoff = 25.0;	// Default.
  char variable[32] = "GSPD";
  float delta = 1.0;
  long int step;


  // Check arguments / usage.
  if (argc < 2)
  {
    cerr << "Print out take-off and landing times from a netCDF file.\nUses ground speed (use -v to change) above 25 m/s (use -t to change).\n\n";
    cerr << "Usage: flt_time [-t value] [-v variable] netcdf_file\n";
    cerr << "Currently takes -t or -v, but not both\n";
    exit(1);
  }

  if (strcmp(argv[indx], "-t") == 0)
  {
    ++indx;
    speed_cutoff = atof(argv[indx++]);
  } 
  else if (strcmp(argv[indx], "-v") == 0)
  {
    ++indx;
    strcpy(variable,argv[indx++]);
    if (strncmp(variable,"WOW",3) == 0)
    {
    speed_cutoff = .5;
    delta = -1.0; // For Takeoff apply speed_cutoff when passes value decreasing
    }
  }

  // keep program from exiting, if netCDF API doesn't find something.
  NcError * ncErr = new NcError(NcError::silent_nonfatal);

  putenv((char *)"TZ=UTC");     // Force all time routines to work in UTC.

  // Open NetCDF file
  NcFile * ncFile = new NcFile(argv[indx], NcFile::ReadOnly);
  if (ncFile->is_valid() == false)
  {
    cerr << "Could not open NetCDF file '" << argv[indx] << "' for reading.\n";
    return 1;
  }
  
  NcAtt * project = ncFile->get_att("project");
  if (project == 0 || project->is_valid() == false)
  {
    // If :project not present, look for :ProjectName
    project = ncFile->get_att("ProjectName");
    if (project == 0 || project->is_valid() == false)
    {
      cerr << "Neither global variable :project nor :ProjectName present in file.\n";
      return 0;
    }
  }

  NcAtt * flight = ncFile->get_att("FlightNumber");
  if (flight == 0 || flight->is_valid() == false)
  {
    cerr << "Global variable :FlightNumber not present in file.\n";
    return 0;
  }

  cout	<< argv[indx] << ":"
		<< project->as_string(0) << ":"
		<< flight->as_string(0) << ":\n";

  NcValues * time_data = getData(ncFile, "Time", &step);
  if (time_data == 0)
  {
    cerr << "Variable Time not present in file.\n";
    return 0;
  }

  // If user specified variable, use that.
  // Try ground speed first, otherwise airspeed.
  NcValues * speed_data = getData(ncFile, variable, &step);
  if (speed_data == 0)
    strncpy(variable,"TASX",5);
    speed_data = getData(ncFile, variable, &step);

  cout << "Using variable " << variable << "\n";

  if (time_data == 0 || speed_data == 0)
    return 1;

  // Get flight start time. = FileStartTime + first Time[Offset] value.
  NcVar * time_var = ncFile->get_var("Time");
  time_t start_t = getStartTime(time_var) + time_data->as_int(0);

  if (start_t <= 0)
  {
    cerr << "Invalid start time, fatal.\n";
    return 1;
  }

  // Locate Start of Flight
  long i;
  long j=0;
  for (i = 0; i < time_var->num_vals(); ++i)
  {
    j+=step;
//    cerr << i << " " << j << " " << speed_data->as_float(j) << "\n";
    if (((delta > 0.0 && speed_data->as_float(j) > speed_cutoff) || (delta < 0.0 && speed_data->as_float(j) < speed_cutoff)) && speed_data->as_float(j) != -32767.0)
    {
      time_t x = start_t + i;

      cout << "Takeoff: " << ctime(&x);
//cout << "take-off indx = " << ctime << " " << x << " " << j << endl;
      break;
    }
  }

  // Increment index to move us forward in time to make sure TAS stays
  // above threshold.
  i += 60;
  j+= 60*step;

  // Locate End of Flight
  for (; i < time_var->num_vals(); ++i)
  {
    j+=step;
    if (((delta > 0.0 && speed_data->as_float(j) < speed_cutoff) || (delta < 0.0 && speed_data->as_float(j) > speed_cutoff)) && speed_data->as_float(j) != -32767.0)
    {
      time_t x = start_t + i;

      cout << "Landing: " << ctime(&x);
//cout << "landing indx = " << x << " " << i << endl;
      break;
    }
  }

  if (speed_data->as_float(0) > 80.0)
    cout	<< endl << " First TAS value is " << speed_data->as_float(0)
		<< "m/s, incomplete netCDF file?" << endl;

  if (speed_data->as_float(time_var->num_vals()*step-1) > 80.0)
    cout << endl << " Last TAS value is " << speed_data->as_float(time_var->num_vals()-1)
	<< "m/s, incomplete netCDF file?" << endl;

  delete time_data;
  delete speed_data;
  delete ncFile;
}

