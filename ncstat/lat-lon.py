#!/usr/bin/env python3
import os, subprocess

output = ''
min_lat = []
max_lat = []
min_lon = []
max_lon = []

# call ncstat on all .nc files in current directory
for filename in os.listdir('.'):
  if filename.endswith(".nc"):
    output += filename
    output += "\n"
    output += subprocess.check_output(["ncstat", "-c", "-v", "LAT", "LON", "-f", filename])

# save output to file for error checking
file = open("lat-lon-output.txt", "w")
file.write(output)
file.close

for line in output.splitlines():
  if line.startswith("LAT"):  
    max_lat.append(float(line.split()[4]))
    min_lat.append(float(line.split()[3]))
  if line.startswith("LON"):
    max_lon.append(float(line.split()[4]))
    min_lon.append(float(line.split()[3]))


print('Maximum Latitude (North): ', max(max_lat))
print('Minimum Latitude (South): ', min(min_lat))
print('Maximum Longitude (East): ', max(max_lon))
print('Minimum Longitude (West): ', min(min_lon))
