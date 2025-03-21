/*
-------------------------------------------------------------------------
OBJECT NAME:	nasaLangley.c

FULL NAME:	NASA ASCII to Nimbus-netCDF Low Rate

ENTRY POINTS:	CreateNASAlangNetCDF()

DESCRIPTION:	Translate NASA ASCII file to Nimbus Low Rate netCDF file

COPYRIGHT:	University Corporation for Atmospheric Research, 1996-07
-------------------------------------------------------------------------
*/

#include "define.h"

static struct tm	StartFlight;

/* -------------------------------------------------------------------- */
void CreateNASAlangNetCDF(FILE *fp)
{
  size_t i, j, cnt;
  int	year, month, day;
  int	ndims, dims[3], TimeDim, RateDim;
  char	*p, name[16], units[16], tmp[32];
  float	missingVal = MISSING_VALUE;


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


  fgets(buffer, BUFFSIZE, fp);
  SkipNlines = atoi(buffer);
  printf("SkipNlines: %d\n", SkipNlines);

  fgets(buffer, BUFFSIZE, fp);	/* Skip file name	*/
  printf("Skip file name: %s", buffer);

  fgets(buffer, BUFFSIZE, fp);
  buffer[strlen(buffer)-1] = '\0';
  status = nc_put_att_text(ncid, NC_GLOBAL, "PI", strlen(buffer)+1, buffer);
  if (status != NC_NOERR) handle_error(status);
  printf("PI: %s\n", buffer);

  fgets(buffer, BUFFSIZE, fp);
  buffer[strlen(buffer)-1] = '\0';
  status = nc_put_att_text(ncid, NC_GLOBAL, "Species", strlen(buffer)+1, buffer);
  if (status != NC_NOERR) handle_error(status);
  printf("Species: %s\n", buffer);

  fgets(buffer, BUFFSIZE, fp);
  buffer[strlen(buffer)-1] = '\0';
  status = nc_put_att_text(ncid, NC_GLOBAL, "ProjectName", strlen(buffer)+1, buffer);
  if (status != NC_NOERR) handle_error(status);
  printf("ProjectName: %s\n", buffer);

  fgets(buffer, BUFFSIZE, fp);
  printf("date span: %s\n", buffer);
  if (strchr(buffer, ','))
    sscanf(buffer, "%d , %d , %d", &year, &month, &day);
  else
    sscanf(buffer, "%d %d %d", &year, &month, &day);

  if (year > 1900) year -= 1900;
  StartFlight.tm_year = year;
  StartFlight.tm_mon = month - 1;
  StartFlight.tm_mday = day;

  sprintf(tmp, "%02d/%02d/%d", month, day, 1900 + year);
  status = nc_put_att_text(ncid, NC_GLOBAL, "FlightDate", strlen(tmp)+1, tmp);
  if (status != NC_NOERR) handle_error(status);

  if (strchr(buffer, ','))
    sscanf(buffer, "%*d , %*d , %*d , %d , %d , %d", &year, &month, &day);
  else
    sscanf(buffer, "%*d %*d %*d %d %d %d", &year, &month, &day);

  if (year > 1900) year -= 1900;
  sprintf(buffer, "%02d/%02d/%d", month, day, 1900 + year);
  status = nc_put_att_text(ncid, NC_GLOBAL, "DateProcessed", strlen(buffer)+1, buffer);
  if (status != NC_NOERR) handle_error(status);


  fgets(buffer, BUFFSIZE, fp);
  sprintf(tmp, "%d", atoi(buffer));
  status = nc_put_att_text(ncid, NC_GLOBAL, "FlightNumber", strlen(tmp)+1, tmp);
  if (status != NC_NOERR) handle_error(status);
  printf("FlightNumber: %s\n", tmp);

  /* Time segments.  Will be updated later.
   */
  status = nc_put_att_text(ncid, NC_GLOBAL, "TimeInterval", DEFAULT_TI_LENGTH, buffer);
  if (status != NC_NOERR) handle_error(status);


  fgets(buffer, BUFFSIZE, fp);
  nVariables = atoi(buffer);
  printf("nVariables: %d\n", nVariables);

  fgets(buffer, BUFFSIZE, fp);	/* Skip nComment lines.	*/
  printf("Skip nComment lines: %s\n", buffer);

  /* File type, we support type = 1 */
  fgets(buffer, BUFFSIZE, fp);
  if (atoi(buffer) != 1)
    {
    fprintf(stderr, "Only support data type = 1 (line 10).\n");
    exit(1);
    }


  /* First dimension is time dimension.
   * Second is Rate in Hz.
   * Third is Vector Length.
   */
  status = nc_def_dim(ncid, "Time", NC_UNLIMITED, &TimeDim);
  if (status != NC_NOERR) handle_error(status);

  fgets(buffer, BUFFSIZE, fp);	/* Line 11, Averaging Rate	*/
  BaseDataRate = atoi(buffer);

  fgets(buffer, BUFFSIZE, fp);	/* Line 12, Data Rate (Hz)	*/
  dataRate = atoi(buffer);
  sprintf(buffer, "sps%d", dataRate);
  status = nc_def_dim(ncid, buffer, dataRate, &RateDim);
  if (status != NC_NOERR) handle_error(status);

  ndims = 1;
  dims[0] = TimeDim;
  dims[1] = RateDim;

  if (dataRate > 1)
    ndims = 2;


  /* Time Variables.
   */
  createTime(dims);

  /* For each variable:
   *	- Set dimensions
   *	- define variable
   *	- Set attributes
   */
  fgets(buffer, BUFFSIZE, fp);
  fgets(buffer, BUFFSIZE, fp);	/* Skip Julian day & seconds.	*/
  nVariables -= 2;

  for (i = 0; i < (size_t)nVariables; ++i)
  {
    fgets(buffer, BUFFSIZE, fp);

    p = strtok(buffer, "\t ,");
    for (cnt = j = 0; j < strlen(p) && j < 16; ++j)
      if (isalnum(p[j]))
        name[cnt++] = p[j];

    name[cnt] = '\0';

    p = strtok(NULL, "\t ,");
    for (cnt = j = 0; j < strlen(p) && j < 16; ++j)
      if (isalnum(p[j]) || p[j] == '/')
        units[cnt++] = p[j];

    units[cnt] = '\0';


    p = strtok(NULL, "\t ,");
    scale[i] = atof(p);

    p = strtok(NULL, "\t ,");
    offset[i] = atof(p);

    p = strtok(NULL, "\t ,");
    p = strtok(NULL, "\t ,");
    p = strtok(NULL, "\t ,");
    missingVals[i] = atof(p);


    if (verbose)
      printf("Adding variable [%s] with units of [%s]\n", name, units);

    status = nc_def_var(ncid, name, NC_FLOAT, ndims, dims, &varid[i]);
    if (status != NC_NOERR) handle_error(status);
    status = nc_put_att_float(ncid,varid[i], "_FillValue",NC_FLOAT, 1, &missingVal);
    if (status != NC_NOERR) handle_error(status);
    status = nc_put_att_text(ncid, varid[i], "units", strlen(units)+1, units);
    if (status != NC_NOERR) handle_error(status);
    status = nc_put_att_text(ncid, varid[i], "long_name", strlen(noTitle)+1, noTitle);
    if (status != NC_NOERR) handle_error(status);
  }
}	/* END CREATENASALANGNETCDF */

/* END NASALANGLEY.C */
