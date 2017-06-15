/*
-------------------------------------------------------------------------
OBJECT NAME:	BADC_CSV.c

FULL NAME:	BADC_CSV to Nimbus-netCDF Low Rate

ENTRY POINTS:	CreateBADCnetCDF()

DESCRIPTION:	Translate BADC_CSV file to Nimbus Low Rate netCDF file

COPYRIGHT:	University Corporation for Atmospheric Research, 1996-2017
-------------------------------------------------------------------------
*/

#include "define.h"


void *GetMemory(size_t nbytes);

typedef struct {	// Variable attributes
    char key[256];
    char ref [256];
    char value [256];
} var_atts;



/* -------------------------------------------------------------------- */
void CreateBADCnetCDF(FILE *fp)
{
  int i = 0, a = 0; // a for attribute count per variable
  int TimeDim, RateDim, VectorDim;
  int year, month, day;
  int ndims, dims[3];
  int dimid;
  int nAtts;
  int first_bin, last_bin, numVars, extraVars = 0;
  char tmpbuf[BUFFSIZE];
  char *key=tmpbuf;
  char *ref;
  char *value;
  var_atts metadata[100]; // max 100 lines of attribute header
  int column = -1;	// First data column

  printf("Converting BADC-CSV file to NetCDF\n");

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

    t = time(0);
    tm = *gmtime(&t);
    strftime(buffer, 128, "%h %d %R GMT %Y", &tm);
    status = nc_put_att_text(ncid, NC_GLOBAL, "DateConvertedFromASCII", 
                  strlen(buffer)+1, buffer);
    if (status != NC_NOERR) handle_error(status);
  }


  /* Get Conventions indicator (line 1) */
  fgets(buffer, BUFFSIZE, fp);
  sscanf(buffer, "Conventions,G,%s", tmpbuf);
  printf("Conventions: %s\n", tmpbuf);

  if (strcmp(tmpbuf,"BADC-CSV,1") != 0)
  {
    fprintf(stderr, "This code only handles BADC-CSV files. Ensure Conventions are set to BADC-CSV.\n");
    exit(1);
  }

  /* Set up NetCDF file specs */
  /* First dimension is time dimension.
   * Second is Rate in Hz.
   * Third is Vector Length.
   */
  ndims = 1;
  dims[0] = TimeDim;
  dims[1] = RateDim;

  if (dataRate > 1)
    ndims = 2;

  /* Time Variables.
   */
  createTime(dims);

  status = nc_enddef(ncid);
  if (status != NC_NOERR) handle_error(status);
  nc_redef(ncid);
  if (status != NC_NOERR) handle_error(status);


  /* Get title, add to global attributes */
  printf("Get metadata\n");
  while (strncmp(key,"data",4) != 0)
  {
    fgets(buffer, BUFFSIZE, fp);
    // Count number of lines in header
    SkipNlines +=1;
    // handle either unix, mac, or linux line terminators
    while (buffer[strlen(buffer)-1] == '\n' || buffer[strlen(buffer)-1] == '\r')
    {
	buffer[strlen(buffer)-1] = '\0';
    }
    // Read in a line from the csv file
    //printf("Read line: %s\n",buffer);
    // Get attribute key from line
    key=strtok(buffer, ",");
    //printf("Key: x%sx\n",key);
    // Get reference indicator from line
    ref=strtok(NULL, ",");
    // Get everything else on the line
    value=strtok(NULL,"\0");


    // This code currently does not parse "scale_factor, add_offset, or missing via valid_min, etc.
    // Warn user.
    if ( strcmp(key,"scale_factor") == 0 || strcmp(key,"add_offset") == 0  || strcmp(key,"valid_min") == 0)
    {
      printf("WARNING: This code does not parse scale_factor, add_offset, or missing value \
	      indicators from the metadata header, but one or more of these was found. Code \
	      sets these to 1,0, and -32767 respectively. BADC_CSV.c needs to be updated.");
      exit(1);
    }
    // If the reference indictor is null, either the line is malformed, or
    // you found the end of metadata, begin data marker.
    if (ref == NULL && strncmp(key,"data",4) != 0) 
    {
	printf("Line: %s - doesn't appear to follow BADC-CSV conventions\n",buffer);
        exit(1);
    }
    // Parse reference indicators
    if (ref != NULL) 
    {
      // Look for Global attributes
      if (*ref == 'G')
      {
	// Convert BADC_CSV keys, to keys we expect in RAF NetCDF.
        if (strcmp(key,"date_valid") == 0) {
	   status = nc_put_att_text(ncid, NC_GLOBAL, key, strlen(value)+1, value);
           if (status != NC_NOERR) handle_error(status);
	   // Parse out year, month, day and write to time struct for use in calculating
	   // basetime in asc2cdf.c
	   sscanf(value, "%d-%d-%d",&year, &month, &day);
	   sprintf(value,"%d/%d/%d",month, day, year);
	   status = nc_put_att_text(ncid, NC_GLOBAL, "FlightDate", strlen(value)+1, value);
           if (status != NC_NOERR) handle_error(status);

	   /* Calculate FlightDate and write it to netCDF file */
	   if (year > 1900) year -= 1900;
	   extern struct tm StartFlight;
	   StartFlight.tm_year = year;
	   StartFlight.tm_mon = month - 1;
	   StartFlight.tm_mday = day;

	// Other keys can go to netCDF as-is.
	} else {
	   status = nc_put_att_text(ncid, NC_GLOBAL, key, strlen(value)+1, value);
           if (status != NC_NOERR) handle_error(status);
	}
        if (status != NC_NOERR) handle_error(status);
      }
      else 
      {
        /* For each variable:
         *	- Set dimensions
         *	- define variable
         *	- Set attributes
	 * We need to find short_name and type before we can define the variable
	 * We need to define the variable before we can set attributes. Since vars and atts can come in any order,
	 * need to queue up atts until var is defined.
         */

	if (strcmp(key,"long_name") == 0)
	{
	   strcpy(metadata[a].key, key);
	   strcpy(metadata[a].ref, ref);
	   strcpy(metadata[a].value, strtok(value,","));
	   value = strtok(NULL,"\0");
	   a++;
	   strcpy(metadata[a].key,"units");
	   strcpy(metadata[a].ref, ref);
	   if (strcmp(value,"1")==0) {
	       // BADC uses units of 1 for counts, whereas RAF uses units of #. Convert here.
	       strcpy(metadata[a].value, "#");
	   } else {
	       strcpy(metadata[a].value, value);
	   }
	} else {
	   strcpy(metadata[a].key, key);
	   strcpy(metadata[a].ref, ref);
	   strcpy(metadata[a].value, value);
	}
	a++;

	if (strcmp(key,"short_name") == 0)
	{
            if (strchr(ref,':') == NULL) {
	      // There is not a colon in the reference ID, so we have found a timeseries variable
	      // Associate this column with this variable index. If there is no histogram 
	      // data, this will be a one-to-one relationship.
              vars_columns[column] = i;
	      column++;	// Count of columns of data expected.
	      ndims = 2;

	    }  else {
	      // There is a colon in the reference ID, so we have found a histogram
              // Look for histograms (just once for each var, or will over-count 
	      // numVars - I chose to look when find a short_name, but any metadata field that exists for every
	      // var will work equally well.)

	      strcpy(histo_vars[i],value);
	      first_bin = atoi(strtok(ref,":"));
	      last_bin = atoi(strtok(NULL,":"));
	      numVars = last_bin-first_bin;
	      printf("Found histogram variable: %s:%d (%d)\n",histo_vars[i],i,numVars);
	      extraVars += numVars;
              // set 3rd dimension (if not already set for another histo var)
	      // In other words, once have Vector26, don't want to define it
	      // again, but can define Vector10, or whatever.
              sprintf(buffer, "Vector%d", numVars+1);

	      status = nc_inq_dimid(ncid,buffer,&dimid);
              //if (status != NC_NOERR) handle_error(status);
	      if (status == -46) // Invalid dimension id or name, e.g dim doesn't exist
	      {
                status = nc_def_dim(ncid, buffer, numVars+1, &VectorDim);
                if (status != NC_NOERR) handle_error(status);
	      }
              dims[2] = VectorDim;
	      

	      numVars=numVars+column+1;
	      for (;column<numVars;++column) {
		  vars_columns[column] = i;
	      }

	      ndims = 3;
            } 


	    // Create variables
	    if (strcmp(value,"Time") != 0) 	// NOT time var
	    {
	      // All variables are written to the RAF NetCDF file as float.
	      status = nc_def_var(ncid, value, NC_FLOAT, ndims, dims, &varid[i]);
              if (status != NC_NOERR) handle_error(status);

	      // Add _FillValue attribute as float
	      missingVals[0]=MISSING_VALUE;
	      status = nc_put_att_float(ncid,varid[i], "_FillValue",NC_FLOAT, 1, &missingVals[0]);
              if (status != NC_NOERR) handle_error(status);
	    
	      i++;
	    }
	}
      }
    }
  }

  // Number of variables found, plus extras for histograms
  nVariables = i + extraVars;
  printf("nVariables: %d\n",nVariables);
  nAtts = a;
  printf("total nAtts: %d\n",nAtts);

  // Have not implemented scale/offset/missing values, so set them
  // to constants here.
  for (i=0;i<nVariables;i++) {
    scale[i]=1;
    offset[i]=0;
    missingVals[i]=MISSING_VALUE;
  }

    
  // Now that we've read in all the metadata, add attributes to the vars in the NetCDF file.
  for (a=0;a<nAtts;a++) {
     if (atoi(metadata[a].ref) != 1) { // skip time
	if (strcmp(metadata[a].key,"type") != 0 && strcmp(metadata[a].key,"short_name") != 0) {
           status = nc_put_att_text(ncid, varid[atoi(metadata[a].ref)-1],metadata[a].key,strlen(metadata[a].value)+1,metadata[a].value);
           if (status != NC_NOERR) handle_error(status);
       }
     }
  }


// After the "data" line, we still have one more line of metadata - the list of reference
// IDs. Read them in and conmpare to the IDs I used as keys to the vars array.
     fgets(buffer, BUFFSIZE, fp);
     buffer[strlen(buffer)-1] = '\0';
     SkipNlines +=1;
     printf("Read ref line: %s\n",buffer);

}	/* END CREATEBADCNETCDF */

/* END BADC_CSV.C */
