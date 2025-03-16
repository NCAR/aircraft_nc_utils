#include <cstdlib>
#include <cstring>

#include <netcdf>

using namespace std;
using namespace netCDF;

// Command line options.
bool verbose = false;
bool hours = false;		// Output hours instead of #dips.
float upper_alt = 8800.0;	// Default.
float lower_alt = 4500.0;	// Default.
char fileName[1024];

float *
getData(NcFile *file, const char * name)
{
  NcVar var = file->getVar(name);

  if (var.isNull())
  {
    cerr << "No variable " << name << "?" << endl;
    return 0;
  }

  float * data = new float[var.getDim(0).getSize()];
  var.getVar(data);

  if (data == 0)
  {
    cerr << "No data for variable " << name << "?" << endl;
    return 0;
  }

  return data;
}


void
usage()
{
  cerr << "Print out number of dips in a flight, take-off and landing will be a dip.\n";
  cerr << "Usage: nc_dips [-v] [-l lower_alt_limit] [-u upper_alt_limit] netcdf_file\n";
  exit(1);
}


void
processArgs(char **argv)
{
  fileName[0] = 0;

  while (*++argv)
  {
    if ((*argv)[0] == '-')
    {
      switch ((*argv)[1])
      {
        case 'v':
          verbose = true;
          break;

        case 'h':
          hours = true;
          break;

        case 'l':
          lower_alt = atof(*++argv);
          break;

        case 'u':
          upper_alt = atof(*++argv);
          break;
      }
    }
    else
      strcpy(fileName, *argv);
  }
}


int
main(int argc, char *argv[])
{
  if (argc < 2)
    usage();

  processArgs(argv);



  // Open NetCDF file
  NcFile *ncFile = new NcFile(fileName, NcFile::read);
  if (ncFile->isNull())
  {
    cerr << "Could not open NetCDF file '" << fileName << "' for reading.\n";
    return 1;
  }

  if (verbose)
  {
    std::string proj, fl;
    NcGroupAtt project = ncFile->getAtt("project");
    NcGroupAtt flight = ncFile->getAtt("FlightNumber");
    project.getValues(proj);
    flight.getValues(fl);
    cout << fileName << ":" << proj << ":" << fl << ":\n";
  }

  // Try GPS alt first, otherwise pressure alt.
  float *alt_data = getData(ncFile, "GGALT");
  if (alt_data == 0)
    alt_data = getData(ncFile, "PALT");

  if (alt_data == 0)
    return 1;

  // Get flight start time. = FileStartTime + first Time[Offset] value.
  NcVar time_var = ncFile->getVar("Time");

  // Locate Start of Flight
  long i, ndips = 0;
  bool high_alt = false;
  for (i = 0; i < time_var.getDim(0).getSize(); ++i)
  {
    float alt = alt_data[i];

    if (alt < 0)
      continue;

    if (high_alt == false && alt > upper_alt)
    {
      high_alt = true;
    }
    else
    if (high_alt == true && alt < lower_alt)
    {
      high_alt = false;
      ++ndips;
    }
  }


  if (hours)
  {
    if (verbose) cout << "Number of flight hours = ";
    cout << (float)time_var.getDim(0).getSize() / 3600 << endl;
  }
  else
  {
    if (verbose) cout << "Number of dips = ";
    cout << ndips << endl;
  }

  delete alt_data;
  delete ncFile;

  return 0;
}
