import os 
from os.path import exists
from PyQt5.QtWidgets import QTextBrowser, QGroupBox, QGridLayout, QWidget, QHBoxLayout, QFrame, QScrollBar, QToolBar, QMessageBox, QFileDialog, QTableWidgetItem, QVBoxLayout, QMenu, QMenuBar, QMainWindow, QAction, qApp, QApplication
import pandas as pd
from datetime import datetime
import xarray as xr 
import numpy as np  # import numpy as np
import traceback

def formatData(instance):

    try:
        # read in the input file
        #nc = netCDF4.Dataset(instance.input_file, mode='r')
        nc = xr.open_dataset(instance.input_file,decode_times=False)
        # create an empty pandas series to hold variables
        instance.variables_extract = pd.Series(dtype=str)
        # create empty dicts
        instance.asc = {}
        instance.units = {}
        instance.long_name = {}
        instance.variables = {}
        instance.fileheader = {}
        try:
            instance.tail_number = nc.attrs['Platform']
        except KeyError:
            instance.tail_number = nc.attrs['platform']
        if instance.tail_number == 'N677F':
            instance.platform = 'GV'
        elif instance.tail_number == 'N130AR':
            instance.platform = 'C130'
        instance.project_name = nc.attrs['project']
        instance.today = str(datetime.today().strftime('%Y, %m, %d'))
        instance.today = instance.today.replace('-', ', ')

        instance.parse_vars(nc)
        if instance.variables_extract.to_list():
            instance.dims = nc[instance.variables_extract.to_list()].dims
        # concatenate
        instance.asc = pd.concat(instance.asc, axis=1, ignore_index=False)
        instance.secofday = nc['Time'].values ##Save second of day
        # create an object to store the NetCDF variable time
        instance.dtime = nc.variables['Time']
        # use num2date to setup dtime object
        instance.dtime = xr.coding.times.decode_cf_datetime(nc['Time'], nc['Time'].attrs['units'])
        instance.dtime = pd.Series(instance.dtime).astype(str)
        instance.dtime_sep = instance.dtime.str.split(' ', expand=True)
        # create separate date and time series for combination in previewData and writeData
        instance.dtime_date = instance.dtime_sep[0]
        instance.dtime_time = instance.dtime_sep[1]
        # concatenate the units, long_name, variables, and header
        instance.units = pd.concat(instance.units, axis=0, ignore_index=True)
        instance.long_name = pd.concat(instance.long_name, axis=0, ignore_index=True)
        instance.variables = pd.concat(instance.variables, axis=0, ignore_index=True)
        instance.fileheader = pd.concat([instance.variables, instance.units, instance.long_name], axis=1, ignore_index=True)
        # subset the start and end time from the dtime objet by position
        instance.start_time = instance.dtime.iloc[0]
        instance.end_time = instance.dtime.iloc[-1]
        try:
            # populate the start_time and end_time fields in the gui
            instance.start.setText(instance.start_time)
            instance.end.setText(instance.end_time)
        except Exception:
            pass
        return instance.start_time, instance.end_time, instance.input_file, instance.units, instance.asc, instance.fileheader, instance.dtime_date, instance.dtime_time, instance.dtime
    except Exception:
        print(traceback.format_exc())
        print('Error in extracting variable in ' + str(instance.input_file))


def writeData(instance):

    #####################################################################
    # Get inputs from GUI or CL depending on mode
    #####################################################################
    try:
        instance.write = instance.asc_new
    except Exception:
        try:
            instance.write = instance.asc_new_batch
        except Exception:
            instance.write = instance.asc
    if instance.header == 'ICARTT':
        instance.write.insert(0, 'Time_Start', instance.secofday)
################################################################################################
    for columnName,columnData in instance.write.items():
            #print(columnName)
            try:
                instance.write[columnName] = columnData.map(lambda x: '%5f' % x)
            except Exception as e:
                pass
################################################################################################
    # determine which output file to use based on mode
    try: 
        instance.output_file = os.path.join(instance.outputdirbox.text(), instance.outputfilebox.text())
        start = instance.start.text()
        end = instance.end.text()
        instance.date = 'yyyy-mm-dd' if instance.date1.isChecked() else 'yyyy mm dd' if instance.date2.isChecked() else 'NoDate'
        instance.time = 'hh:mm:ss' if instance.time1.isChecked() else 'hh mm ss' if instance.time2.isChecked() else 'SecOfDay'
        instance.fillvalue = -32767 if instance.fillvalue1.isChecked() else 'Blank' if instance.fillvalue2.isChecked() else 'Replicate'
        instance.delimiter = 'comma' if instance.comma.isChecked() else 'space'
        instance.header = 'Plain' if instance.header1.isChecked() else 'ICARTT' if instance.header2.isChecked() else 'AMES'
        instance.time = 'hh:mm:ss' if instance.time1.isChecked() else 'hh mm ss' if instance.time2.isChecked() else 'SecOfDay'
        if instance.header == 'ICARTT':
            instance.date= 'NoDate'
            instance.time='SecOfDay'
    except:
        #not gui mode
        pass
    try:
        start = instance.start_time
        end = instance.end_time
        
    except Exception as e:
        instance._log_exception(e)
        
    try:
        os.remove(str(instance.output_file))
    except Exception:
        pass
    # try to get the start and end time from the gui then from the batchfile
    buttonReply = 'No'
    if exists(instance.output_file):
        try:
            buttonReply = QMessageBox.question(instance, 'Warning', "Output file already exists. Overwrite?", QMessageBox.Yes | QMessageBox.No)
        except Exception:
            pass
    if buttonReply == QMessageBox.No:
        print('No clicked. Exiting.')
        return
    
    print('Continuing...')
        # gui fields
        
    instance.averaging_window = getattr(instance, 'averagingbox', None)
    if instance.averaging_window:
        instance.averaging_window = instance.averaging_window.text()
    else:
        instance.averaging_window = instance.avg

    if instance.averaging_window:
        instance.averaging_window = int(instance.averaging_window)
        instance.write = instance.write.rolling(instance.averaging_window, min_periods=0).mean().round(decimals=0)
        instance.write = instance.write.iloc[::instance.averaging_window, :]
    #################################################################
    # Date and time combination checks for output file
    #################################################################
    instance.write =instance.process_date_time(instance.write) 
    if instance.header == 'Plain':
        PLAINHeader(instance,instance.write)
# Append the DataFrame content to the file
        try:
            instance.processingSuccess_GUI()
        except Exception as e:
            pass
    # ICARTT header
    elif instance.header == 'ICARTT':
        ICARTTHeader(instance,instance.write)
    # AMES header
    elif instance.header == 'AMES':
        try:
            # drop the unit and dimension rows for AMES
            instance.write.columns = instance.write.columns.droplevel(1)
            instance.write.columns = instance.write.columns.droplevel(1)
            instance.AMESHeader(instance.write)
        except Exception:
            print('AMES header was not created or appended to output file.')
        try:
            instance.processingSuccess_GUI()
            instance.deselectAll_GUI()
        except Exception as e:
            print(e)
    # try:
    #     processing_complete = QMessageBox()
    #     processing_complete.setWindowTitle("Error")
    #     processing_complete.setText("There was an error writing your ASCII file. Please try again.")
    #     x = processing_complete.exec_()
    # except Exception as e:
    #     print(e)
    #     print('Data was not written. Please try again.')

########HEADER FORMATTING #########
def PLAINHeader(instance, dataframe):
    na_rep = '-32767.0' if instance.fillvalue == '-32767' else ''
    na_fill = -32767.0 if na_rep== '-32767.0' else ''
    
    if instance.fillvalue == 'Replicate':
        dataframe = dataframe.fillna(method='ffill')
        na_rep = None
    # Drop levels until there is only one level left in the columns
    while isinstance(dataframe.columns, pd.MultiIndex):
        try:
            dataframe.columns = dataframe.columns.droplevel(1)
        except IndexError:
            break
    dataframe = add_fills(dataframe, na_fill)
    sep = ',' if instance.delimiter == 'comma' else ' '
    cellsizes_lines = []
    if instance.histo:
        for var in instance.cellsize_dict:
            print(var)
            cellsize_len=0
            if var in dataframe.columns:
                print(var)
                cellsizes_lines.append(f'{var} Cellsizes: {", ".join(map(str, instance.cellsize_dict[var].flatten()))}\n')
                cellsize_len+=1     
    # Write the Cellsizes information to the file
        with open(instance.output_file, 'w') as f:
            f.writelines(cellsizes_lines)
    dataframe.to_csv(instance.output_file, header=True, index=False, na_rep=na_rep, sep=sep)

    
def ICARTTHeader(instance, dataframe):

    instance.lib_path = str(os.path.abspath(os.path.dirname(__file__)))
    if instance.lib_path == '/opt/local/bin':
        try:
            instance.lib_path = instance.lib_path.replace("bin", "lib")
        except Exception as e:
            print(e)
            print(traceback.format_exc())
    else:
        try:
            if 'lib' not in instance.lib_path:
                instance.lib_path = str(instance.lib_path) + '/lib/'
        except Exception as e:
            print(e)
            print(traceback.format_exc())

    # Drop levels until there is only one level left in the columns
    while isinstance(dataframe.columns, pd.MultiIndex):
        try:
            dataframe.columns = dataframe.columns.droplevel(1)
        except IndexError:
            break

    # Rename the time var to Time_Start
    dataframe = dataframe.rename(columns={'Time': 'Time_Start', 'DateTime': 'Time_Start'})
    # Convert columns to float
    dataframe = add_fills(dataframe,-99999)
    dataframe.to_csv(instance.output_file, header=True, index=False)
    instance.varNumber = str(len(dataframe.columns) - 1)
    try:
        instance.data_date = str(instance.dtime_sep[0].iloc[1]).replace('-', ', ')
        os.system(f'cp {instance.lib_path}/header1.txt ./header1.tmp')
        os.system("ex -s -c '5i' -c x ./header1.tmp")
        os.system(f'cp {instance.lib_path}/header2.txt ./header2.tmp')
        instance.today = datetime.today().strftime('%Y, %m, %d')

        with open('./header1.tmp', 'r+') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if line.startswith('RAF instruments on'):
                    lines[i] = f'{line.strip()} {instance.platform}\n'
                if line.startswith('<PROJECT>'):
                    lines[i] = f'{instance.project_name}\n'
                if line.startswith('<YYYY, MM, DD,>'):
                    lines[i] = f'{instance.data_date}, {instance.today}\n'
                if line.startswith('<varNumber>'):
                    lines[i] = f'{instance.varNumber}\n'
                if line.startswith('<1.0>'):
                    lines[i] = '1.0,' * int(instance.varNumber)
                    lines[i] = lines[i].rstrip(',') + '\n'
                if line.startswith('<-99999.0>'):
                    print('Replacing fill values')
                    lines[i] = '-99999.0,' * int(instance.varNumber)
                    lines[i] = lines[i].rstrip(',') + '\n'
            f.seek(0)
            f.writelines(lines)

        with open('./header2.tmp', 'r+') as f:
            lines = f.readlines()
            cells_len=0
            if instance.histo:
                for var in instance.cellsize_dict:
                    cellsize_len=0
                    if var in dataframe.columns:
                        lines.insert(3, f'{var} Cellsizes: {", ".join(map(str, instance.cellsize_dict[var].flatten()))}\n')
                        cellsize_len+=1
                cells_len = cellsize_len
            for i, line in enumerate(lines):
                if line.startswith('18'):
                    lines[i] =str(cells_len+18) + '\n'
                if line.startswith('<PLATFORM>'):
                    lines[i] = f'PLATFORM: NSF/NCAR {instance.platform} {instance.tail_number}\n'
                if line.startswith('REVISION: RA'):
                    lines[i] = line.replace('RA', instance.version)
            f.seek(0)
            f.writelines(lines)

        instance.columns = pd.DataFrame(dataframe.columns.values.tolist())
        instance.fileheader = instance.fileheader.loc[instance.fileheader[0].isin(instance.columns[0])]
        ordered_fileheader = []
        for col in dataframe.columns:
            matching_rows = instance.fileheader[instance.fileheader[0] == col]
            if not matching_rows.empty:
                ordered_fileheader.append(matching_rows)
        if ordered_fileheader:
            instance.fileheader = pd.concat(ordered_fileheader, ignore_index=True)
        #instance.fileheader.to_csv('./header1.tmp', mode='a', header=False, index=False)
        csv_string = instance.fileheader.to_csv(header=False, index=False)

        # Append to file manually
        with open('./header1.tmp', 'a', newline='') as f:
            f.write(csv_string)
        os.system('cat ./header1.tmp ./header2.tmp > ./header.tmp')

        with open('./header.tmp', 'r+') as f:
            lines = f.readlines()
            #if there is a trailing line with just 'a' remove it
            if lines[-1].strip() == 'a':
                lines.pop(-1)
            count = f'{len(lines) + 1}, 1001'
            for i, line in enumerate(lines):
                if line.startswith('<ROWCOUNT>'):
                    lines[i] = f'{count}\n'
                f.seek(0)
                f.writelines(lines)
            
        instance.icartt_filename_date = instance.data_date.replace(', ', '')
        instance.icartt_filename = f'{instance.project_name}-CORE_{instance.platform}_{instance.icartt_filename_date}_{instance.version}.ict'
        print(f'Overwriting Output Filename, since ICARTT file has strict format: {instance.icartt_filename}')
        os.system(f'mv {instance.output_file} {instance.output_file}.tmp')
        #os.system(f'cat ./header.tmp {instance.output_file}.tmp >> {instance.output_file}')
        # Use Python file operations for more control
        with open(instance.output_file, 'w') as outfile:
            # Copy header
            with open('./header.tmp', 'r') as header_file:
                header_content = header_file.read()
                # Remove any trailing 'a' lines
                header_lines = header_content.split('\n')
                header_lines = [line for line in header_lines if line.strip() != 'a']
                outfile.write('\n'.join(header_lines))
                if header_lines and header_lines[-1].strip():  # Add newline if needed
                    outfile.write('\n')
            
            # Copy data
            with open(f'{instance.output_file}.tmp', 'r') as data_file:
                outfile.write(data_file.read())
        os.system(f'mv {instance.output_file} {os.path.abspath(os.path.dirname(instance.output_file))}/{instance.icartt_filename}')
        os.system(f'rm header.tmp header1.tmp header2.tmp {instance.output_file}.tmp')
    except Exception:
        print(traceback.format_exc())
        print('ICARTT header was not created or appended to output file')

    try:
        instance.processingSuccess_GUI()
    except Exception:
        print('Processing complete')
    
#########################################################################
# Define function to format AMES header
########################################################################
def AMESHeader(instance, ames_header):

    # try renaming the time var to Start_UTC
    try:
        ames_header = pd.DataFrame(ames_header.rename(columns={'Time': 'UTs'}))
    except Exception:
        pass
    # get the varNumber from the # of columns in the dataframe
    instance.varNumber = str(len(ames_header.columns)-1)
    ames_header.to_csv(instance.output_file, header=True, index=False, na_rep='99999')
    lib_path = str(os.path.abspath(os.path.dirname(__file__)))
    try:
        lib_path = lib_path.replace("bin", "lib")
    except Exception:
        try:
            lib_path = './lib'
        except Exception as e:
            print(e)
    try:
        instance.columns = pd.DataFrame(ames_header.columns.values.tolist())
        instance.fileheader = instance.fileheader.loc[instance.fileheader[0].isin(instance.columns[0])]
        instance.data_date = str(instance.dtime_sep[0].iloc[1])
        instance.data_date = instance.data_date.replace('-', ', ')
        # start going through the template text docs
        os.system('cp ' + lib_path + '/header1_ames.txt ' + lib_path + '/header1_ames.tmp')
        os.system("ex -s -c '5i' -c x " + lib_path + "/header1_ames.tmp")
        os.system('cp ' + lib_path + '/header2_ames.txt ' + lib_path + '/header2_ames.tmp')
        # get today's date
        instance.today = datetime.today().strftime('%Y, %m, %d')
        # perform the replacements on the first header file
        with open(lib_path + '/header1_ames.tmp', 'r+') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if line.startswith('Flight data from:'):
                    lines[i] = lines[i].strip() + ' ' + instance.platform + '\n'
                if line.startswith('<PROJECT>'):
                    lines[i] = instance.project_name + '\n'
                if line.startswith('<YYYY, MM, DD,>'):
                    lines[i] = instance.data_date+', ' + instance.today + '\n'
                if line.startswith('<varNumber>'):
                    lines[i] = instance.varNumber + '\n'
                if line.startswith('<0.1>'):
                    lines[i] = '0.1,' * int(instance.varNumber) + '\n'
                    lines[i] = lines[i][:-2] + '\n'
                if line.startswith('<9999>'):
                    lines[i] = '9999,' * int(instance.varNumber) + '\n'
                    lines[i] = lines[i][:-2] + '\n'
            f.seek(0)
            for line in lines:
                f.write(line)
        # combine and perform replacement on the combined header file
        instance.fileheader.to_csv(lib_path + '/header1_ames.tmp', header=False, index=False)
        os.system('cat ' + lib_path + '/header1_ames.tmp ' + lib_path + '/header2_ames.tmp > ' + lib_path + '/header_ames.tmp')
        with open(lib_path + '/header_ames.tmp', 'r+') as f:
            lines = f.readlines()
            count = str(len(lines))+', 1001'
            for i, line in enumerate(lines):
                if line.startswith('<ROWCOUNT>'):
                    lines[i] = count+'\n'
            f.seek(0)
            for line in lines:
                f.write(line)
        os.system('mv ' + str(instance.output_file) + ' ' + str(instance.output_file) + '.tmp')
        os.system('cat ' + lib_path + '/header_ames.tmp ' + str(instance.output_file) + '.tmp >> ' + str(instance.output_file))
        os.system('rm ' + lib_path + '/header_ames.tmp ' + lib_path + '/header1_ames.tmp ' + lib_path + '/header2_ames.tmp ' + str(instance.output_file) + '.tmp')
    except Exception:
        print('AMES header not created or appended to output file.')

def add_fills(dataframe, fill):
    ''''Make sure that the dataframe has the correct fill values'''
    for column in dataframe.columns:
        try:
            dataframe[column] = dataframe[column].astype(float)
            dataframe[column] = dataframe[column].where(np.isfinite(dataframe[column]), fill)
        except Exception:
            if column == 'Time_Start' or column == 'Date':
                pass
            else:
                print(f'Could not convert {column} to float')
                pass  
    
    return dataframe.replace(np.nan, fill)  