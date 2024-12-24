/*
-------------------------------------------------------------------------
OBJECT NAME:	nc_compare.cc

FULL NAME:	netCDF compare program

DESCRIPTION:	Compare two netCDF files and output the differnces.

COPYRIGHT:	University Corporation for Atmospheric Research, 2016
-------------------------------------------------------------------------
*/

#include "NcComparison.h"

#include <iostream>
#include <boost/program_options.hpp>

using std::cout;
using std::cerr;
namespace po = boost::program_options;

int
nc_compare(int argc, char *argv[])
{
  // Declare the supported options.
  po::options_description
    desc("nc_compare [options] primary_file secondary_file");
  desc.add_options()
    ("help", "Show this help message.")
    ("showequal", "Show equal objects as well as different.")
    ("showindex",
     "For vector values, report the indexes of the differences.")
    ("showtimes", "Report different time coordinates.")
    ("ignore", po::value<std::vector<std::string> >()->composing(),
     "Ignore attributes and variables with the given name.  "
     "Add * as suffix or prefix to match a substring.  "
     "Pass --ignore for each name to be ignored.")
    ("variable", po::value<std::vector<std::string> >()->composing(),
     "Select variables for comparison.  Add * as prefix or suffix "
     "or both match variables with the given substring.  "
     "All variables are selected by default.  "
     "If a variable matches one of the ignores, then it is ignored "
     "even if it matches one of the --variable strings.  "
     "Pass --variable for each substring to match.")
    ("override", po::value<std::vector<std::string> >()->composing(),
     "Override a global attribute in the left file specified in the form "
     "key=value.  "
     "Pass --override for each attribute to override.  Only "
     "global attribute names which exist in the left file will be "
     "overridden, all other overrides are ignored.")
    ("file", po::value<std::vector<std::string> >(), "Input files.")
    ("delta", po::value<double>(),
     "Error delta allowed for floating point values to be equal.  "
     "This is a floating point delta value, meaning "
     "the absolute difference between two numbers, no matter how large, must "
     "be less than the error delta.  To determine if floats of arbitrary "
     "range are close enough, use the ulps option.")
    ("ulps",
     po::value<int>()->default_value(compare_floating_point().getULPS()),
     "Number of Units in the Last Places (bits) "
     "in which floating point numbers can "
     "differ and still be considered equal.  This is the floating point "
     "comparison used if --delta or --ulps is not specified explicitly.  "
     "For example, ULPS=4 means two floats must be within 15 (2^4-1) steps "
     "of each other to compare as equal.  "
     "If ULPS is 0, then floats must be exactly equal.  "
     "The same ULPS setting is used for float and double types.")
    ("limit",
     po::value<int>()->default_value(ReportStyle::DEFAULT_REPORT_LIMIT),
     "Maximum number of differences to show in the report.  Once the limit "
     "is reached, no more differences are shown.")
    ("use-right-blanks",
     "Fill values in a variable on the right are used to filter "
     "out variable values on the left. In other words, values on the right "
     "which have been blanked out are also used to blank out the left, but "
     "only if the dimension sizes are the same.")
    ("minmax",
     "Report min and max in the statistics report.")
    ("nans-equal",
     "By default a NAN does not equal anything, including another NAN. "
     "Set nans-equal if a nan in both files should not be a difference. "
     "Two NANs are equal if their signs are equal. INFINITY values are "
     "always equal if their signs are equal, regardless of nans-equal. "
     "This setting also affects the means comparison in the statistics "
     "report.")
    ;

  po::positional_options_description p;
  p.add("file", 2);

  po::variables_map vm;
  po::store(po::command_line_parser(argc, argv).
	    options(desc).positional(p).run(), vm);
  po::notify(vm);

  if (vm.count("help")) {
    cout << desc << "\n";
    return 1;
  }

  std::vector<std::string> files;
  if (vm.count("file"))
    files = vm["file"].as<std::vector<std::string> >();
  if (files.size() != 2)
  {
    cerr << "Two input files must be specified.\n";
    exit(1);
  }

  ncopts = 0;
  putenv((char *)"TZ=UTC");	// All time calcs in UTC.

  NcCache left(files[0]);
  NcCache right(files[1]);

  std::vector<std::string> override;
  if (vm.count("override"))
  {
    override = vm["override"].as<std::vector<std::string> >();
    left.overrideGlobalAttributes(override);
  }

  CompareNetcdf ncdiff(&left, &right);
  ReportStyle& style = ncdiff.style();
  style.showEqual(vm.count("showequal") > 0);
  style.showIndex(vm.count("showindex") > 0);
  style.showTimes(vm.count("showtimes") > 0);
  style.useRightBlanks(vm.count("use-right-blanks") > 0);
  style.showMinMax(vm.count("minmax") > 0);

  std::vector<std::string> ignores;
  if (vm.count("ignore"))
    ignores = vm["ignore"].as<std::vector<std::string> >();
  if (ignores.size())
  {
    ncdiff.ignore(ignores);
  }
  std::vector<std::string> selects;
  if (vm.count("variable"))
    selects = vm["variable"].as<std::vector<std::string> >();
  if (selects.size())
  {
    ncdiff.selectVariables(selects);
  }
  if (vm.count("limit"))
  {
    int limit = vm["limit"].as<int>();
    style.setReportLimit(limit);
  }
  compare_floating_point cfp;
  if (vm.count("ulps"))
  {
    int ulps = vm["ulps"].as<int>();
    cfp.setULPS(ulps);
    cfp.useULPS();
  }
  if (vm.count("delta"))
  {
    double delta = vm["delta"].as<double>();
    cfp.setDoubleDelta(delta);
    cfp.setFloatDelta(delta);
    cfp.useDelta();
  }
  cfp.setNansEqual(vm.count("nans-equal") > 0);
  ncdiff.setFloatComparator(cfp);
  ncdiff.compare();
  ncdiff.report(cout);
  int ndiffs = ncdiff.countDifferences();
  if (ndiffs)
  {
    std::cout << ndiffs << " differences.\n";
  }
  return ndiffs;
}


int
main(int argc, char *argv[])
{
  try {
    return nc_compare(argc, argv);
  }
  catch (const std::runtime_error& error)
  {
    // Typically IO errors.
    cerr << "Error: " << error.what() << std::endl;
    exit(1);
  }
  catch (const boost::program_options::error& error)
  {
    // Error parsing command-line options.
    cerr << error.what() << std::endl;
    cerr << "Use option --help to see usage info." << std::endl;
    exit(1);
  }
}
    
