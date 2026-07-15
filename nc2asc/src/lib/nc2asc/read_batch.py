##WRITING BATCHFILE##
import os 
from os.path import exists
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMessageBox, QFileDialog

def saveBatchFile_GUI(instance):

    # check to ensure the user has already loaded a NetCDF
    if len(instance.inputfilebox.text()) == 0:
        no_savebatch = QMessageBox()
        # if no NetCDF loaded, display error message
        no_savebatch.setWindowTitle('Error')
        no_savebatch.setText('Cannot Save Batchfile, Need Input File!')
        x = no_savebatch.exec_()
    else:
        buttonReply = 'No'
        if exists(str(instance.head) + '/batchfile'):
            buttonReply = QMessageBox.question(instance, 'Warning', "Batch file already exists. Overwrite?", QMessageBox.Yes | QMessageBox.No)
        else:
            pass
        if buttonReply == QMessageBox.No:
            print('buttonReply == QMessageBox.No')
        else:
            try:
                # if NetCDF file has been loaded start creating batch file
                instance.batchfile = str(instance.outputdirbox.text()) + '/batchfile'
                os.system('touch ' + instance.batchfile)
                instance.batchfile = open(instance.batchfile, "w")

                # get the output directory and filename from the gui
                instance.batchfile.write('if=' + instance.input_file + '\n')
                instance.batchfile.write('of=' + str(instance.outputdirbox.text()) + '/' + str(instance.outputfilebox.text()) + '\n\n')

                # determine the settings from the gui to inlude in the batch file
                # check which header to include in the batch file
                if instance.header1.isChecked():
                    instance.batchfile.write('hd=Plain\n')
                elif instance.header2.isChecked():
                    instance.batchfile.write('hd=ICARTT\n')
                elif instance.header3.isChecked():
                    instance.batchfile.write('hd=AMES\n')

                # determine averaing to write to the batch file
                averagingbox_text = str(instance.averagingbox.text())
                instance.batchfile.write('avg='+averagingbox_text+'\n')

                # determine date format to write to the batch file
                if instance.date1.isChecked():
                    instance.batchfile.write('dt=yyyy-mm-dd\n')
                elif instance.date2.isChecked():
                    instance.batchfile.write('dt=yyyy mm dd\n')
                elif instance.date3.isChecked():
                    instance.batchfile.write('dt=NoDate\n')

                # determine time format to write to the batch file
                if instance.time1.isChecked():
                    instance.batchfile.write('tm=hh:mm:ss\n')
                elif instance.time2.isChecked():
                    instance.batchfile.write('tm=hh mm ss\n')
                elif instance.time3.isChecked():
                    instance.batchfile.write('tm=SecOfDay\n')

                # determine delimieter to write to the batch file
                if instance.comma.isChecked():
                    instance.batchfile.write('sp=comma\n')
                elif instance.space.isChecked():
                    instance.batchfile.write('sp=space\n')

                # determine the fillvalue to write to the batch file
                if instance.fillvalue1.isChecked():
                    instance.batchfile.write('fv=-32767\n')
                elif instance.fillvalue2.isChecked():
                    instance.batchfile.write('fv=blank\n')
                elif instance.fillvalue3.isChecked():
                    instance.batchfile.write('fv=replicate\n')

                # determine the time interval to write to the batch file
                # by default the instance.start/end.text() method will return the full file
                instance.batchfile.write('ti=X,X\n')

                # in order to display vars on separate lines to align with
                # nimbus batch file conventions, split by two spaces
                for i in instance.variables_extract:
                    try:
                        instance.batchfile.write('Vars=' + i + '\n')
                    except Exception:
                        pass
                instance.batchfile.close

                # notify user that batch file has been written
                savebatch = QMessageBox()
                savebatch.setWindowTitle("Success!")
                savebatch.setText("Batch File Successfully Created! Close program and check output directory")
                x = savebatch.exec_()
            except Exception as e:
                print(e)
                    



##READING BATCHFILE##
def process_batch_file(instance, inputbatch_file):
    """Processes a batch file to extract settings and variables."""
    action_map = {
        'if=': lambda ln: _handle_file(instance,ln, 'input_file', 'Input'),
        'of=': lambda ln: _handle_file(instance,ln, 'output_file', 'Output'),
        'hd=': lambda ln: _handle_directive(instance,ln, 'header', _header_map()),
        'dt=': lambda ln: _handle_directive(instance,ln, 'date', _date_map()),
        'tm=': lambda ln: _handle_directive(instance,ln, 'time', _time_map()),
        'sp=': lambda ln: _handle_directive(instance,ln, 'delimiter', _delimiter_map()),
        'fv=': lambda ln: _handle_directive(instance,ln, 'fillvalue', _fillvalue_map()),
        'version=': lambda ln: setattr(instance, 'version', ln.replace('version=', '').strip()),
        'ti=': lambda ln: setattr(instance, 'ti', ln[3:].strip()),
        'avg=': lambda ln: setattr(instance, 'avg', _format_avg(ln[4:])),
        'Vars=': lambda ln: _add_variable(instance,ln),
    }
    
    with open(inputbatch_file, 'r') as fil:
        print('****Reading Batch File****')
        for ln in fil:
            ln = ln.strip()
            for key, action in action_map.items():
                if ln.startswith(key):
                    action(ln)
                    break
        print('Batch file processing complete.')
        
def readBatchFile(instance):

    # try to get batch file from the gui prompt if in gui mode
    try:
        instance.inputbatch_file = instance.inputbatch_file
    except Exception:
        try:
            instance.inputbatch_file, _ = QFileDialog.getOpenFileName(instance, "Select a Batch file to Read", "/scr/raf_data", "filter = *")
        except Exception:
            pass
    try:
        instance.process_batch_file(instance.inputbatch_file)

            # update the gui fields
        try:
            instance.inputfilebox.setText(instance.input_file)
            instance.outputdirbox.setText(os.path.dirname(instance.output_file) + '/')
            instance.outputfilebox.setText(os.path.basename(instance.output_file))
            instance.start.setText(str(instance.start_time))
            instance.end.setText(str(instance.end_time))
            instance.averagingbox.setText(instance.avg)
        except Exception:
            pass

        # get data from input file field and format
        try:
            instance.input_file = instance.inputfilebox.text()
        except Exception:
            instance.input_file = instance.input_file
        instance.batchfile_read = True
        try:
            
            instance.formatData()
            instance.asc_new_batch = instance.asc[instance.variables_extract_batch]
            instance.asc_new =instance.asc_new_batch
        except Exception as e:
            instance._log_exception(e)
            pass
        try:
            instance.loadVars_GUI()
        except Exception as e:
            instance._log_exception(e)
            pass

        try:
            for i in range(0, instance.row_count):
                for j in instance.asc_new_batch:
                    if j[0] == instance.var.item(i, 0).text():
                        print('success')
                        instance.var.item(i, 0).text()
                        instance.var.item(i, 0).setBackground(QtGui.QColor(255, 0, 255))
                    else:
                        pass
        except Exception as e:
            instance._log_exception(e)
        try:
            instance.previewData_GUI()
        except Exception as e :
            instance._log_exception(e)
            pass
    except Exception as e:
        instance._log_exception(e)
        pass


def _header_map():
    return {
        'hd=Plain': ('header1', 'Plain'),
        'hd=ICARTT': ('header2', 'ICARTT'),
        'hd=AMES': ('header3', 'AMES'),
    }

def _date_map():
    return {
        'dt=yyyy-mm-dd': ('date1', 'yyyy-mm-dd'),
        'dt=yyyy mm dd': ('date2', 'yyyy mm dd'),
        'dt=NoDate': ('date3', 'NoDate'),
    }

def _time_map():
    return {
        'tm=hh:mm:ss': ('time1', 'hh:mm:ss'),
        'tm=hh mm ss': ('time2', 'hh mm ss'),
        'tm=SecOfDay': ('time3', 'SecOfDay'),
    }

def _delimiter_map():
    return {
        'sp=comma': ('comma', 'comma'),
        'sp=space': ('space', 'space'),
    }

def _fillvalue_map():
    return {
        'fv=-32767': ('fillvalue1', '-32767'),
        'fv=blank': ('fillvalue2', 'blank'),
        'fv=replicate': ('fillvalue3', 'replicate'),
    }

def _handle_file(instance, line, attr_name, file_type):
    """Prompt user to confirm file selection from batch file or use command line input."""
    batch_file_value = line.split('=')[1].strip() # extract file path from batch file line
    current_value = getattr(instance, attr_name, None)

    if not current_value:
        print(f'No {file_type} file provided.')
        setattr(instance, attr_name, batch_file_value) 
        ## print attr to make sure it's set
    else:
        choice = input(
            f"Would you like to use the {file_type.lower()} file from the batch file? (y/Y to confirm, any other key to keep current): "
        )
        if choice.lower() == 'y':
            setattr(instance, attr_name, batch_file_value)
        else:
            print(f"Using {file_type.lower()} file from command line: {current_value}")


def _handle_directive(instance, line, attr_name, directive_map):
    """Set an attribute and toggle GUI checkbox based on a line and a directive map."""
    if line in directive_map:
        gui_attr, value = directive_map[line]
        try:
            getattr(instance, gui_attr).setChecked(True) ##TODO check this
            setattr(instance, attr_name, value)
        except AttributeError:
            setattr(instance, attr_name, value)

def _add_variable(instance, line):
    """Extract and add variables from a batch file line."""
    variable = line.replace('Vars=', '').replace("'", "").replace('[', '').replace(']', '').strip()
    if variable not in instance.variables_extract_batch:
        instance.variables_extract_batch.append(variable)

def _format_avg(avg):
    """Format the averaging value from the batch file."""
    return avg.translate({ord(c): None for c in "[]='g"}).strip()[:-1]

