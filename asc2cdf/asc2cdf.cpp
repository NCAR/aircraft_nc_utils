/*
-------------------------------------------------------------------------
OBJECT NAME:	asc2cdf.c

FULL NAME:	ASCII to Nimbus-netCDF Low Rate

ENTRY POINTS:	main()

STATIC FNS:	ProcessArgv()
		WriteMissingData()

DESCRIPTION:	Translate ASCII file to Nimbus Low Rate netCDF file

COPYRIGHT:	University Corporation for Atmospheric Research, 1996-2007
-------------------------------------------------------------------------
*/

#include "define.h"

#include <sys/types.h>
#include <sys/stat.h>
#include <iostream>

char	buffer[BUFFSIZE];
char    histo_vars[MAX_VARS][256] = {"\0"};
char    var[256]  = {"\0"};
char    vars_columns[MAX_VARS][256] = {"\0"};
char    *refptr;

int	ncid;
int	status, nComments;
int	baseTimeID, timeOffsetID, timeVarID, varid[MAX_VARS], nVariables, nvars;
time_t	BaseTime = 0;
float	scale[MAX_VARS], offset[MAX_VARS], missingVals[MAX_VARS];
bool	getRec = true;
bool	notLastRec = true;

int	hour, minute, second, firstSecond, prevSecond = -1;
double	currSecond;
int	subsec;
int	startHour, startMinute, startSecond;
float	dataValue,lastDataValue;
int     lastVar;

char FlightDate[50];

static FILE	*inFP;
static size_t	nRecords;
static char	*globalAttrFile = 0;

/* Command line option flags.
 */
InputFileType	fileType = PLAIN_FILE;
bool	secondsSinceMidnight = false, Colonless = false;
bool    RAFconventions = true;
bool    verbose = false, histogram = false;
int	SkipNlines = 1;

int		BaseDataRate = 1, dataRate = 1;
const int	rateOne = 1;

const char	*noTitle = "No Title";
const char	*noUnits = "Unk";

void addGlobalAttrs(const char *p);
//void WriteBaseTime(); // Base time is depricated.
void handle_error(const int), Usage();

static int ProcessArgv(int argc, char **argv);
static size_t ProcessTime(char *p);
//static void WriteMissingData(int, int);


/* -------------------------------------------------------------------- */
int main(int argc, char *argv[])
{
  int	i, j, k, hz;
  int	count;
  char	*p;
  size_t index[3];
  size_t rec,ncol;

  putenv((char *)"TZ=UTC");	// All time calcs in UTC.
  FlightDate[0] = 0;

  i = ProcessArgv(argc, argv);

  if ((argc - i) < 2)
    Usage();

  if ((inFP = fopen(argv[i], "r")) == NULL)
  {
    fprintf(stderr, "Can't open input file %s.\n", argv[i]);
    exit(1);
  }


  if (nc_create(argv[i+1], NC_CLOBBER, &ncid) != NC_NOERR)
  {
    fprintf(stderr, "Can't destroy/create output file %s.\n", argv[i+1]);
    exit(1);
  }


  switch (fileType)
    {
    case PLAIN_FILE:
      CreatePlainNetCDF(inFP);
      SetPlainBaseTime();
      break;

    case NASA_AMES:
      CreateNASAamesNetCDF(inFP);
      break;

    case ICARTT:
      CreateICARTTnetCDF(inFP);
      break;

    case NASA_LANGLEY:
      CreateNASAlangNetCDF(inFP);
      break;

    case BADC_CSV:
      CreateBADCnetCDF(inFP);
      if (verbose) {
          for (i=0;i< nVariables; ++i)
	      printf("vars_columns[%d] = %s\n",i,vars_columns[i]);
          for (j=0;j< nvars; ++j)
	      printf("histo_vars[%d] = %s\n",j,histo_vars[j]);
      }
      break;
    }

  addGlobalAttrs(globalAttrFile);
  status = nc_enddef(ncid);
  if (status != NC_NOERR) handle_error(status);

  //WriteBaseTime();

  printf("Averaging Period = %d, Data Rate = %dHz\n", BaseDataRate, dataRate);


  /* Start uploading data.
   */
  rewind(inFP);

  while (SkipNlines--)
    fgets(buffer, BUFFSIZE, inFP);


  for (nRecords = 0; notLastRec; )
  {
    if (getRec)
    {
      if (fgets(buffer, BUFFSIZE, inFP) == NULL)
      {
        notLastRec = false;
	break;
      }
      if (strlen(buffer) < 3)
        continue;

      p = strtok(buffer, ", \t");	// Parse the first value (Time) out of the buffer

    }
    else
    {
	getRec=true;
    }


    if (fileType == NASA_LANGLEY)	/* Skip Julian day column */
      p = strtok(NULL, ", \t");

    if (fileType == BADC_CSV)   {       /* "end date" means no more data */
      if (strncmp(p,"end",3) == 0) {
	// Break out of hz loop
	notLastRec = false;
	continue;
      }
    }

    rec = ProcessTime(p);
    // Ignore duplicate timestamp
    if (int(rec) == -1) continue;


//    dataValue = (float)(nRecords * BaseDataRate);
//    nc_put_var1_float(ncid, timeVarID, &nRecords, &dataValue);
//    nc_put_var1_float(ncid, timeOffsetID, &nRecords, &dataValue);

    //If subseconds are given in the time column, offset here.-JAG
    if (verbose)
	printf("subsec: %d ; dataRate: %d\n",subsec,dataRate);
    for (hz = subsec; hz < dataRate; ++hz)
    {
      // If histogram data, zeroth data bin must be zero for legacy
      // reasons.
      if (histogram) {
	dataValue = 0;
        index[0] = rec; index[1] = hz; index[2] = 0;
        status = nc_put_var1_float(ncid, varid[1], index, &dataValue);
        if (status != NC_NOERR) handle_error(status);
    }
      j=0; // index for netCDF variables
      // k values only apply to histograms stored as repeating column headers
      k=1; // index for histogram columns; First var is written to index 0 of histogram by C: loop, so start at 1
#ifdef ZEROBIN
      k++; // With the legacy zero bin, everything is shifted to the right by one.
#endif
      lastVar = 0;
      for (i = 0; i < nVariables; ++i)
      {
        if ((p = strtok(NULL, ", \t\n\r")) == NULL)
          fprintf(stderr, "Not enough data points in row # %zu, check your formating;\n   are there spaces in a variable name on the title line?\n", nRecords);

        if (p)
          dataValue = atof(p);
        else
          dataValue = MISSING_VALUE;

	// Increment netCDF variable pointer if working with a new var
        if (fileType == BADC_CSV) {
	  strcpy(var,histo_vars[j]);
	  if (strstr(histo_vars[j],":") != NULL) {
	      strtok_r(var,":",&refptr);
	  }
	  if (strcmp(vars_columns[i],var) != 0) {
	    j++;
	  }
	  strcpy(var,histo_vars[j]);
	  if (strstr(histo_vars[j],":") != NULL) {
	      strtok_r(var,":",&refptr);
	  }
	} else { // For non-BADC, every var is a new var
	    j=i;
	}


        if (fileType != PLAIN_FILE)
        {
          if (dataValue == missingVals[i])
            dataValue = MISSING_VALUE;
          else
            dataValue = dataValue * scale[i] + offset[i];
        }

        if (histogram)
	{
          index[0] = rec; index[1] = hz; index[2] = i+1;
	  if (verbose)
	      printf("A: Writing data point %f to variable %d:%d index[%lu,%d,%d] \n",dataValue,varid[1],i,rec,hz,i+1);
          status = nc_put_var1_float(ncid, varid[1], index, &dataValue);
          if (status != NC_NOERR) handle_error(status);
        }
	else if (lastVar ==varid[j]) // repeating var, assume histogram
	{
          index[0] = rec; index[1] = hz; index[2] = k;
	  if (verbose)
	    printf("B: Writing data point %f to variable %d:%d index[%lu,%d,%d] \n",dataValue,varid[j],j,rec,hz,k);
	  // Use variable/column mapping to figure out which variable to put this value in.
          status = nc_put_var1_float(ncid, varid[j], index, &dataValue);
          if (status != NC_NOERR) handle_error(status);

#ifdef ZEROBIN
	  // If k=2, this is the first time through, and we already wrote the first value to the legacy zero bin.
	  // Move it to the first bin.
	  if (k == 2) {
	      if (verbose)
		  printf("B: Move data out of legacy zero bin\n");
              index[0] = rec; index[1] = hz; index[2] = 1;
              status = nc_put_var1_float(ncid, varid[j],index,&lastDataValue);
              if (status != NC_NOERR) handle_error(status);

              index[0] = rec; index[1] = hz; index[2] = 0;
	      lastDataValue = MISSING_VALUE;
              status = nc_put_var1_float(ncid, varid[j],index,&lastDataValue);
              if (status != NC_NOERR) handle_error(status);
	  }
#endif

	  // The number of columns in this histogram is already in the netCDF header as the third
	  // dimension of this variable.
	  nc_inq_dimlen(ncid, 2,&ncol);
	  count = int(ncol);
#ifdef ZEROBIN
	  count = count-1; // Have count bins, but only count-1 data point because first bin is legacy placeholder.
#endif
	  if (k >= count) k=1;
#ifdef ZEROBIN
	  k++;
#endif
        }
        else
        {
          index[0] = rec; index[1] = hz; index[2] = 0;
	  if (verbose)
	    printf("C: Writing data point %f to variable %d:%d index[%lu,%d,0] \n",dataValue,varid[j],j,rec,hz);
          status = nc_put_var1_float(ncid, varid[j], index, &dataValue);
          if (status != NC_NOERR) handle_error(status);
        }
	lastVar = varid[j];
#ifdef ZEROBIN
	lastDataValue = dataValue;
#endif

      }

      // If haven't read all the sub-dataRate data, keep looping until reach
      // next time interval. Compare on current time to avoid merging data
      // from different seconds into a single second record. This additional
      // fgets will cause us to loose a record when time passes a multiple
      // of data rate. Set a flag so we don't repeat fgets at top of loop.
      if (hz != dataRate-1) {
	getRec = false;
        if (fgets(buffer, BUFFSIZE, inFP) == NULL)
        {
          notLastRec = false;
	  break;
        }
        // I am not sure why this test is here. I can imagine good data in seconds since midnight with 1
        // column of time and one of data, so "1,23". It would be rare, but is it bad data?? Is this there
        // to catch something else??
        if (strlen(buffer) < 5)
          continue;
        p = strtok(buffer, ", \t");
        if (fileType == BADC_CSV)	{	/* "end date" means no more data */
          if (strncmp(p,"end",3) == 0) {
	    // Break out of hz loop
	    notLastRec = false;
	    break;
	  }
        }

	if (atoi(p) != int(currSecond)) // found a new second, so break out of hz loop
	  break;

        // look for data gaps and handle appropriately
        subsec = int(atof(p)*dataRate-currSecond*dataRate);
        if (subsec != hz+1) { // found a sub-second data gap for data with rates > 1sps
	  hz= subsec-1;
        }

      } else {
	getRec = true;
      }

      if (fileType == NASA_LANGLEY)     /* Skip Julian day      */
        p = strtok(NULL, ", \t");

      } // End hz loop

    ++nRecords;
  }

  fclose(inFP);

  // If FlightDate was specified, we need to re-write the base_time & Time::units
  // since we didn't know the start time of the first data record, just the date
  // of the flight.
  //WriteBaseTime();

  nc_redef(ncid);
  SetPlainBaseTime();

  sprintf(buffer, "%02d:%02d:%02d-%02d:%02d:%02d",
          startHour, startMinute, startSecond, hour, minute, second);

  status = nc_put_att_text(ncid, NC_GLOBAL, "TimeInterval", strlen(buffer)+1, buffer);
  if (status != NC_NOERR) handle_error(status);
  printf("Time interval completed = %s\n", buffer);
  status = nc_enddef(ncid);
  if (status != NC_NOERR) handle_error(status);
  nc_close(ncid);

  return(0);

}	/* END MAIN */

/* -------------------------------------------------------------------- */
//static void WriteMissingData(int currSecond, int lastSecond)
//{
//  float	dataValue;
//
//  for (int i = lastSecond; i < currSecond; i += BaseDataRate, ++nRecords)
//  {
//    dataValue = (float)(nRecords * BaseDataRate);
//    status = nc_put_var1_float(ncid, timeOffsetID, &nRecords, &dataValue);
//    if (status != NC_NOERR) handle_error(status);
//
//    dataValue = MISSING_VALUE;
//
//    for (int j = 0; j < nVariables; ++j)
//      status = nc_put_var1_float(ncid, varid[j], &nRecords, &dataValue);
//      if (status != NC_NOERR) handle_error(status);
//  }
//}	/* END WRITEMISSINGDATA */
//
/* -------------------------------------------------------------------- */
static int ProcessArgv(int argc, char **argv)
{
  int	i;

  for (i = 1; i < argc; ++i)
  {
    if (argv[i][0] != '-')
      break;

    switch (argv[i][1])
    {
      case 'b':
        if (strlen(FlightDate) > 0)
          fprintf(stderr, "-d option trumps -b option, BaseTime ignored.\n");
        else
          BaseTime = atoi(argv[++i]);
        break;

      case 'd':
        {
        struct tm tm;
        strptime(argv[++i], "%F", &tm);
        tm.tm_hour = tm.tm_min = tm.tm_sec = 0;
        BaseTime = mktime(&tm);
        sprintf(FlightDate, "%02d/%02d/%4d", tm.tm_mon+1, tm.tm_mday, tm.tm_year+1900);
        }
        break;

      case 'm':
        secondsSinceMidnight = true;
        break;

      case 'a':
        fileType = NASA_AMES;
        secondsSinceMidnight = true;
        break;

      case 'h':
	histogram = true;
	break;

      case 'c':
	fileType = BADC_CSV;
	secondsSinceMidnight = true;
	break;

      case 'i':
        fileType = ICARTT;
        secondsSinceMidnight = true;
        break;

      case 'l':
        fileType = NASA_LANGLEY;
        secondsSinceMidnight = true;
        break;

      case 'g':
        globalAttrFile = argv[++i];
        break;

      case 'r':
        {
        float rate = atof(argv[++i]);
        if (rate < 1.0)
          BaseDataRate = (int)(1.0 / rate + 0.5);
        if (rate > 1.0)
          dataRate = (int)rate;
        }
        break;

      case 's':
        SkipNlines = atoi(argv[++i]);
        break;

      case 'n':
        RAFconventions = false;
        break;

      case 'v':
        verbose = true;
        break;

      case ':':
        Colonless = true;
        break;

      default:
        fprintf(stderr, "Invalid option %s, ignoring.\n", argv[i]);
    }
  }

  return(i);

}	/* END PROCESSARGV */
/* -------------------------------------------------------------------- */
size_t ProcessTime(char *p)
{
    if (secondsSinceMidnight)
      {
      /* Save the seconds with any possible subsecond component */
      currSecond = atof(p);

      hour = int(currSecond) / 3600; currSecond -= hour * 3600;
      minute = int(currSecond) / 60; currSecond -= minute * 60;
      second = int(currSecond);

      if (nRecords == 0 && fileType != PLAIN_FILE)
        SetNASABaseTime(hour, minute, second);
      }
    else
      {
      if (Colonless)
        {
	/* Save the seconds with any possible subsecond component */
	currSecond = atof(&p[4]);
        second = atoi(&p[4]); p[4] = '\0';
        minute = atoi(&p[2]); p[2] = '\0';
        hour = atoi(p);
        }
      else
        {
        sscanf(p, "%d:%d:%lf", &hour, &minute, &currSecond);
        second = int(currSecond);
        }
      }

    if (dataRate > 1)
      {
      /* parse out the subseond component */
      currSecond -= second; subsec = int(currSecond*dataRate);
      }
    else
      {
      subsec = 0;
      }

    if (hour > 23)
      hour -= 24;

    currSecond = hour * 3600 + minute * 60 + second;


    if (prevSecond == -1) // 1st time through loop.
    {
      firstSecond = int(currSecond);
    }

    // Watch for midnight wrap around.
    if (currSecond < firstSecond)
      currSecond += 86400;

    if (nRecords == 0)
      {
      startHour = hour;
      startMinute = minute;
      startSecond = second;
      }
    else
    if (currSecond == prevSecond  && dataRate <= 1)
      {
      printf("Duplicate time stamp, ignoring, utsecs = %ld\n", (long int)currSecond);
      prevSecond = int(currSecond);
      return(-1);
      }
    else
    if (currSecond > prevSecond + BaseDataRate)
      {
      if (currSecond - prevSecond > 2)
        printf("last time = %d, new time = %d\n", prevSecond, int(currSecond));
//      WriteMissingData(currSecond, prevSecond);
      }

    prevSecond = int(currSecond);
    dataValue = currSecond;
    size_t rec = int(dataValue) - firstSecond;
    status = nc_put_var1_float(ncid, timeVarID, &rec, &dataValue);
    if (status != NC_NOERR) handle_error(status);
    status = nc_put_var1_float(ncid, timeOffsetID, &rec, &dataValue);
    if (status != NC_NOERR) handle_error(status);

    return(rec);
}	/* END PROCESSTIME */

void Usage()
{
  printf("Usage: asc2cdf [options] ascii_file_name output.nc\n\nStandard options:\n");
  printf("  -b time_t\tSet basetime.  Mostly deprecated, applied to original RAF files in the 1990's\n");
  printf("  -d YYYY-MM-DD\tSet date, useful for plain ascii files.\n");
  printf("  -g file\tAdd contents of file as global attributes, file should be in key=value format\n");
  printf("  -a\tIncoming format is NASA Ames\n");
  printf("  -l\tIncoming format is NASA Langely\n");
  printf("  -c\tIncoming format is BADC CSV (Ames offshoot)\n");
  printf("  -i\tIncoming format is ICARTT (this has mostly superceeded Ames and Langely)\n");
  printf("  -m\tIncoming time column is seconds since midnight (Above formats engage this)\n");
  printf("  -h\tIncoming file is a histogram\n");
  printf("  -n\tDo not produce RAF/nimbus netCDF conventions\n");

  printf("  -r n\tIncoming sample rate, for rates faster than 1 per second\n");
  printf("  -s n\tSkip n lines from the file before decoding data (skip header)\n");
  printf("  -v\tVerbose\n");
  printf("  -:\tIncoming time column is HHMMSS, no colons.\n");
  exit(1);
}
/* END ASC2CDF.C */
