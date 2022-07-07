
#include "gtest/gtest.h"


#include "NcCache.h"
#include "NcComparison.h"
#include "compare_lists.h"
#include "gsl.hh"

const bool PRINT_DEBUG = false;

#include <iostream>

using std::cerr;
using std::endl;

using boost::make_shared;
using boost::shared_ptr;

TEST(NcCache, ReadFirstTime)
{
  NcCache ncc("IDEAS-4rf02-expected.nc");

  // seconds since 2013-09-26 00:00:00 +0000
  // 67273
  nc_time xtime = nc_time(boost::gregorian::date(2013, 9, 26),
			  boost::posix_time::time_duration(0, 0, 67273));
  // nc_time xtime = nc_time_from_time_t(1380242473);
  EXPECT_EQ(xtime, ncc.times()[0]);
}

TEST(NcCache, GlobalKeys)
{
  // Make sure the global attributes are cached correctly.
  NcCache ncc("IDEAS-4rf02-expected.nc");
  NcCache::attribute_vector_t gatts = ncc.global_attributes;

  EXPECT_EQ(39, gatts.size());
  EXPECT_EQ("institution", gatts[0]->name);
  EXPECT_EQ("time_coverage_end", gatts[38]->name);
  EXPECT_EQ("TimeInterval", gatts[20]->name);
}


TEST(NcCache, Variables)
{
  NcCache ncc("IDEAS-4rf02-expected.nc");
  ASSERT_EQ(493, ncc.variables.size());
  EXPECT_EQ(ncc.getVariable("Time")->name, "Time");
  EXPECT_EQ(ncc.variables[0]->name, "Time");
  EXPECT_EQ(ncc.variables[1]->name, "A1DC_LWIO");
  EXPECT_EQ(ncc.variables[ncc.variables.size()-1]->name, "ZERO");
}

TEST(NcCache, Dimensions)
{
  NcCache ncc("IDEAS-4rf02-expected.nc");
  nc_dimension time = *ncc.getDimension("Time");
  EXPECT_EQ(time, time);
  EXPECT_TRUE(!(time == *ncc.getDimension("sps1")));
  EXPECT_EQ(time.len, 45);
  EXPECT_FALSE(time.empty());
  EXPECT_EQ(ncc.getDimension("sps1")->len, 1);
  EXPECT_EQ(ncc.getDimension("Vector98")->len, 98);
  EXPECT_EQ(ncc.getDimension("Vector512")->len, 512);
  EXPECT_FALSE(ncc.getDimension("no_such_dim"));
}


TEST(NcCache, coordinates)
{
  NcCache* ncf = 0;
  nc_dimension time(ncf, "time", 0, 100);
  nc_dimension height(ncf, "height", 1, 88);
  nc_dimension freq(ncf, "frequency", 2, 256);
  std::vector<nc_dimension*> dims;
  dims.push_back(&time);
  dims.push_back(&height);
  dims.push_back(&freq);
  coordinates coords(dims);
  EXPECT_EQ(coords.npoints, 100*88*256);
  EXPECT_EQ(coords.index, 0);
  EXPECT_EQ(coords.dims.size(), 3);
  EXPECT_EQ(coords.next(), true);
  EXPECT_EQ(coords.index, 1);
  coords_t ic;
  ic = coords.as_vector();
  EXPECT_EQ(ic.size(), 3);
  EXPECT_EQ(ic[0], 0);
  EXPECT_EQ(ic[1], 0);
  EXPECT_EQ(ic[2], 1);
  coords.index = 150;
  ic = coords.as_vector();
  EXPECT_EQ(ic[0], 0);
  EXPECT_EQ(ic[1], 0);
  EXPECT_EQ(ic[2], 150);
  coords.index = 256;
  ic = coords.as_vector();
  EXPECT_EQ(ic[0], 0);
  EXPECT_EQ(ic[1], 1);
  EXPECT_EQ(ic[2], 0);
  coords.index = 256*88;
  ic = coords.as_vector();
  EXPECT_EQ(ic[0], 1);
  EXPECT_EQ(ic[1], 0);
  EXPECT_EQ(ic[2], 0);
  coords.index = 256*88+513;
  ic = coords.as_vector();
  EXPECT_EQ(ic[0], 1);
  EXPECT_EQ(ic[1], 2);
  EXPECT_EQ(ic[2], 1);

  coords.set(1, 2, 3);
  EXPECT_EQ(256*88+515, coords.index);
}


TEST(NcCache, Attributes)
{
  NcCache ncc("IDEAS-4rf02-expected.nc");

  {
    nc_att<float> att(&ncc, "geospatial_lat_min", NC_GLOBAL);
    att.load_values();
    EXPECT_EQ(att.as_string(), "39.9126701");
    EXPECT_EQ(att.datatype, NC_FLOAT);
  }
  {
    nc_string_attribute att(&ncc, "ProjectName", NC_GLOBAL);
    att.load_values();
    EXPECT_EQ(att.as_string(), "IDEAS-4");
    EXPECT_EQ(att.datatype, NC_CHAR);
  }

  nc_variable* rtx = ncc.getVariable("RTX");
  EXPECT_EQ(rtx->attributes[0]->name, "_FillValue");
  EXPECT_EQ(rtx->attributes[6]->name, "Dependencies");
  EXPECT_EQ(rtx->attributes[6]->as_string(), "1 RTH1");
  nc_att<float>* range = dynamic_cast<nc_att<float>*>(rtx->attributes[3].get());
  ASSERT_TRUE(range);
  EXPECT_EQ(range->len, 2);
  ASSERT_FLOAT_EQ(range->values[0], 21.6585);
  ASSERT_FLOAT_EQ(range->values[1], 21.69501);
}


TEST(NcCache, GlobalAttributes)
{
  NcCache ncc("IDEAS-4rf02-expected.nc");

  EXPECT_EQ(ncc.global_attributes[0]->name, "institution");
  EXPECT_EQ(ncc.global_attributes[0]->as_string(),
	    "NCAR Research Aviation Facility");
  nc_attribute* att = ncc.getGlobalAttribute("geospatial_lat_min");
  ASSERT_TRUE(att);
  EXPECT_EQ(att->as_string(), "39.9126701");
}


TEST(NcCache, Compare)
{
  NcCache left("IDEAS-4rf02-expected.nc");
  NcCache right("IDEAS-4rf02-expected.nc");

  CompareNetcdf ncdiff(&left, &right);
  ncdiff.compare();
  EXPECT_EQ(ncdiff.countDifferences(), 0);

  right.overrideGlobalAttribute("ConventionsVersion", "99999");
  nc_attribute* att = right.getGlobalAttribute("ConventionsVersion");
  ASSERT_TRUE(att);
  EXPECT_EQ(att->as_string(), "99999");

  ncdiff.compare();
  EXPECT_EQ(ncdiff.countDifferences(), 1);

  std::vector<std::string> overrides;
  overrides.push_back("ConventionsVersion=99999");
  left.overrideGlobalAttributes(overrides);
  ncdiff.compare();
  EXPECT_EQ(ncdiff.countDifferences(), 0);
}


TEST(NcCache, variable_range)
{
  NcCache* ncf = 0;
  nc_dimension time(ncf, "time", 0, 100);
  nc_dimension height(ncf, "height", 1, 88);
  nc_dimension freq(ncf, "frequency", 2, 256);
  std::vector<nc_dimension*> dims;
  dims.push_back(&time);
  dims.push_back(&height);
  dims.push_back(&freq);
  coordinates start(dims);
  coordinates end(dims);
  start.set(0, 0, 0);
  end.set(99, 87, 255);
  variable_range range(start, end);
  EXPECT_EQ(start.npoints, range.size());

  start.set(98, 86, 254);
  range = variable_range(start, end);
  EXPECT_EQ(1*88*256 + 1*256 + 1 + 1, range.size());

  start.set(99, 87, 254);
  range = variable_range(start, end);
  EXPECT_EQ(2, range.size());

  start.set(0, 0, 0);
  end.set(2, 2, 2);
  range = variable_range(start, end);
  EXPECT_EQ(2*88*256 + 2*256 + 2 + 1, range.size());
}


TEST(Comparison, Dimensions)
{
  NcCache* ncf1 = 0;
  NcCache* ncf2 = 0;
  nc_dimension left(ncf1, "time", 0, 100);
  nc_dimension right(ncf2, "time", 1, 100);
  nc_dimension height1(ncf1, "height", 0, 99);
  nc_dimension height2(ncf2, "height", 1, 100);

  ReportStyle style(8);
  {
    CompareDimensions cdim(0, &left, &right);
    EXPECT_EQ(cdim.compare(), Comparison::Equal);
    std::ostringstream out;
    cdim.generateReport(out, style.derive(2));
    EXPECT_EQ(out.str(), "                time = 100 ;\n");
  }
  {
    CompareDimensions cdim(0, &height1, &height2);
    EXPECT_EQ(cdim.compare(), Comparison::Different);
    std::ostringstream out;
    cdim.generateReport(out, style.derive(1));
    EXPECT_EQ(out.str(),
	      " -      height = 99 ;\n"
	      " +      height = 100 ;\n");
  }
  {
    CompareDimensions cdim(0, &height1, 0);
    EXPECT_EQ(cdim.compare(), Comparison::Deleted);
    std::ostringstream out;
    cdim.generateReport(out, style.derive(1));
    EXPECT_EQ(out.str(), " -      height = 99 ;\n");
  }
  {
    CompareDimensions cdim(0, 0, &height2);
    EXPECT_EQ(cdim.compare(), Comparison::Added);
    std::ostringstream out;
    cdim.generateReport(out, style.derive(1));
    EXPECT_EQ(out.str(), " +      height = 100 ;\n");
  }
}


TEST(Comparison, DimensionList)
{
  NcCache* ncf1 = 0;
  NcCache* ncf2 = 0;
  NcCache::dimension_vector_t ldims;
  NcCache::dimension_vector_t rdims;

  ldims.push_back(make_shared<nc_dimension>(ncf1, "time", 0, 100));
  ldims.push_back(make_shared<nc_dimension>(ncf1, "height", 0, 99));

  rdims.push_back(make_shared<nc_dimension>(ncf2, "time", 1, 100));
  rdims.push_back(make_shared<nc_dimension>(ncf2, "height", 1, 100));

  std::vector< shared_ptr<Comparison> > comparisons;
  CompareNetcdf ncomp(0, 0);
  compare_lists(&ncomp, ldims, rdims, comparisons, never_ignore());
  EXPECT_EQ(2, comparisons.size());
}



TEST(Comparison, Variables)
{
  NcCache* ncf = 0;

  nc_var<float> pres(ncf, "pres", 0);
  nc_dimension timed(ncf, "time", 0, 1440);
  pres.addDimension(&timed);
  EXPECT_EQ("float pres(time) ;", pres.textSummary());
}


TEST(Comparison, Attributes)
{
  CompareNetcdf ncf(0, 0);
  ncf.setFloatComparator(compare_floating_point().useDelta());
  NcCache* ncc = 0;

  float sizes[] = { 0.0, 0.1, 0.2, 0.3, 0.4, 0.5 };
  std::vector<float> vsizes(sizes, sizes+6);

  // Create two attributes and make sure their values compare correctly.
  nc_att<float> cells(ncc, "cells", 0);
  nc_att<float> cells2(ncc, "cells", 0);
  cells.set_values(vsizes);
  cells2.set_values(vsizes);
  CompareAttributes catts(&ncf, &cells, &cells2);
  EXPECT_EQ(catts.compare(), Comparison::Equal);
  cells2.values[3] += 0.0000001;
  EXPECT_TRUE(cells2.values[3] != cells.values[3]);
  EXPECT_EQ(catts.compare(), Comparison::Equal);
  cells2.values[3] += 0.000001;
  EXPECT_TRUE(cells2.values[3] != cells.values[3]);
  EXPECT_EQ(catts.compare(), Comparison::Different);
  ncf.setFloatComparator(compare_floating_point().setDelta(0.1).useDelta());
  EXPECT_EQ(catts.compare(), Comparison::Equal);
  cells2.values[3] += 0.2;
  EXPECT_EQ(catts.compare(), Comparison::Different);
  cells2.set_values(vsizes);
  EXPECT_EQ(catts.compare(), Comparison::Equal);
  vsizes.erase(vsizes.begin());
  cells2.set_values(vsizes);
  EXPECT_EQ(catts.compare(), Comparison::Different);
}


TEST(CompareNetcdf, Ignores)
{
  CompareNetcdf ncdiff(0, 0);

  EXPECT_TRUE(ncdiff.isIgnored("date_created"));
  std::vector<std::string> ignores;
  ignores.push_back("something_else");
  ignores.push_back("Dir_*");
  ncdiff.ignore(ignores);
  EXPECT_FALSE(ncdiff.isIgnored("date_created"));
  EXPECT_TRUE(ncdiff.isIgnored("something_else"));
  EXPECT_TRUE(ncdiff.isIgnored("Dir_10m_s1"));
}


TEST(CompareNetcdf, Selects)
{
  CompareNetcdf ncdiff(0, 0);

  EXPECT_TRUE(ncdiff.isSelected("Dir_10m_s1"));
  std::vector<std::string> ignores;
  ignores.push_back("Dir_*");
  ncdiff.ignore(ignores);
  EXPECT_FALSE(ncdiff.isSelected("Dir_10m_s1"));
  EXPECT_TRUE(ncdiff.isSelected("T"));
  std::vector<std::string> selects;
  selects.push_back("RH");
  ncdiff.selectVariables(selects);
  EXPECT_FALSE(ncdiff.isSelected("T"));
}


TEST(CompareNetcdf, match_substring)
{
  EXPECT_TRUE(match_substring("date*", "date_created"));
  EXPECT_TRUE(match_substring("*date*", "date_created"));
  EXPECT_FALSE(match_substring("date", "date_created"));
  EXPECT_FALSE(match_substring("date", "created_date"));
  EXPECT_TRUE(match_substring("Dir_*", "Dir_1m_s1"));
  EXPECT_FALSE(match_substring("Dir_", "Dir_1m_s1"));
  EXPECT_FALSE(match_substring("", "date_created"));
  EXPECT_TRUE(match_substring("", ""));
  EXPECT_TRUE(match_substring("*", "Dir_1m_s1"));
  EXPECT_TRUE(match_substring("***", "created_date"));
}


TEST(compare_floating_point, compare)
{
  compare_floating_point cfp;
  cfp.useDelta();

  EXPECT_TRUE(cfp.near_equal(1.0f, 1.0f));
  EXPECT_TRUE(cfp.near_equal(1.0000001f, 1.0000002f));
  EXPECT_FALSE(cfp.near_equal(1.0000001f, 1.000002f));
  cfp.setDelta(1.0);
  EXPECT_TRUE(cfp.near_equal(1.1f, 1.4f));
  EXPECT_TRUE(cfp.near_equal(1.1d, 1.4d));
  EXPECT_FALSE(cfp.near_equal(1.1d, 5.0d));
}


int getbit(const double& d, int bit)
{
  return ((*(unsigned long*)(&d)) >> (bit)) & 1;
};


void printbits(const double& d)
{
  auto nbits = sizeof(d) * 8;
  auto b = nbits-1;
  do
  {
    cerr << getbit(d, b);
    if (b == nbits - 1 or b == nbits - 12)
      cerr << " ";
  } while (b-- != 0);
  cerr << endl;
}


double setbit(const double& d, int bit, int value)
{
  union {
    double d;
    long i;
  } ut;
  ut.d = d;
  auto& i = ut.i;
  i = (i & (~(1ul << bit))) | (value << bit);
  return ut.d;
};


TEST(compare_floating_point, ulps)
{
  compare_floating_point cfp;
  cfp.setULPS(2).useULPS();
  EXPECT_EQ(cfp.near_equal(1.0, 1.0), true);
  EXPECT_EQ(cfp.near_equal(1.0, -1.0), false);
  EXPECT_EQ(cfp.near_equal(-1.0, -1.0), true);
  EXPECT_EQ(cfp.near_equal(1.01, 1.02), false);
  EXPECT_EQ(cfp.near_equal(-1.01, -1.02), false);
  double x = 1234567890123456;
  EXPECT_TRUE(x != x + 1);
  cfp.setULPS(4);
  EXPECT_EQ(cfp.near_equal(x, x+1), true);
  EXPECT_EQ(cfp.near_equal(-x, -x-1), true);
  EXPECT_EQ(cfp.near_equal(x, x-1), true);
  EXPECT_EQ(cfp.near_equal(-x, -x+1), true);
  cfp.setULPS(2);
  EXPECT_EQ(cfp.near_equal(x, x+1), false);
  EXPECT_EQ(cfp.near_equal(-x, -x-1), false);
  float y = 12345678;
  EXPECT_TRUE(y != y + 1);
  cfp.setULPS(4);
  EXPECT_EQ(cfp.near_equal(y, y+2), true);
  EXPECT_EQ(cfp.near_equal(-y, -y-2), true);
  cfp.setULPS(1);
  EXPECT_EQ(cfp.near_equal(y, y+2), false);
  EXPECT_EQ(cfp.near_equal(-y, -y-2), false);

  // Test setting steps to zero to require exact equality.
  cfp.setULPS(0);
  EXPECT_EQ(cfp.near_equal(y, y), true);
  EXPECT_EQ(cfp.near_equal(y, nextafterf(y, y+1)), false);
  EXPECT_EQ(cfp.near_equal(y, y+1), false);
  EXPECT_EQ(cfp.near_equal(x, x), true);
  EXPECT_EQ(cfp.near_equal(x, x+1), false);
  EXPECT_EQ(cfp.near_equal(x, nextafter(x, x-1)), false);

  // Actually test that ULPs equates to number of bits.
  x = 2.0;
  if (PRINT_DEBUG)
  {
    cerr << std::setprecision(20);
    cerr << "bytes in double: " << sizeof(x)
        << "; bytes in long: " << sizeof(0ul) << endl;
    EXPECT_EQ(sizeof(x), sizeof(0ul));

    cerr << "bits of x=" << x << endl;
    printbits(x);
    x = setbit(x, 0, 1);
    cerr << "after setting bit 0, x = " << x << ", bits:" << endl;
    printbits(x);
  }

  x = 2.0;
  auto dnext = x;
  for (int i = 1; i <= 1 << 4; ++i)
  {
    dnext = nextafter(dnext, dnext+1000);
    if (PRINT_DEBUG)
    {
      cerr << "Step " << std::setw(2) << i
          << ": nextafter(x) => " << dnext << ", bits:" << endl;
      printbits(dnext);
    }
  }

  // dnext now contains a number that is 16 steps from x.  It is the same
  // value as x up until the 5th bit.  So if ULPs is less than 5, then an
  // equality test of the numbers should be false.

  cfp.setULPS(4);
  EXPECT_EQ(cfp.near_equal(x, dnext), false);
  cfp.setULPS(5);
  EXPECT_EQ(cfp.near_equal(x, dnext), true);
}


TEST(calling_gsl, empty)
{
  double value = 10;

  // Make sure it's ok to call gsl with 0 values.
  EXPECT_EQ(0, gsl::gsl_stats_mean(&value, 1, 0));
  EXPECT_EQ(10, gsl::gsl_stats_mean(&value, 1, 1));
}
