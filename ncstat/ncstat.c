
/**
 * Copyright (c) 2016, University Corporation for Atmospheric Research
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 * 3. Neither the name of the copyright holder nor the names of its
 *   contributors may be used to endorse or promote products derived from this
 *   software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

/**
 * @author Nicholas DeCicco <decicco@ucar.edu>
 *                          <nsd.cicco@gmail.com>
 */

#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <netcdf.h>

typedef struct {
	int hour;
	int minute;
	int second;
} Time;

int parse_time(char const*const str, Time *const start, Time *const end);

void print_statistics_f(float const*const v,
                        const int firstPoint,
                        const int lastPoint,
                        const int sampleRate,
                        const char name[]);

void show_usage();

int time_to_int(Time const*const t);

int main(int argc, char **argv)
{
	char *inFileName = NULL;
	int ncerr;
	int ncid;
	int numDims, numVars, numGlobalAttrs, unlimitedDim;
	void *data = NULL;
	char varName[NC_MAX_NAME+1];
	nc_type varType;
	int varNumDims, varNumAttrs;
	int *varIds = NULL;
	int i, j;
	size_t varSize;
	size_t len;
	int varDims[NC_MAX_VAR_DIMS];
	Time fileStartTime, fileEndTime, selectedStartTime, selectedEndTime;
	int timeRangeSpecified = 0;
	char *buf;
	int firstPoint, lastPoint, selectedStart, selectedEnd, fileStart, fileEnd;
	int nextOption;
	int sampleRate;

	do {
		switch ((nextOption = getopt(argc, argv, "t:"))) {
			case 't': /* Specify a time range */
				if (parse_time(optarg, &selectedStartTime, &selectedEndTime))
				{
					timeRangeSpecified = 1;
				} else {
					fprintf(stderr, "Error: Invalid time range.\n");
					exit(1);
				}
				break;
			default:
				break;
		}
	} while (nextOption >= 0);

	if (optind = argc-1) {
		inFileName = argv[optind];
	} else {
		if (optind < argc) {
			fprintf(stderr, "Error: Unexpected arguments\n");
		} else {
			fprintf(stderr, "Error: Expected an input filename\n");
		}
		exit(1);
	}

	if ((ncerr = nc_open(inFileName, NC_NOWRITE, &ncid)) != NC_NOERR) {
		fprintf(stderr, "\n");
		return 1;
	}

	nc_inq(ncid, &numDims, &numVars, &numGlobalAttrs, &unlimitedDim);

	if (!(varIds = (int*) malloc(sizeof(int)*numVars))) {
		goto malloc_fail;
	}
	nc_inq_varids(ncid, &numVars, varIds);

	nc_inq_attlen(ncid, NC_GLOBAL, "TimeInterval", &len);
	if (!(buf = (char*) malloc(sizeof(char)*(len+1)))) {
		free(varIds);
		goto malloc_fail;
	}
	nc_get_att_text(ncid, NC_GLOBAL, "TimeInterval", buf);

	/* There is no guarantee that a text attribute will be null-terminated. */
	if (buf[len-1] != '\0') {
		buf[len] = '\0';
	}
	if (!parse_time(buf, &fileStartTime, &fileEndTime)) {
		fprintf(stderr, "Error: failed to parse 'TimeInterval' attribute "
		                "for this file\n");
		exit(1);
	}

	/* Ensure that the requested time range falls within the time range
	 * covered by the file.
	 */
	if (timeRangeSpecified) {
		selectedStart = time_to_int(&selectedStartTime);
		selectedEnd   = time_to_int(&selectedEndTime);
		fileStart     = time_to_int(&fileStartTime);
		fileEnd       = time_to_int(&fileEndTime);

		if (selectedStart < fileStart || selectedStart > fileEnd ||
		    selectedEnd   < fileStart || selectedEnd   > fileEnd)
		{
			fprintf(stderr, "Error: Time range not within file limits.\n");
			exit(1);
		}

		firstPoint = selectedStart - fileStart;
		lastPoint  = selectedEnd - fileStart;
	} else {
		firstPoint = 0;
	}

	printf("name,len,min,max,stddev,variance,mean\n");

	for (i = 0; i < numVars; i++) {
		nc_inq_var(ncid, varIds[i], varName, &varType, &varNumDims, varDims,
		           &varNumAttrs);

		sampleRate = 1;
		for (j = 0; j < varNumDims; j++) {
			nc_inq_dimlen(ncid, varDims[j], &len);
			if (j == 0) {
				varSize = len;
				if (!timeRangeSpecified) {
					lastPoint = len-1;
				}
			} else {
				sampleRate *= len;
				varSize *= len;
			}
		}

		switch (varType) {
			case NC_FLOAT:
				if (!(data = (float*) realloc(data, sizeof(float) * varSize))) {
					goto malloc_fail;
				}
				if ((ncerr = nc_get_var_float(ncid, varIds[i], (float*) data)) != NC_NOERR) {
					goto get_var_err;
				}
				print_statistics_f((float*) data, firstPoint, lastPoint,
				                   sampleRate, varName);
				break;
			case NC_INT:
#if 0
				if (!(data = (int*) realloc(data, sizeof(int) * varSize))) {
					goto malloc_fail;
				}
				if ((ncerr = nc_get_var_int(ncid, varIds[i], (int*) data)) != NC_NOERR) {
					goto get_var_err;
				}
				break;
#endif
			default:
				break;
		}
	}

	free(varIds); varIds = NULL;
	free(data);

	nc_close(ncid);

	return 0;

get_var_err:
	fprintf(stderr, "Failed to get variable\n");
	return 1;

malloc_fail:
	fprintf(stderr, "Memory allocation failed\n");
	return 1;
}

#define MIN(a,b) ((a) < (b) ? (a) : (b))
#define MAX(a,b) ((a) > (b) ? (a) : (b))

void print_statistics_f(float const*const v,
                        const int firstPoint,
                        const int lastPoint,
                        const int sampleRate,
                        const char name[])
{
	int i;
	double mean = 0.0f;    /* expectation value of x */
	double exp_xsq = 0.0f; /* expectation value of x^2 */
	double variance, stddev;
	double min, max;
	int numPoints = (lastPoint - firstPoint + 1)*sampleRate;

	min = max = v[0];

	for (i = firstPoint*sampleRate; i < lastPoint*sampleRate; i++) {
		mean += ((double) v[i]);
		exp_xsq += ((double) v[i])*((double) v[i]);
		min = MIN(min, (double) v[i]);
		max = MAX(max, (double) v[i]);
	}
	mean /= (double) numPoints;

	for (i = firstPoint*sampleRate; i < lastPoint*sampleRate; i++) {
		variance += (((double) v[i]) - mean)*(((double) v[i]) - mean);
	}
	variance /= (double) numPoints;
	stddev = sqrtf(variance);

	printf("%s,%d,%g,%g,%g,%g,%g\n",
	       name, numPoints, min, max, stddev, variance, mean);
}

int parse_time(char const*const str, Time *const start, Time *const end)
{
	return 6 == sscanf(str, "%d:%d:%d-%d:%d:%d",
	                   &(start->hour), &(start->minute), &(start->second),
	                   &(end->hour), &(end->minute), &(end->second));
}

void show_usage()
{
	printf("Usage:\n"
	       "\n"
	       "    ncstat [-t TIME_RANGE] INFILE\n");
}

int time_to_int(Time const*const t)
{
	return t->second + 60*(t->minute + 60*t->hour);
}
