/*
-------------------------------------------------------------------------
OBJECT NAME:	ncvarlist.cc

FULL NAME:	netCDF Variable List

DESCRIPTION:	Output list of variables, names, units, and titles, from
		a netCDF file.

COPYRIGHT:	University Corporation for Atmospheric Research, 2011
-------------------------------------------------------------------------
*/

#include <cstdlib>
#include <cstring>
#include <iomanip>
#include <vector>

#include <netcdf>

using namespace std;
using namespace netCDF;

static bool csv = false;

void processArgs(char **argv);

/* -------------------------------------------------------------------- */
void
usage()
{
  cerr << "netCDF variable list.\n  Usage: ncvavrlist [-c] file.nc\n";
  cerr << "    -c: output comma separated values (CSV).\n";
  cerr << "    Read a netCDF file [file.nc] and output variable names, units, and titles.\n";
  exit(1);
}

int
main(int argc, char *argv[])
{
  if (argc < 2)
    usage();

  processArgs(argv);

  NcFile *inFile = new NcFile(argv[argc-1], NcFile::read);
  if (inFile->isNull())
  {
    cerr << "ncvarlist: Failed to open input file [" << argv[argc-1] << "], exiting.\n";
    return 1;
  }

  cout << argv[argc-1] << endl;

  // Output some basic info about the file.
  NcGroupAtt att;
  std::string s;
  att = inFile->getAtt("project");
  att.getValues(s);
  if (s.size() > 0) cout << s;
  att = inFile->getAtt("FlightNumber");
  att.getValues(s);
  if (s.size() > 0) cout << ", " << s;
  att = inFile->getAtt("FlightDate");
  att.getValues(s);
  if (s.size() > 0) cout << ", " << s;
  cout << endl;

  size_t longestName = 0, longestUnits = 0;

  // Go through var list and determine longest name and units for pretty print.
  if (!csv)
  {
    std::multimap<std::string, NcVar> varList = inFile->getVars();
    for (auto it = varList.begin(); it != varList.end(); ++it)
    {
      NcVar var = it->second;

      longestName = max(longestName, var.getName().size());
      NcVarAtt att = var.getAtt("units");
      if (!att.isNull())
      {
        std::string s;
        att.getValues(s);
        longestUnits = max(longestUnits, s.size());
      }
    }
  }


  // Output.
  std::multimap<std::string, NcVar> varList = inFile->getVars();
  for (auto it = varList.begin(); it != varList.end(); ++it)
  {
    NcVar var = it->second;
    NcVarAtt att;
    std::string units, long_name;

    att = var.getAtt("units");
    att.getValues(units);
    att = var.getAtt("long_name");
    att.getValues(long_name);

    if (csv)
    {
      cout << "\"" << var.getName() << "\",\"";
      if (units.size() > 0) cout << units;
      cout << "\",\"";
      if (long_name.size() > 0) cout << long_name;
      cout << "\"" << endl;
    }
    else
    {
      cout << left << setw (longestName+3) << var.getName();
      if (units.size() > 0) cout << left << setw (longestUnits+3) << units;
      if (long_name.size() > 0) cout << long_name;
      cout << endl;
    }
  }
}


void
processArgs(char **argv)
{
  while (*++argv)
    if ((*argv)[0] == '-')
      switch ((*argv)[1])
        {
        case 'h':
          usage();
          break;

        case 'c':
          csv = true;
          break;
        }
}
