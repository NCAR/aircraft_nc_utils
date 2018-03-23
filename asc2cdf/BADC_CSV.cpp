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

void CreateVar(int index,char *value,int ndims,int dims[3]);
void defVectorDim(int numVars, int *ndims, int dims[3]);
void processIntRef(char *ref,char *value,int *nVariables,int *index,int column,int *ndims,int dims[3]);
void processCharRef(char *buffer, char *tmpbuf, int *nVariables,int *i,int *j,int *ndims,int dims[3]);

/* -------------------------------------------------------------------- */
void CreateBADCnetCDF(FILE *fp)
{
  int i = 0, j = 0, a = 0; // a for attribute count per variable
  int TimeDim, RateDim;
  int year, month, day;
  int ndims, dims[3];
  int nAtts;
  char tmpbuf[BUFFSIZE];
  char *key=tmpbuf;
  char *ref;
  char *value;
  var_atts metadata[100]; // max 100 lines of attribute header
  int column = -1;	// First data column
  int found_short_name = 0;
  float atts[256];

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


  /* Read in Metadata (header)
   * Line with just the word "data" indicates end of metadata (almost)
   */
  printf("Get metadata\n");
  nVariables=0;
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

    // Read in a line from the csv file and parse
    // Get attribute key from line
    key=strtok(buffer, ",");	// key
    // Get reference indicator from line
    ref=strtok(NULL, ",");	// ref
    // Get everything else on the line
    value=strtok(NULL,"\0");	// value


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

      // Handle variable-specifc attributes
      else 
      {
        /* For each variable:
         *	- Set dimensions
         *	- define variable
         *	- Set attributes
	 * We need to find short_name and type before we can define the variable
	 * We need to define the variable before we can set attributes. Since vars and 
	 * atts can come in any order, queue up atts until var is defined.
         */

	// long name has units appended to the end so process as a special case
	if (strcmp(key,"long_name") == 0)
	{
	   strcpy(metadata[a].key, key);
	   strcpy(metadata[a].ref, ref);
	   strcpy(metadata[a].value, strtok(value,","));
	   value = strtok(NULL,"\0");
	   a++;
	   strcpy(metadata[a].key,"units");
	   strcpy(metadata[a].ref, ref);
	   strcpy(metadata[a].value, value);
	} 
	// all other lines contain one value per line
	else 
	{
	   strcpy(metadata[a].key, key);
	   strcpy(metadata[a].ref, ref);
	   strcpy(metadata[a].value, value);
	}

	a++; // attribute counter

        // BADC data can have either short_name metadata with integers for references, or 
	// omit short name and use short names for references. Handle the first 
	// case here.
	if (strcmp(key,"short_name") == 0)
	{
	    found_short_name = 1;
            processIntRef(ref,value,&nVariables,&i,column,&ndims,dims);
	}
      }
    }
  }

  // After the "data" line, we still have one more line of metadata - the list 
  // of reference IDs. If refs are the variable short names, read them into an
  // array to relate column number to ref. (If not, already handled above when
  // found short_name.
  fgets(buffer, BUFFSIZE, fp);
  buffer[strlen(buffer)-1] = '\0';
  SkipNlines +=1;
  printf("Read ref line: %s\n",buffer);

  // BADC data can have either short_name metadata with integers for references, or 
  // omit short name and use short names for references. Handle the first 
  // case here.
  if (found_short_name == 0)
  {
      processCharRef(buffer,tmpbuf,&nVariables,&i,&j,&ndims,dims);
      nvars = j;
      nVariables = nVariables -2; // Number of variables found
  } else {
      nvars = i;
  }
  printf("netCDF vars: %d\n",nvars);
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
	// skip type and short_name atts
	if (strcmp(metadata[a].key,"type") != 0 && strcmp(metadata[a].key,"short_name") != 0) {
	   // The variable's short name is histo_vars[i]
	   // The attribute short name is metadata[a].ref
	   for (i=0;i<nvars; i++) {
	       if (strcmp(histo_vars[i],metadata[a].ref) == 0) {
	           break;
	       }
	   }
	   // CellSizes need to be stored as an array of floats
	   if (strcmp(metadata[a].key,"CellSizes") == 0) {
	       j=0;
	       atts[j] = atof(strtok(metadata[a].value,","));
	       while ((value=strtok(NULL,",")) != NULL)
		   atts[++j] = atof(value);
	       status = nc_put_att_float(ncid,varid[i],metadata[a].key,NC_FLOAT, ++j, atts);
               if (status != NC_NOERR) handle_error(status);

#ifdef ZEROBIN
	       // If have cell sizes, then need to add histogram note that Zeroth data bin is an unused legacy placeholder
	       status = nc_put_att_text(ncid, varid[i],"HistogramNote",48,"Zeroth data bin is an unused legacy placeholder.");
	       if (status != NC_NOERR) handle_error(status);
#endif

	   } else 
	   // Store SampleVolume as a float
	   if (strcmp(metadata[a].key,"SampleVolume") == 0) {
	       atts[0] = atof(metadata[a].value);
	       status = nc_put_att_float(ncid,varid[i],metadata[a].key,NC_FLOAT,1,&atts[0]);
               if (status != NC_NOERR) handle_error(status);

	   // All other atts are stored as strings
	   } else {
               status = nc_put_att_text(ncid, varid[i],metadata[a].key,strlen(metadata[a].value)+1,metadata[a].value);
               if (status != NC_NOERR) handle_error(status);
	   }
       }
     }
  }

}	/* END CREATEBADCNETCDF */

/* -------------------------------------------------------------------- */
void CreateVar(int index, char *value, int ndims, int dims[3])
{
   // All variables are written to the RAF NetCDF file as float.
   status = nc_def_var(ncid, value, NC_FLOAT, ndims, dims, &varid[index]);
   if (status != NC_NOERR) handle_error(status);

   // Add _FillValue attribute as float
   missingVals[0]=MISSING_VALUE;
   status = nc_put_att_float(ncid,varid[index], "_FillValue",NC_FLOAT, 1, &missingVals[0]);
   if (status != NC_NOERR) handle_error(status);
}

/* -------------------------------------------------------------------- */
void defVectorDim(int numVars, int *ndims, int dims[3])
{
   int dimid;
   int VectorDim;

   // set 3rd dimension (if not already set for another histo var)
   // In other words, once have Vector27, don't want to define it
   // again, but can define Vector10, or whatever.
   sprintf(buffer, "Vector%d", numVars);

   status = nc_inq_dimid(ncid,buffer,&dimid);
   if (status == -46) // Invalid dimension id or name, e.g dim doesn't exist
   { 
       status = nc_def_dim(ncid, buffer, numVars, &VectorDim);
       if (status != NC_NOERR) handle_error(status);
       dims[2] = VectorDim;
   } else
   if (status == NC_NOERR) // dimension exists, assign ID of dim, to dims[2]
   {
       dims[2] = dimid;
   } else // unknown status; warn user
   {
       handle_error(status);
   }
   *ndims =3; // histograms have 3 dimensions

}

/* -------------------------------------------------------------------- */
/* BADC data can have either short_name metadata with integers for references, or 
 * omit short name and use short names for references. Handle the first 
 * case here.
 */
void processIntRef(char *ref,char *value,int *nVariables,int *i,int column,int *ndims,int dims[3])
{
  int first_bin, last_bin, numVars;
  int j;

  // Associate this column reference with this variable index. 
  strcpy(histo_vars[*i],ref); 

  // There is not a colon in the reference ID, so we have found a timeseries variable
  if (strchr(ref,':') == NULL) {
      column++;	// Count of columns of data expected.
      *ndims = 2;
      if (strcmp(value,"Time") != 0) 	// NOT time var
      {
        strcpy(vars_columns[*nVariables],ref); 
        *nVariables=*nVariables+1;
      }
  }  

  // There is a colon in the reference ID, so we have found a histogram
  // Look for histograms (just once for each var, or will over-count 
  // numVars - I chose to look when find a short_name, but any metadata field that exists for every
  // var will work equally well.)
  else {
      first_bin = atoi(strtok(ref,":"));
      last_bin = atoi(strtok(NULL,":"));
      numVars = last_bin-first_bin+1;
      printf("Found histogram variable: %s:%d (%d)\n",value,*i,numVars);

      // Associate this column reference with this variable index. 
      for (j=0;j<numVars;j++) {
        strcpy(vars_columns[*nVariables+j],ref); 
      }
      *nVariables=*nVariables+numVars;

      // Add new histogram dimension
#ifdef ZEROBIN
      defVectorDim(numVars+1,ndims,dims);
#else
      defVectorDim(numVars,ndims,dims);
#endif

      numVars=numVars+column;
  } 

  // Create variables
  if (strcmp(value,"Time") != 0) 	// NOT time var
  {
     CreateVar(*i,value,*ndims,dims);
     *i=*i+1;
  }
}

/* -------------------------------------------------------------------- */
/* BADC data can have either short_name metadata with integers for references, or 
 * omit short name and use short names for references. Handle the second 
 * case here.
 */
void processCharRef(char *buffer,char *tmpbuf,int *nVariables,int *i,int *j,int *ndims,int dims[3])
{
  int first_bin, last_bin, numVars;
  char *lastVar = tmpbuf;
  char *ref;

  // Parse the column headers to get short names.
  *i=1;
  *j=0;

  *ndims = 2; // To start, assume we are reading in a timeseries variable
  ref=strtok(buffer, ","); // Read in the first column header. Should be time.
  first_bin = -1;
  strcpy(lastVar,"xxx");
  while (1)
  {
     if (ref != NULL && strcmp(lastVar,ref) == 0) 
     { 
         // Found a duplicate variable, which means we have a histogram
         if (first_bin == -1) { // Build up which columns this var spans.
	     first_bin = *i;
    	 }
	 last_bin = *i+1;
     } 
     else 
     { 
	 // Vars don't match, so either end of a histogram, or just a 
	 // single timeseries var
	 if (first_bin == -1) { 
	     // timeseries
	     numVars = 1; 
	 } else {
	     numVars = last_bin - first_bin + 1;
	     first_bin = -1;
	     printf("Found histogram variable: %s  %d (%d)\n",lastVar,*i,numVars);

	     // Add new histogram dimension
#ifdef ZEROBIN
             defVectorDim(numVars+1,ndims,dims);
#else
             defVectorDim(numVars,ndims,dims);
#endif
	     printf("ndims: %d %d\n",*ndims,dims[2]);
             printf("dims: %d %d %d\n",dims[0],dims[1],dims[2]);
	 }

	 // Create variables
	 if (strcmp(lastVar,"xxx") != 0 && strcmp(lastVar,"Time") != 0)  // NOT time var
	 {
             CreateVar(*j,lastVar,*ndims,dims);

	     strcpy(histo_vars[*j],lastVar);
	     *j=*j+1;
	 }

	 *nVariables=*nVariables+numVars;
	 if (ref == NULL) {break;}
     }
     if (strcmp(ref,"Time") != 0) { // Not time var
         strcpy(vars_columns[*i-1],ref); 
         *i=*i+1;
     }

  lastVar = ref;
  ref=strtok(NULL, ",");
  }
}

/* END BADC_CSV.C */
