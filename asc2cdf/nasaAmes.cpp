/*
-------------------------------------------------------------------------
OBJECT NAME:	nasaAmes.c

FULL NAME:	NASA Ames ASCII to Nimbus-netCDF Low Rate

ENTRY POINTS:	SetNASABaseTime()
		CreateNASAamesNetCDF()

STATIC FNS:	none

DESCRIPTION:	Translate NASA ASCII file to Nimbus Low Rate netCDF file

COPYRIGHT:	University Corporation for Atmospheric Research, 1996-07
-------------------------------------------------------------------------
*/

#include "define.h"

struct tm	StartFlight;

void *GetMemory(size_t nbytes);

/* -------------------------------------------------------------------- */
void SetNASABaseTime(int hour, int min, int sec)
{
  struct tm	*gt;
  char buff[512];

  StartFlight.tm_hour	= 0;
  StartFlight.tm_min	= 0;
  StartFlight.tm_sec	= 0;
  StartFlight.tm_isdst	= -1;

  BaseTime = mktime(&StartFlight);
  gt = gmtime(&BaseTime);
  StartFlight.tm_hour += StartFlight.tm_hour - gt->tm_hour;

  BaseTime = mktime(&StartFlight);

  strftime(buff, 128, "seconds since %F %T %z", &StartFlight);

  status = nc_put_att_text(ncid, timeVarID, "units", strlen(buff)+1, buff);
  if (status != NC_NOERR) handle_error(status);
  status = nc_put_att_text(ncid, timeOffsetID, "units", strlen(buff)+1, buff);
  if (status != NC_NOERR) handle_error(status);

}	/* END SETNASABASETIME */

/* -------------------------------------------------------------------- */
void CreateNASAamesNetCDF(FILE *fp)
{
  int	i, start;
  int	FFI, year, month, day;
  int	ndims, dims[3], TimeDim, RateDim, VectorDim;
  char	*p, *p1, *p2, *titles[MAX_VARS], *units[MAX_VARS], tmp[32];
  char *varUnits;
  //char  *varName;
  float missing_val = MISSING_VALUE;
  float cellSizes[512];
  int   nCells;


  /* Dimensions.
   */
  status = nc_def_dim(ncid, "Time", NC_UNLIMITED, &TimeDim);
  if (status != NC_NOERR) handle_error(status);

  sprintf(buffer, "sps%d", dataRate);
  status = nc_def_dim(ncid, buffer, dataRate, &RateDim);
  if (status != NC_NOERR) handle_error(status);


  /* Global Attributes.
   */
  strcpy(buffer, "NCAR-RAF/nimbus");
  status = nc_put_att_text(ncid, NC_GLOBAL, "Conventions", strlen(buffer)+1, buffer);
  if (status != NC_NOERR) handle_error(status);

  {
  time_t	t;
  struct tm	tm;

  memset(&tm, 0, sizeof(struct tm));
  tm.tm_isdst = -1;
  t = time(0);
  tm = *gmtime(&t);
  strftime(buffer, 128, "%h %d %R GMT %Y", &tm);
  status = nc_put_att_text(ncid, NC_GLOBAL, "DateConvertedFromASCII", 
                  strlen(buffer)+1, buffer);
  if (status != NC_NOERR) handle_error(status);
  }


  /* Get length of header and format type (FFI) */
  fgets(buffer, BUFFSIZE, fp);
  sscanf(buffer, "%d %d", &SkipNlines, &FFI);
  printf("SkipNlines: %d  FFI:%d\n", SkipNlines, FFI);

  if (FFI < 1000 || FFI > 1999)
  {
    fprintf(stderr, "Can't handle more than one independent variable.\n");
    exit(1);
  }

  /* Get PI */
  fgets(buffer, BUFFSIZE, fp);
  buffer[strlen(buffer)-1] = '\0';
  status = nc_put_att_text(ncid, NC_GLOBAL, "PI", strlen(buffer)+1, buffer);
  if (status != NC_NOERR) handle_error(status);
  printf("PI: %s\n", buffer);

  /* Get Data Source Institution */
  fgets(buffer, BUFFSIZE, fp);
  buffer[strlen(buffer)-1] = '\0';
  status = nc_put_att_text(ncid, NC_GLOBAL, "Source", strlen(buffer)+1, buffer);
  if (status != NC_NOERR) handle_error(status);
  printf("Source: %s\n", buffer);

  /* Get probe name */
  fgets(buffer, BUFFSIZE, fp);
  buffer[strlen(buffer)-1] = '\0';
  status = nc_put_att_text(ncid, NC_GLOBAL, "SNAME", strlen(buffer)+1, buffer);
  if (status != NC_NOERR) handle_error(status);
  printf("SNAME: %s\n", buffer);

  /* Get project name */
  fgets(buffer, BUFFSIZE, fp);
  buffer[strlen(buffer)-1] = '\0';
  status = nc_put_att_text(ncid, NC_GLOBAL, "ProjectName", strlen(buffer)+1, buffer);
  if (status != NC_NOERR) handle_error(status);
  printf("ProjectName: %s\n", buffer);


  /* Get IVOL NVOL */
  fgets(buffer, BUFFSIZE, fp);
  buffer[strlen(buffer)-1] = '\0';
  status = nc_put_att_text(ncid, NC_GLOBAL, "IVOL_NVOL", strlen(buffer)+1, buffer);
  if (status != NC_NOERR) handle_error(status);
  printf("IVOL NVOL: %s", buffer);


  /* get data start date and processing date */
  fgets(buffer, BUFFSIZE, fp);
  printf("start date, date processed: %s", buffer);
  if (strchr(buffer, ','))
    sscanf(buffer, "%d , %d , %d", &year, &month, &day);
  else
    sscanf(buffer, "%d %d %d", &year, &month, &day);


  /* Calculate FlightDate and write it to netCDF file */
  if (year > 1900) year -= 1900;
  StartFlight.tm_year = year;
  StartFlight.tm_mon = month - 1;
  StartFlight.tm_mday = day;

  sprintf(tmp, "%02d/%02d/%d", month, day, 1900 + year);
  status = nc_put_att_text(ncid, NC_GLOBAL, "FlightDate", strlen(tmp)+1, tmp);
  if (status != NC_NOERR) handle_error(status);


  /* Calculate DateProcessed and write it to netCDF file */
  if (strchr(buffer, ','))
    sscanf(buffer, "%*d , %*d , %*d , %d , %d , %d", &year, &month, &day);
  else
    sscanf(buffer, "%*d %*d %*d %d %d %d", &year, &month, &day);

  if (year > 1900) year -= 1900;
  sprintf(tmp, "%02d/%02d/%d", month, day, 1900 + year);
  status = nc_put_att_text(ncid, NC_GLOBAL, "DateProcessed", strlen(tmp)+1, tmp);
  if (status != NC_NOERR) handle_error(status);

  if (status != NC_NOERR) handle_error(status);

  /* Get uniformity */
  fgets(buffer, BUFFSIZE, fp);
  printf("uniformity %s", buffer);
  if (atof(buffer) != 1.0)
    fprintf(stderr, "Non-uniform time interval, results may be sketchy.\n");


  /* Time segments.  Will be updated later.
   */
  status = nc_put_att_text(ncid, NC_GLOBAL, "TimeInterval", DEFAULT_TI_LENGTH, buffer);
  if (status != NC_NOERR) handle_error(status);


  /* First dimension is time dimension.
   * Second is Rate in Hz.
   * Third is Vector Length.
   */
  ndims = 1;
  dims[0] = TimeDim;
  dims[1] = RateDim;


  /* Time Variables.
   */
  createTime(dims);

  /* Skip XNAME */
  fgets(buffer, BUFFSIZE, fp);
  printf("skipping XNAME: %s", buffer);

  /* For each variable:
   *	- Set dimensions
   *	- define variable
   *	- Set attributes
   */
  /* Scan in Primary variables first.
   */
  /* Get number of variables */
  fgets(buffer, BUFFSIZE, fp);
  nVariables = atoi(buffer);
  printf("nVariables: %d\n", nVariables);


  if (histogram)
  {
    sprintf(buffer, "Vector%d", nVariables+1);
    status = nc_def_dim(ncid, buffer, nVariables+1, &VectorDim);
    if (status != NC_NOERR) handle_error(status);
    dims[2] = VectorDim;
  }


  /* Get Scale Factors. */
  fgets(buffer, BUFFSIZE, fp);
  printf("Scale Factors: %s", buffer);
  p = strtok(buffer, " \t\n\r");
  for (i = 0; i < nVariables; ++i)
  {
    scale[i] = atof(p);
    offset[i] = 0.0;
    printf("  scale[%d]: %f\n", i, scale[i]);
    p = strtok(NULL, " \t\n\r");
  }

  /* Get missing values, these will be translated to nimbus MISSING_VALUES.
   */
  fgets(buffer, BUFFSIZE, fp);
  printf("Missing Values: %s", buffer);
  p = strtok(buffer, " \t\n\r");
  for (i = 0; i < nVariables; ++i)
  {
    missingVals[i] = atof(p);
    printf("  missingVals[%d]: %f\n", i, missingVals[i]);
    p = strtok(NULL, " \t\n\r");
  }

  /* Get Titles. */
  printf("Get Titles...\n");
  for (i = 0; i < nVariables; ++i)
  {
    fgets(buffer, BUFFSIZE, fp);
    buffer[strlen(buffer)-1] = '\0';
    titles[i] = (char *)GetMemory(strlen(buffer)+1);
    strcpy(titles[i], buffer);
    p = strrchr(titles[i], '(');
    if ( (p = strrchr(titles[i], '(')) )
      *(p-1) = '\0';

    if ( (p = strrchr(buffer, '(')) && (p1 = strchr(p, ')')))
    {
      units[i] = (char *)GetMemory(p1 - p + 1);
      *p1 = '\0';
      strcpy(units[i], p+1);
    }
    else
    {
      units[i] = (char *)GetMemory(10);
      strcpy(units[i], "Unk");
    }
    printf("  titles[%d]: %s\n", i, titles[i]);
  }

  /* Get number of comment lines */
  fgets(buffer, BUFFSIZE, fp);
  nComments = atoi(buffer);
  printf("Number of comment lines: %d\n",nComments);
  for (i = 0; i < nComments; i++)
  {
    fgets(buffer, BUFFSIZE, fp);
    buffer[strlen(buffer)-1] = '\0';
    sprintf(tmp,"comment%d",i);
    status = nc_put_att_text(ncid, NC_GLOBAL, tmp, strlen(buffer)+1, buffer);
    if (status != NC_NOERR) handle_error(status);
  }


  /* Scan in Auxilary variables.
   */
  if (FFI == 1010)
  {
    fgets(buffer, BUFFSIZE, fp);
    start = nVariables;
    nVariables += atoi(buffer);
    printf("nVariables: %d\n", nVariables);

    /* Get Scale Factors. */
    fgets(buffer, BUFFSIZE, fp);
    printf("Auxilary Scale Factors: %s", buffer);
    p = strtok(buffer, " \t\n\r");
    for (i = start; i < nVariables; ++i)
    {
      scale[i] = atof(p);
      offset[i] = 0.0;
      printf("  auxilary scale[%d]: %f\n", i, scale[i]);
      p = strtok(NULL, " \t\n\r");
    }

    /* Get missing values, these will be xlated to nimbus MISSING_VALUES.
     */
    fgets(buffer, BUFFSIZE, fp);
    printf("Missing Values: %s", buffer);
    p = strtok(buffer, " \t\n\r");
    for (i = start; i < nVariables; ++i)
    {
      missingVals[i] = atof(p);
      printf("  missingVals[%d]: %f\n", i, missingVals[i]);
      p = strtok(NULL, " \t\n\r");
    }

    /* Get Titles. */
    printf("Auxilary Get Titles...\n");
    for (i = start; i < nVariables; ++i)
    {
      fgets(buffer, BUFFSIZE, fp);
      buffer[strlen(buffer)-1] = '\0';
      titles[i] = (char *)GetMemory(strlen(buffer)+1);
      strcpy(titles[i], buffer);
      printf("  auxilary titles[%d]: %s\n", i, titles[i]);

      if ( (p = strchr(buffer, '(')) && (p1 = strchr(buffer, ')')))
      {
        units[i] = (char *)GetMemory(p1 - p + 1);
        *p1 = '\0';
        strcpy(units[i], p+1);
      }
      else
      {
        units[i] = (char *)GetMemory(10);
        strcpy(units[i], "Unk");
      }

    }

  }

  if (verbose)
    printf("Header parsed... rewinding to read data\n");


  rewind(fp);
  for (i = 0; i < SkipNlines; ++i)
  {
    fgets(buffer, BUFFSIZE, fp);
    buffer[strlen(buffer)-1] = '\0';
    if ((p = strchr(buffer, '=')) != 0)
    {
      *p = '\0';
      printf("%s\n",buffer);
      if (strcmp(buffer,"CELLSIZES ") == 0)
      {
	++p;
        printf("%s\n",p);
	int j = 0;
        while ((p1 = strchr(p, ',')) != 0)
	{
	    *p1 = '\0';
	    printf("index: %d %s\n",j,p);
	    cellSizes[j++] = atof(p);
	    p = ++p1;
	}
	printf("index: %d %s\n",j,p);
	cellSizes[j++] = atof(p);
	nCells = j;

      }
    }
  }

  // Buffer now contains the last line of the header
  // which is the line with variable names

  // skip any leading whitespace in variable name line.
  for (p = buffer; isspace(*p); ++p)
    ;

  // split p into tokens and return pointer to first token
  // in this case, time
  p = strtok(p, " \t\n\r");

  if (dataRate > 1)
    ndims = 2;

  if (histogram)
  {
    // Histogram assumes that all columns in NASA Ames file (except time column)
    // contain bins of data for a single variable, and that all variable names
    // are the same to reflect this.
    if (nVariables > 1)
      ndims = 3;


    i=1;

    // return pointer to next variable in buffer
    p = strtok(NULL, " \t\n\r");
    status = nc_def_var(ncid, p, NC_FLOAT, ndims, dims, &varid[i]);
    if (status != NC_NOERR) handle_error(status);
    if (verbose)
      printf("Creating single 2D var [%s] from AMES file\n",p);


    //varName = p;
    if (verbose)
      printf("Adding variable [%s] with units of [%s]\n", p, units[0]);

    //Under RAF conventions, missing is always set to -32767
    if (RAFconventions)
      missingVals[i]=missing_val;

    status = nc_put_att_float(ncid,varid[i], "_FillValue",NC_FLOAT, 1, &missingVals[i]);
    if (status != NC_NOERR) handle_error(status);
    p = units[i];
    status = nc_put_att_text(ncid, varid[i], "units", strlen(p)+1, p);
    if (status != NC_NOERR) handle_error(status);
    p = titles[i];
    status = nc_put_att_text(ncid, varid[i], "long_name", strlen(p)+1, p);
    if (status != NC_NOERR) handle_error(status);
    status = nc_put_att_int(ncid, varid[i], "FirstBin",NC_INT, 1, &i);
    if (status != NC_NOERR) handle_error(status);
    status = nc_put_att_int(ncid, varid[i], "LastBin",NC_INT, 1, &nVariables);
    if (status != NC_NOERR) handle_error(status);
    status = nc_put_att_float(ncid, varid[i], "CellSizes",NC_FLOAT,nCells,cellSizes);
    if (status != NC_NOERR) handle_error(status);

    for (i = 1; i < nVariables; ++i)
    {
      p = strtok(NULL, " \t\n\r");
      //if( p != varName)
      //{
      //  printf("All variable names [%s] must be the same [as %s] in last line of header\n",p,varName);
      //  printf("  when -h (histogram) option to asc2cdf -a is used.\n");
      //}
      free(units[i]);
      free(titles[i]);
    }
  }
  else
  {
    if (verbose)
      printf("Creating %d 2D variables from AMES file\n",nVariables);

    for (i = 0; i < nVariables; ++i)
    {
      // return pointer to next variable in buffer
      p = strtok(NULL, " \t\n\r");

      // If variable contains units in parenthesis, remove units
      if ( (p1 = strchr(p, '('))  && (p2 = strchr(p1, ')')) )
      {
        varUnits =  (char *)GetMemory(p2 - p1 + 1);
        *p2 = '\0';
        strcpy(varUnits, p1+1);
        *p1 = '\0';
        if (strcmp(varUnits,units[i]) != 0) 
        {
          printf("WARNING: Units in titles [%s] and units in column header line [%s] don't match for variable [%s]\n",units[i],varUnits,p);
        }
      }

      if (verbose)
        printf("Adding variable [%s] with units of [%s]\n", p, units[i]);

      status = nc_def_var(ncid, p, NC_FLOAT, ndims, dims, &varid[i]);
      if (status != NC_NOERR) handle_error(status);

      //Under RAF conventions, missing is always set to -32767
      if (RAFconventions)
        missingVals[i]=missing_val;


      status = nc_put_att_float(ncid,varid[i], "_FillValue",NC_FLOAT, 1, &missingVals[i]);
      if (status != NC_NOERR) handle_error(status);
      p = units[i];
      status = nc_put_att_text(ncid, varid[i], "units", strlen(p)+1, p);
      if (status != NC_NOERR) handle_error(status);
      p = titles[i];
      status = nc_put_att_text(ncid, varid[i], "long_name", strlen(p)+1, p);
      if (status != NC_NOERR) handle_error(status);

      free(units[i]);
      free(titles[i]);
    }
  }
}	/* END CREATENASAAMESNETCDF */

/* END NASAAMES.C */
