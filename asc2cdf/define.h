#define NO_NETCDF_2

#include <cctype>
#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <ctime>

#include <netcdf.h>

#define BUFFSIZE            8192
#define MAX_VARS            500
#define DEFAULT_TI_LENGTH   (20)
#define MISSING_VALUE       (-32767.0)

enum InputFileType { PLAIN_FILE, NASA_AMES, NASA_LANGLEY, ICARTT, BADC_CSV };

extern char	buffer[];
extern int	ncid, varid[], nVariables, nvars, timeOffsetID, timeVarID, baseTimeID;
extern int      nComments;
extern float	scale[], offset[], missingVals[];
extern const char	*time_vars[];
extern const char	*noTitle, *noUnits;
extern const int	rateOne;
extern time_t	BaseTime;
extern int	BaseDataRate, dataRate;
extern bool	verbose;
extern bool	RAFconventions;
extern bool	histogram;
extern char	histo_vars[][256];	// array to store names of histogram vars
extern char	vars_columns[][256];	// array to relate variable number to column 
					// reference for which it contains data.

extern int	SkipNlines;
extern int	status;

void CreateNASAamesNetCDF(FILE *fp);
void CreateNASAlangNetCDF(FILE *fp);
void CreateICARTTnetCDF(FILE *fp);
void CreateBADCnetCDF(FILE *fp);
void CreatePlainNetCDF(FILE *fp);
void SetNASABaseTime(int, int, int), SetPlainBaseTime(void);
void createTime(int dims[]);
void handle_error(int);
