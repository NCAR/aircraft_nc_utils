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

enum InputFileType { PLAIN_FILE, NASA_AMES, NASA_LANGLEY };

extern char	buffer[];
extern int	ncid, varid[], nVariables, timeOffsetID, timeVarID, baseTimeID;
extern float	scale[], offset[], missingVals[];
extern const char	*time_vars[];
extern const char	*noTitle, *noUnits;
extern const int	rateOne;
extern time_t	BaseTime;
extern int	BaseDataRate, dataRate;
extern struct tm	StartFlight;

extern int	SkipNlines;

void CreateNASAamesNetCDF(FILE *fp);
void CreateNASAlangNetCDF(FILE *fp);
void CreatePlainNetCDF(FILE *fp);
void SetNASABaseTime(void), SetPlainBaseTime(void);
void AddTimeVariables(int dims[]);
