/**
 * This program makes two small test netCDF files.  This uses the Unidata NetCDF4
 * C++ interface.
 *
 * See nVariables and nRecords for file dimensions.  The first file is all 1hz
 * data, the second has 5  variables at 5hz and 5 at 25hz.  Future developments
 * could/would include histogram variables.
 */

#include <cstdio>
#include <cstdlib>
#include <netcdf>
#include <ctime>

static const size_t nVariables = 10;
static const size_t nRecords = 60;

using namespace netCDF;

void createGlobalAttrs(NcFile *file, NcVar& time_v)
{
  /* Pick and choose as you see fit.  Please not the date and time ones near the
   * bottom of this function
   */
  file->putAtt("program", "NSF NCAR");
  file->putAtt("institution", "National Center for Atmospheric  Research");
  file->putAtt("source", "airborne observations");
  file->putAtt("platform", "N130AR");
  file->putAtt("platform_type", "aircraft");
  file->putAtt("project", "CEASAR");

  file->putAtt("creator_name", "NCAR EOL - Research Aviation Facility");
  file->putAtt("creator_url", "https://www.eol.ucar.edu/who-we-are/eol-organization/research-aviation-facility-raf");
  file->putAtt("creator_email", "somelist at ucar.edu");
  file->putAtt("creator_type", "group");
  file->putAtt("creator_group", "NSF NCAR C130 Team");

  file->putAtt("publisher_name", "UCAR NCAR - Earth Observing Laboratory");
  file->putAtt("publisher_url", "https://www.eol.ucar.edu/data-software/eol-field-data-archive");
  file->putAtt("publisher_email", "datahelp at ucar.edu");
  file->putAtt("publisher_type", "group");

  file->putAtt("conventions", "NCAR-RAF/nimbus-2.0,ACDD-1.3");
  file->putAtt("conventionsURL", "https://www.eol.ucar.edu/raf/Software/netCDF.html");

  file->putAtt("FlightNumber", "rf09");

  { // Date processed.
  time_t t = time(0);
  struct tm now;
  char now_s[64];

  memset(&now, 0, sizeof(struct tm));
  now = *localtime(&t);
  strftime(now_s, 64, "%FT%T %z", &now);

  file->putAtt("date_created", now_s);
  }

  // This should be accurate, as well as the untits for the time_v six lines lower
  file->putAtt("FlightDate", "03/05/2024");
  file->putAtt("time_coverage_start", "2024-03-05T06:02:00 +0000");
  file->putAtt("time_coverage_end", "2024-03-05T10:57:23 +0000");

  time_v.putAtt("long_name", "time of measurement");
  time_v.putAtt("standard_name", "time");
  time_v.putAtt("units", "seconds since 2024-03-05 16:00:00 +0000");
  time_v.putAtt("strptime_format", "seconds since %F %T %z");
}

void makeLRTfile()
{
  NcFile *file;
  file = new NcFile("lrt.nc", NcFile::replace);
  NcDim time_d;
  NcVar vars[10], time_v;
  float *varData[nVariables];

  if (file->isNull())
  {
    std::cerr << "Failed to create file lrt.nc" << std::endl;
    exit(1);
  }

  time_d = file->addDim("Time", nRecords);	// 1 minute of data.
  time_v = file->addVar("Time", NcType::nc_INT, time_d);
  createGlobalAttrs(file, time_v);

  for (size_t i = 0; i < nVariables; ++i)
  {
    char name[64];
    sprintf(name, "VAR%lu", i);
    vars[i] = file->addVar(name, NcType::nc_FLOAT, time_d);
    vars[i].putAtt("_FillValue", NcType::nc_FLOAT, (float)-32767.0);
    vars[i].putAtt("units", "test_units");
    sprintf(name, "Title for variable %lu", i);
    vars[i].putAtt("long_name", name);
    varData[i] = new float[nRecords];
  }

  int timeData[nRecords];

  for (size_t i = 0; i < nRecords; ++i)
  {
    timeData[i] = i;
    for (size_t j = 0; j < nVariables; ++j)
      varData[j][i] = 100 * j + i;
  }

  time_v.putVar(timeData);
  for (size_t i = 0; i < nVariables; ++i)
  {
    vars[i].putVar(varData[i]);
  }

  file->close();
}


void setData(float *varData, int i, int offset, int rate)
{
  for (size_t j = 0; j < rate; ++j)
    varData[(i*rate)+j] = (float)offset + i + ((float)j / rate);
}


void makeHRTfile()
{
  NcFile *file;
  file = new NcFile("hrt.nc", NcFile::replace);
  NcDim time_d, rate5_d, rate25_d;
  NcVar vars[10], time_v;
  float *varData[nVariables];

  // This routine creates 5 variables at 5hz and 5 at 25hz.
  int rates[] = { 5, 5, 5, 5, 5, 25, 25, 25, 25, 25 };

  if (file->isNull())
  {
    std::cerr << "Failed to create file\n";
    exit(1);
  }

  time_d = file->addDim("Time", nRecords);
  rate5_d = file->addDim("sps5", 5);
  rate25_d = file->addDim("sps25", 25);

  time_v = file->addVar("Time", NcType::nc_INT, time_d);
  createGlobalAttrs(file, time_v);

  for (size_t i = 0; i < nVariables; ++i)
  {
    char name[64];
    sprintf(name, "VAR%lu", i);

    std::vector<NcDim> dims;
    dims.push_back(time_d);

    if (rates[i] == 5)
    {
      dims.push_back(rate5_d);
      vars[i] = file->addVar(name, NcType::nc_FLOAT, dims);
    }
    if (rates[i] == 25)
    {
      dims.push_back(rate25_d);
      vars[i] = file->addVar(name, NcType::nc_FLOAT, dims);
    }

    vars[i].putAtt("_FillValue", NcType::nc_FLOAT, (float)-32767.0);
    vars[i].putAtt("units", "test_units");
    sprintf(name, "Title for variable %lu", i);
    vars[i].putAtt("long_name", name);
    varData[i] = new float[nRecords * rates[i]];
  }

  int timeData[nRecords];

  for (size_t i = 0; i < nRecords; ++i)
  {
    timeData[i] = i;

    for (size_t j = 0; j < nVariables; ++j)
      setData(varData[j], i, j * 100, rates[j]);
  }

  time_v.putVar(timeData);
  for (size_t i = 0; i < nVariables; ++i)
  {
    vars[i].putVar(varData[i]);
//    vars[i].putVar(varData[i], nRecords, rates[i]);
  }

  file->close();
}


int main(int argc, char *argv[])
{
  makeLRTfile();
  makeHRTfile();

  return 0;
}
