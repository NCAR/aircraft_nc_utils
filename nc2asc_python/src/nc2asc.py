#! /usr/bin/env python3

#######################################################################
# Python based netCDF to ASCII converter with GUI
#
# Copyright University Corporation for Atmospheric Research (2021)
#######################################################################

import os
import sys
import argparse
import netCDF4
import pandas as pd
import numpy as np
from datetime import datetime
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QFrame, QScrollBar, QToolBar, QMessageBox, QFileDialog, QTableWidgetItem, QVBoxLayout, QMenu, QMenuBar, QMainWindow, QAction, qApp, QApplication

class gui(QMainWindow):
    def __init__(self):

        super(gui, self).__init__() 

        self.initUI()

    #########################################################################
    # Define layout of gui
    # Set up the fields, table, buttons, and menu
    #########################################################################
    def initUI(self):               

        # bold font to help with organization of processing options
        myFont=QtGui.QFont()
        myFont.setBold(True)

        #####################################################################
        # Input file and output dir / file fields
        #####################################################################
        # define input file box and label 
        inputoptionslabel = QtWidgets.QLabel(self)
        inputoptionslabel.setText('Input Options:')
        inputoptionslabel.move(20, 20)
        inputoptionslabel.setFont(myFont)
        self.inputfilebox=QtWidgets.QLineEdit(self)
        self.inputfilebox.move(140, 40)
        self.inputfilebox.resize(350, 20)
        inputlabel=QtWidgets.QLabel(self)
        inputlabel.setText('Input File')
        inputlabel.move(75, 40) 
        # define output dir and file
        # output dir 
        outputdirlabel=QtWidgets.QLabel(self)
        outputdirlabel.setText('Output Directory')
        outputdirlabel.move(30, 70)
        self.outputdirbox=QtWidgets.QLineEdit(self)
        self.outputdirbox.move(140, 70)
        self.outputdirbox.resize(350, 20)
        # output file
        outputlabel=QtWidgets.QLabel(self)
        outputlabel.setText('Output Filename:')
        outputlabel.move(30, 100)        
        self.outputfilebox=QtWidgets.QLineEdit(self)
        self.outputfilebox.move(140, 100)
        self.outputfilebox.resize(175, 20)

        #####################################################################
        # Start time, end time, and averaging options
        #####################################################################
        # fields for start and end time
        timeselectionlabel = QtWidgets.QLabel(self)
        timeselectionlabel.setText('Time Options:')
        timeselectionlabel.move(20, 140)
        startlab = QtWidgets.QLabel(self)
        startlab.setText('Start:')
        endlab = QtWidgets.QLabel(self)
        endlab.setText('End:')
        startlab.move(100,160)
        endlab.move(100,180)
        self.start=QtWidgets.QLineEdit(self)
        self.end=QtWidgets.QLineEdit(self)
        self.start.move(140, 165)
        self.start.resize(140, 20)
        self.end.move(140, 185)
        self.end.resize(140, 20)
        # averaging label and box
        averaginglabel=QtWidgets.QLabel(self)
        averaginglabel.setText('Averaging (s):')
        averaginglabel.move(100, 200)
        averagingnote=QtWidgets.QLabel(self)
        averagingnote.move(280, 200)
        averagingnote.resize(300, 20)
        self.averagingbox = QtWidgets.QLineEdit(self)
        self.averagingbox.move(220, 205)
        self.averagingbox.resize(60, 20)
        # button to update preview based on time options
        self.outputpreviewbutton=QtWidgets.QPushButton('Update Preview', self)
        self.outputpreviewbutton.move(300, 200)
        self.outputpreviewbutton.clicked.connect(self.selectVars_GUI)

        #####################################################################
        # Processing options section
        #####################################################################
        processinglabel = QtWidgets.QLabel(self)
        processinglabel.setText('Output Options:')
        processinglabel.move(20, 240)
        processinglabel.resize(100, 20)
        processinglabel.setFont(myFont)

        #####################################################################
        # Date format options
        #####################################################################
        # radio buttons for date
        dateformatlabel = QtWidgets.QLabel(self)
        dateformatlabel.setText('Date Format:')
        dateformatlabel.move(20, 260)
        dateformatlabel.setFont(myFont)
        self.date1=QtWidgets.QRadioButton(self)
        self.date1.setText('yyyy-mm-dd')
        self.date1.move(20, 280)
        self.date2=QtWidgets.QRadioButton(self)
        self.date2.setText('yyyy mm dd')
        self.date2.move(20, 300)
        self.date3=QtWidgets.QRadioButton(self)
        self.date3.setText('NoDate')
        self.date3.move(20, 320)
        dategroup = QtWidgets.QButtonGroup(self)
        dategroup.addButton(self.date1)
        dategroup.addButton(self.date2)
        dategroup.addButton(self.date3)
        # have the default be date 1 but update the preview when any are clicked
        self.date1.setChecked(True)
        self.date1.clicked.connect(self.selectVars_GUI)
        self.date2.clicked.connect(self.selectVars_GUI)
        self.date3.clicked.connect(self.selectVars_GUI)

        #####################################################################
        # Time format options
        #####################################################################
        # radio buttons for time
        timeformatlabel = QtWidgets.QLabel(self)
        timeformatlabel.setText('Time Format:')
        timeformatlabel.move(200, 260)
        timeformatlabel.setFont(myFont)
        self.time1=QtWidgets.QRadioButton(self)
        self.time1.setText('hh:mm:ss')
        self.time1.move(200, 280)
        self.time2=QtWidgets.QRadioButton(self)
        self.time2.setText('hh mm ss')
        self.time2.move(200, 300)
        self.time3=QtWidgets.QRadioButton(self)
        self.time3.setText('SecOfDay')
        self.time3.move(200, 320)
        timegroup = QtWidgets.QButtonGroup(self)
        timegroup.addButton(self.time1)
        timegroup.addButton(self.time2)
        timegroup.addButton(self.time3)
        # have default be time 1 but update the preview when any are clicked
        self.time1.setChecked(True)
        self.time1.clicked.connect(self.selectVars_GUI)
        self.time2.clicked.connect(self.selectVars_GUI)
        self.time3.clicked.connect(self.selectVars_GUI)

        #####################################################################
        # Delimiter format options
        #####################################################################
        # radio buttons for the delimiter
        delimiterlabel = QtWidgets.QLabel(self)
        delimiterlabel.setText('Delimiter:')
        delimiterlabel.move(380, 260)
        delimiterlabel.setFont(myFont)
        self.comma = QtWidgets.QRadioButton(self)
        self.comma.setText('Comma')
        self.comma.move(380, 280)
        self.space = QtWidgets.QRadioButton(self)
        self.space.setText('Space')
        self.space.move(380, 300)
        delimitergroup = QtWidgets.QButtonGroup(self)
        delimitergroup.addButton(self.comma)
        delimitergroup.addButton(self.space)
        # have default be comma delimited but update the preview when any are clicked
        self.comma.setChecked(True)        
        self.comma.clicked.connect(self.selectVars_GUI)
        self.space.clicked.connect(self.selectVars_GUI)

        #####################################################################
        # Fill value format options
        ####################################################################
        # radio buttons for the fill value
        fillvaluelabel = QtWidgets.QLabel(self)
        fillvaluelabel.setText('Fill Value:')
        fillvaluelabel.move(20, 360)
        fillvaluelabel.setFont(myFont)
        self.fillvalue1=QtWidgets.QRadioButton(self)
        self.fillvalue1.setText('-32767.0')
        self.fillvalue1.move(20, 380)
        self.fillvalue2=QtWidgets.QRadioButton(self)
        self.fillvalue2.setText('Blank')
        self.fillvalue2.move(20, 400)
        self.fillvalue3=QtWidgets.QRadioButton(self)
        self.fillvalue3.setText('Replicate')
        self.fillvalue3.move(20, 420)
        fillvaluegroup = QtWidgets.QButtonGroup(self)
        fillvaluegroup.addButton(self.fillvalue1)
        fillvaluegroup.addButton(self.fillvalue2)
        fillvaluegroup.addButton(self.fillvalue3)
        # have default be fill value 1 but update the preview when any are clicked
        self.fillvalue1.setChecked(True)
        self.fillvalue1.clicked.connect(self.selectVars_GUI)
        self.fillvalue2.clicked.connect(self.selectVars_GUI)
        self.fillvalue3.clicked.connect(self.selectVars_GUI)

        #####################################################################
        # Header format options
        #####################################################################
        # radio buttons for header
        headerformatlabel = QtWidgets.QLabel(self)
        headerformatlabel.setText('Header:')
        headerformatlabel.move(200, 360)
        headerformatlabel.setFont(myFont)
        self.header1 = QtWidgets.QRadioButton(self)
        self.header1.setText('Plain')
        self.header1.move(200, 380)
        self.header2 = QtWidgets.QRadioButton(self)
        self.header2.setText('ICARTT')
        self.header2.move(200, 400)
        self.header3 = QtWidgets.QRadioButton(self)
        self.header3.setText('AMES DEF')
        self.header3.move(200, 420)
        headergroup = QtWidgets.QButtonGroup(self)
        headergroup.addButton(self.header1)
        headergroup.addButton(self.header2)
        headergroup.addButton(self.header3)
        # have the default be header 1 (plain) but update the preview when any are clicked
        self.header1.setChecked(True)
        self.header2.clicked.connect(self.ICARTT_AMES_toggle_GUI)
        self.header1.clicked.connect(self.selectVars_GUI)
        self.header2.clicked.connect(self.selectVars_GUI)
        self.header3.clicked.connect(self.ICARTT_AMES_toggle_GUI)
        self.header3.clicked.connect(self.selectVars_GUI)
        # process button calls writeData function
        self.processbtn=QtWidgets.QPushButton('Convert File', self)
        self.processbtn.resize(self.processbtn.sizeHint())
        self.processbtn.move(20, 670)
        self.processbtn.clicked.connect(self.writeData)

        #####################################################################
        # Variable table and selection / deselection options
        #####################################################################
        # button to select all variables
        self.varbtn=QtWidgets.QPushButton('Select All', self)
        self.varbtn.move(600, 30)
        self.varbtn.clicked.connect(self.loadVars_GUI)
        self.varbtn.clicked.connect(self.selectAll_GUI)
        # button to de-select all variables
        self.varbtn2=QtWidgets.QPushButton('Clear All', self)
        self.varbtn2.move(700, 30)
        self.varbtn2.clicked.connect(self.loadVars_GUI)
        self.varbtn2.clicked.connect(self.deselectAll_GUI)
        # button to remove current variable
        self.deselectvar=QtWidgets.QPushButton('Remove Var', self)
        self.deselectvar.move (800, 30)
        self.deselectvar.clicked.connect(self.deselectVar_GUI)
        # variable table and buttons with labels
        varlabel=QtWidgets.QLabel(self)
        varlabel.setText('Click Vars:')
        varlabel.move(500, 30)
        varlabel.setFont(myFont)
        self.var=QtWidgets.QTableWidget(self)
        self.var.setColumnCount(3)
        self.var.setColumnWidth(2, 150)
        self.var.setRowCount(15)
        self.var.move(500, 60)
        self.var.resize(400, 430)
        self.var.setHorizontalHeaderLabels(['Var', 'Units', 'Long Name']) 
        self.var.clicked.connect(self.selectVars_GUI)
     
        ##################################################################### 
        # Output preview options
        #####################################################################
        # output preview label
        outputpreviewlabel=QtWidgets.QLabel(self)
        outputpreviewlabel.move(20, 470)
        outputpreviewlabel.setText('Preview:')
        outputpreviewlabel.setFont(myFont)
        # output preview field with horizontal scroll bar
        self.outputpreview=QtWidgets.QTextEdit(self)
        self.outputpreview.move(20, 500)
        self.outputpreview.resize(880, 150)
        self.outputpreview.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)

        #####################################################################
        # Menu options
        #####################################################################
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        helpMenu = mainMenu.addMenu('Help')
        importFile = QAction('Open NetCDF File', self)
        saveBatchFile = QAction('Save Batch File', self)
        readBatchFile = QAction('Read Batch File', self)
        exit = QAction('Exit', self)
        fileMenu.addAction(importFile)
        fileMenu.addAction(saveBatchFile)
        fileMenu.addAction(readBatchFile)
        fileMenu.addAction(exit)
        # connect the menu option File > Import NetCDF File to the data functions
        importFile.triggered.connect(self.loadData_GUI)
        importFile.triggered.connect(self.formatData)
        importFile.triggered.connect(self.loadVars_GUI)
        # connect the menu option File > Read Batch file to the function
        readBatchFile.triggered.connect(self.readBatchFile)
        # connect the exit menu option to the close function
        exit.triggered.connect(self.close)
        # connect the save batch file menu option to the function
        saveBatchFile.triggered.connect(self.saveBatchFile_GUI)

        #####################################################################
        # General setup options
        #####################################################################
        # changing the background color to gray
        self.setWindowIcon(QIcon('raf.png'))
        self.setStyleSheet("background-color: light gray;")
        self.setGeometry(100, 100, 920, 700)
        self.setWindowTitle('NCAR/EOL RAF Aircraft NetCDF to ASCII File Converter')    
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)
        self.show()

    #########################################################################
    # Function definitions for batch file saving and reading
    #########################################################################
    def saveBatchFile_GUI(self):

        # check to ensure the user has already loaded a NetCDF
        if len(self.inputfilebox.text()) == 0:
            no_savebatch = QMessageBox()
            # if no NetCDF loaded, display error message
            no_savebatch.setWindowTitle("Error")
            no_savebatch.setText("Cannot Save Batchfile, Need Input File!")
            x = no_savebatch.exec_()
        else:
            try:
                # if NetCDF file has been loaded start creating batch file
                self.batchfile = str(self.head)+'/batchfile'
                os.system('touch '+ self.batchfile)
                self.batchfile = open(self.batchfile,"w") 
                self.batchfile.write('if='+self.input_file+'\n')
                self.batchfile.write('of='+self.head+'/'+self.tail+'\n\n')
                # determine the settings from the gui to inlude in the batch file
                # check which header to include in the batch file
                if self.header1.isChecked() == True:
                    self.batchfile.write('hd=Plain\n') 
                elif self.header2.isChecked() == True:
                    self.batchfile.write('hd=ICARTT\n')
                elif self.header3.isChecked() == True:
                    self.batchfile.write('hd=AMES\n')
                # determine averaing to write to the batch file
                averagingbox_text = str(self.averagingbox.text()) 
                self.batchfile.write('avg='+averagingbox_text+'\n')
                # determine date format to write to the batch file
                if self.date1.isChecked() == True:
                    self.batchfile.write('dt=yyyy-mm-dd\n')
                elif self.date2.isChecked() == True:
                    self.batchfile.write('dt=yyyy mm dd\n')
                elif self.date3.isChecked() == True:
                    self.batchfile.write('dt=NoDate\n')
                # determine time format to write to the batch file
                if self.time1.isChecked() == True:
                    self.batchfile.write('tm=hh:mm:ss\n')
                elif self.time2.isChecked() == True:
                    self.batchfile.write('tm=hh mm ss\n')
                elif slef.time3.isChecked() == True:
                    self.batchfile.write('tm=SecOfDay\n')
                # determine delimieter to write to the batch file
                if self.comma.isChecked() == True:
                    self.batchfile.write('sp=comma\n')
                elif self.space.isChecked() == True:
                    self.batchfile.write('sp=space\n')
                # determine the fillvalue to write to the batch file
                if self.fillvalue1.isChecked() == True:
                    self.batchfile.write('fv=-32767\n')
                elif self.fillvalue2.isChecked() == True:
                    self.batchfile.write('fv=blank\n')
                elif self.fillvalue3.isChecked() == True:
                    self.batchfile.write('fv=replicate\n')
                # determine the time interval to write to the batch file
                # by default the self.start/end.text() method will return the full file
                self.batchfile.write('ti='+self.start.text()+','+self.end.text()+'\n\n')
                # in order to display vars on separate lines to align with 
                # nimbus batch file conventions, split by two spaces
                for i in self.var_selected.split(' '):
                    try:
                        self.batchfile.write('Vars='+i+'\n')
                    except:
                        pass
                self.batchfile.close
                # notify user that batch file has been written
                savebatch = QMessageBox()
                savebatch.setWindowTitle("Success!")
                savebatch.setText("Batch File Successfully Created! Close program and check output directory")
                x = savebatch.exec_()
            except:
                # if there is an error, notify user on command line
                print("Error writing batchfile.")

    def readBatchFile(self):

        # try to get batch file from the gui prompt if in gui mode
        try:
            self.inputbatch_file = self.inputbatch_file
        except:
            self.inputbatch_file, _ = QFileDialog.getOpenFileName(self,"Select a Batch file to Read", "/scr/raf_data","filter = *")
            # notify user that batch file has been read
            readbatch = QMessageBox()
            readbatch.setWindowTitle("Success!")
            readbatch.setText("Batch file successfully imported!")
            x = readbatch.exec_()
        with open(self.inputbatch_file, 'r') as fil:
            # create empty placeholders for objects
            self.input_file = []
            self.output_file = []
            self.variables_extract_batch = []
            # step through batchfile to find relevant information and assign
            # to be used to populate fields (GUI) and format and convert data
            for ln in fil:
                # extract the path of the input file from the batch file
                if ln.startswith('if='):
                    self.input_file.append(ln[2:])
                # extract the path of the output file
                elif ln.startswith('of='):
                    self.output_file.append(ln[2:])
                # get the header format from the batch file
                elif ln.startswith('hd=Plain'):
                    try:
                        self.header1.setChecked(True)
                    except:
                        self.header = 'Plain'
                elif ln.startswith('hd=ICARTT'):
                    try:
                        self.header2.setChecked(True)
                    except:
                        self.header = 'ICARTT'
                elif ln.startswith('hd=AMES'):
                    try:
                        self.header3.setChecked(True)
                    except:
                        self.header = 'AMES'
                # get the date format from the batch file
                elif ln.startswith('dt=yyyy-mm-dd'):
                    try:
                        self.date1.setChecked(True)
                    except:
                        self.date = 'yyyy-mm-dd'
                elif ln.startswith('dt=yyyy mm dd'):
                    try:
                        self.date2.setChecked(True)
                    except:
                        self.date = 'yyyy mm dd'
                elif ln.startswith('dt=NoDate'):
                    try:
                        self.date3.setChecked(True)
                    except:
                        self.date = 'NoDate'
                # get the time format from the batch file
                elif ln.startswith('tm=hh:mm:ss'):
                    try:
                        self.time1.setChecked(True)
                    except:
                        self.time = 'hh:mm:ss'
                elif ln.startswith('tm=hh mm ss'):
                    try:
                        self.time2.setChecked(True)
                    except:
                        self.time = 'hh mm ss'
                elif ln.startswith('tm=SecOfDay'):
                    try:
                        self.time3.setChecked(True)
                    except:
                        self.time = 'SecOfDay'
                # get the delimiter from the batch faile
                elif ln.startswith('sp=comma'):
                    try:
                        self.comma.setChecked(True)
                    except:
                        self.delimiter = 'comma'
                elif ln.startswith('sp=space'):
                    try:
                        self.space.setChecked(True)
                    except:
                        self.delimiter = 'space'
                # get the fill value from the batch file
                elif ln.startswith('fv=-32767'):
                    try:
                        self.fillvalue1.setChecked(True)
                    except:
                        self.fillvalue = '-32767'
                elif ln.startswith('fv=blank'):
                     try:
                         self.fillvalue2.setChecked(True)
                     except:
                         self.fillvalue = 'blank'
                elif ln.startswith('fv=replicate'):
                    try:
                        self.fillvalue3.setChecked(True)
                    except:
                        self.fillvalue = 'replicate'
                # get the time interval from the batch file
                elif ln.startswith('ti='):
                    self.ti = ln[2:]
                # get the average value (if provided) from the bath file
                elif ln.startswith('avg='):
                    self.avg = ln[2:]
                elif ln.startswith('Vars='):
                    var_batchfile = str(ln)
                    if var_batchfile not in self.variables_extract_batch:
                        self.variables_extract_batch.append(var_batchfile.replace('Vars=', '').replace('\n', '').replace("'", '').replace('[', '').replace(']', ''))
            # cleanup the extracted text from the batch file
            # format the input file
            self.input_file = str(self.input_file)
            self.input_file = self.input_file.replace('[', '')
            self.input_file = self.input_file.replace("'", '')
            self.input_file = self.input_file.replace('=', '')
            self.input_file = self.input_file.replace(']', '')
            self.input_file = self.input_file[:-2]
            # format the output dir and file
            self.output_file = str(self.output_file)
            self.output_file = self.output_file.replace('[', '')
            self.output_file = self.output_file.replace("'", '')
            self.output_file = self.output_file.replace('=', '')
            self.output_file = self.output_file.replace(']', '')
            self.output_file = self.output_file[:-2]
            # format the start and end time
            self.ti = self.ti.replace('[', '')
            self.ti = self.ti.replace("'", '')
            self.ti = self.ti.replace('=', '')
            self.ti = self.ti.replace(']', '')
            self.ti = self.ti[:-1]
            self.ti = self.ti.split(',')
            self.start_time = self.ti[0]
            self.end_time = self.ti[1]
            # format averaging
            self.avg = self.avg.replace('[', '')
            self.avg = self.avg.replace("'", '')
            self.avg = self.avg.replace('=', '')
            self.avg = self.avg.replace(']', '')
            self.avg = self.avg.replace('g', '')
            self.avg = self.avg[:-1]
            # update the gui fields
            try:
                self.inputfilebox.setText(self.input_file)
                self.outputdirbox.setText(os.path.dirname(self.output_file))
                self.outputfilebox.setText(os.path.basename(self.output_file))
                self.start.setText(str(self.start_time))
                self.end.setText(str(self.end_time))
                self.averagingbox.setText(self.avg)
            except:
                print('Not in GUI mode.')
        # get data from input file field and format
        try:
            self.input_file = self.inputfilebox.text()
        except:
            self.input_file = self.input_file
        self.variables_extract_batch = pd.Series(self.variables_extract_batch)
        try:
            self.formatData()
        except:
            pass
        self.asc_new_batch = self.asc[self.variables_extract_batch]
        return self.asc_new_batch
        try:
            del self.asc, self.asc_new
        except:
            pass 
        try:
            self.loadVars_GUI()
        except:
            pass
        try:
            self.previewData_GUI()
        except:
            pass
        
#######################################################################
# Function definitions for data loading, formatting, and processing
#######################################################################
    def loadData_GUI(self):

        try:
            # pop up box to select the input file for processing
            self.input_file, _ = QFileDialog.getOpenFileName(self,"Select a File to Convert", "/scr/raf_data","filter = nc(*.nc)")
            self.inputfilebox.setText(str(self.input_file))
            # use the path to the input file to pre-populate the output dir and filename
            self.head, self.tail = os.path.split(self.input_file)
            # populate the output directory text from the input directory
            self.outputdirbox.setText(str(self.head+'/'))
            # populate the output file text from the input filename with .txt extension
            self.tail = os.path.splitext(self.tail)[0]+'.txt'
            self.outputfilebox.setText(str(self.tail))
        except:
            # if there is an error loading the NetCDF file, notify the user in a popup
            no_process = QMessageBox()
            no_process.setWindowTitle("Error")
            no_process.setText("Cannot Process!")
            x = no_process.exec_()

    # define finction to format the data loaded
    def formatData(self):    

        try:
            # read in the input file 
            nc = netCDF4.Dataset(self.input_file, mode='r')
            # create an empty pandas series to hold variables
            self.variables_extract = pd.Series([])
            # create empty dicts
            self.asc = {}
            self.units = {}
            self.long_name = {}
            self.variables= {}
            self.fileheader = {}
            self.project_manager = 'Pavel Romashkin'
            self.platform = nc.getncattr('Platform')
            self.project_name=nc.getncattr('project')
            self.today = str(datetime.today().strftime('%Y, %m, %d'))
            self.today = self.today.replace('-', ', ')
            for i in nc.variables.keys():
                # handle only time dimension variables
                dims = str(nc.variables[i].dimensions)
                if dims == "('Time',)":
                    output=nc[i][:]
                    # append self.asc with vars in file 
                    self.asc[i]=pd.DataFrame(output)
                elif "sps1" in dims:
                    histo_output = pd.DataFrame(nc.variables[i][:,0,:])
                    self.asc[i] = pd.DataFrame(histo_output)
                # append self.units with netcdf attribute units
                units = nc.variables[i].getncattr('units')
                self.units[i]=pd.Series(units)
                # append self.long_name with netcdf attribute long_name
                long_name = nc.variables[i].getncattr('long_name')
                self.long_name[i]=pd.Series(long_name)
                # append self.variables with netcdf variable names
                variables = nc.variables[i].name
                self.variables[i]=pd.Series(variables)
            # concatenate
            self.asc=pd.concat(self.asc, axis=1, ignore_index=False)
            self.asc.columns = self.asc.columns.droplevel(-1)
            # create an object to store the NetCDF variable time          
            self.dtime=nc.variables['Time']
            # use num2date to setup dtime object
            self.dtime=netCDF4.num2date(self.dtime[:],self.dtime.units)
            self.dtime=pd.Series(self.dtime).astype(str)
            self.dtime_sep = self.dtime.str.split(' ', expand=True)
            # create separate date and time series for combination in previewData and writeData
            self.dtime_date = self.dtime_sep[0]
            self.dtime_time = self.dtime_sep[1]
            type(self.asc)
            # concatenate the units, long_name, variables, and header
            self.units=pd.concat(self.units, axis=0, ignore_index=True)
            self.long_name=pd.concat(self.long_name, axis=0, ignore_index=True)
            self.variables = pd.concat(self.variables, axis=0, ignore_index=True)
            self.fileheader = pd.concat([self.variables, self.units, self.long_name], axis=1, ignore_index=True)
            # subset the start and end time from the dtime objet by position
            self.start_time = self.dtime.iloc[1]
            self.end_time = self.dtime.iloc[-1]
            try:
                # populate the start_time and end_time fields in the gui
                self.start.setText(self.start_time)
                self.end.setText(self.end_time)
            except:
                print('Not running in gui mode, not setting fields for start and end time.')
        except:
           print('Error in extracting variable in '+str(self.input_file))
           return self.input_file, self.asc, self.fileheader, self.dtime_date, self.dtime_time
        print(self.asc)
    # define function to populate variables in the table
    def loadVars_GUI(self):

        try:
            self.header_np = self.fileheader.to_numpy()
            self.row_count = (len(self.header_np))
            self.column_count = 3
            self.var.setColumnCount(self.column_count)
            self.var.setRowCount(self.row_count)
            for row in range(self.row_count):
                for column in range(self.column_count):
                    self.item = str(self.header_np[row, column])
                    self.var.setItem(row, column, QTableWidgetItem(self.item))
        except:
            print("error setting up the table")

    # define function to select all variables in a NetCDF file
    def selectAll_GUI(self):

        self.formatData()
        self.asc_new = {}
        # iterate over the variables in the list 
        try:
            for i in range(self.row_count):
                self.var.item(i, 0).setBackground(QtGui.QColor(71,145,209))
            del self.asc_new
            self.asc = self.asc
            self.previewData_GUI()
        except:
            no_data = QMessageBox()
            no_data.setWindowTitle("Error")
            no_data.setText("There is no data to select all!")
            x = no_data.exec_() 

    # define function to deselect all variables, start from none
    def deselectAll_GUI(self):

        self.formatData()
        self.asc_new = {}
        try:
            for i in range(self.row_count):
                self.var.item(i, 0).setBackground(QtGui.QColor(255,255,255))
            self.outputpreview.setText('')
            self.date1.setChecked(True)
            self.time1.setChecked(True)
            self.comma.setChecked(True)
            self.fillvalue1.setChecked(True)
            self.header1.setChecked(True)
        except:
            no_data = QMessageBox()
            no_data.setWindowTitle("Error")
            no_data.setText("Error Clearing Vars!")
            x = no_data.exec_()

    # define function to select individual vars from list and populate fields
    def selectVars_GUI(self):

        # if there is a set of batch vars and user begins other selection, remove objects
        try:
            del(self.asc_new_batch)
            del(self.variables_extract_batch)
        except:
            print('No batch objects to remove.')
        try:
            self.output=pd.Series(self.var.item(self.var.currentRow(), 0).text()) 
            self.variables_extract = self.variables_extract.append(self.output)
            self.variables_extract = self.variables_extract.drop_duplicates()
            self.asc_new = self.asc[self.variables_extract]
        except:
            pass
        try:
            self.var_selected = str(self.asc_new.columns.values.tolist())
            self.var.item(self.var.currentRow(), 0).setBackground(QtGui.QColor(71,145,209))
            # need to remove the unwanted characters for the batch file
            self.var_selected = self.var_selected.replace('(', '')
            self.var_selected = self.var_selected.replace(')', '')
            self.var_selected = self.var_selected.replace("'", '')
            self.var_selected = self.var_selected.replace(',', '')
            self.var_selected = self.var_selected.replace('[', '')
            self.var_selected = self.var_selected.replace(']', '')
            self.previewData_GUI()
            return self.asc_new, self.variables_extract, self.var_selected
        except:
            print("error in getting values from table")

    # Define function to deselect (clear) all vars selected
    def deselectVar_GUI(self):

        self.checkoutput=self.var.item(self.var.currentRow(), 0).text()
        if self.checkoutput in self.variables_extract.values:
            self.variables_extract = self.variables_extract.loc[self.variables_extract.values != self.checkoutput]
            self.asc_new = self.asc_new.drop(self.checkoutput, axis=1)
            self.var_selected = self.var_selected.replace(self.checkoutput, '')
            self.var.item(self.var.currentRow(), 0).setBackground(QtGui.QColor(255,255,255))
        else:
            pass
        self.previewData_GUI()
        return self.asc_new, self.variables_extract, self.var_selected

    # Define function to switch radio buttons to align with ICARTT or AMES selection
    def ICARTT_AMES_toggle_GUI(self):

        self.time3.setChecked(True)
        self.date3.setChecked(True)
        self.comma.setChecked(True)
        self.fillvalue1.setChecked(True)
    #########################################################################
    # Define function to format ICARTT header
    # Note: if used outside of this script, multiple vars needed
    # self.dtime, self.platform, self.project_manager, self.project_name, 
    # self.today, self.varNumber, self.output_file
    # also need header1.txt and header2.txt as templates
    #########################################################################
    def ICARTTHeader(self, icartt_header):

        # try renaming the time var to Start_UTC
        try:
            icartt_header = pd.DataFrame(icartt_header.rename(columns={'Time': 'Start_UTC'}))
        except:
            print('Start_UTC rename failed')
        # get the varNumber from the # of columns in the dataframe
        self.varNumber = str(len(icartt_header.columns)-1)
        icartt_header.to_csv(self.output_file, header=True, index=False, na_rep='-99999.0')
        try:
            self.columns = pd.DataFrame(icartt_header.columns.values.tolist())
            self.fileheader = self.fileheader.loc[self.fileheader[0].isin(self.columns[0])]
            self.data_date = str(self.dtime_sep[0].iloc[1])
            self.data_date = self.data_date.replace('-', ', ')
            # start going through the template text docs
            os.system('cp ./docs/header1.txt ./docs/header1.tmp')
            os.system("ex -s -c '5i' -c x ./docs/header1.tmp")
            os.system('cp ./docs/header2.txt ./docs/header2.tmp') 
            # get today's date
            self.today = datetime.today().strftime('%Y, %m, %d')
            # perform the replacements on the first header file
            with open('./docs/header1.tmp', 'r+') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if line.startswith('RAF instruments on'):
                        lines[i] = lines[i].strip()+' '+self.platform+'\n'
                    if line.startswith('<PROJECT MANAGER>'):
                        lines[i] = self.project_manager+'\n'
                    if line.startswith('<PROJECT>'):
                        lines[i] = self.project_name+'\n'
                    if line.startswith('<YYYY, MM, DD,>'):
                        lines[i] = self.data_date+', '+self.today+'\n'
                    if line.startswith('<varNumber>'):
                        lines[i] = self.varNumber+'\n'
                    if line.startswith('<1.0>'):
                        lines[i] = '1.0,' * int(self.varNumber)+'\n'
                        lines[i] = lines[i][:-2]+'\n'
                    if line.startswith('<-99999.0>'):
                        lines[i] = '-99999.0,' * int(self.varNumber)+'\n'
                        lines[i] = lines[i][:-2]+'\n'
                f.seek(0)
                for line in lines:
                    f.write(line)
            # perform the replacements on the second header file
            with open('./docs/header2.tmp', 'r+') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if line.startswith('<PLATFORM>'):
                        lines[i] = 'PLATFORM: '+self.platform+'\n'
                f.seek(0)
                for line in lines:
                    f.write(line)
            # combine and perform replacement on the combined header file
            self.fileheader.to_csv('./docs/header1.tmp', mode='a', header=False, index=False)
            os.system('cat ./docs/header1.tmp ./docs/header2.tmp > ./docs/header.tmp')
            with open('./docs/header.tmp', 'r+') as f:
                lines = f.readlines()
                count = str(len(lines))+', 1001'
                for i, line in enumerate(lines):
                    if line.startswith('<ROWCOUNT>'):
                        lines[i] = count+'\n'
                f.seek(0)
                for line in lines:
                    f.write(line)
            os.system('head -n -1 ./docs/header.tmp > ./docs/trim.tmp ; mv ./docs/trim.tmp ./docs/header.tmp')
            os.system('mv '+str(self.output_file)+' '+str(self.output_file)+'.tmp')
            os.system('cat ./docs/header.tmp '+str(self.output_file)+'.tmp >> '+str(self.output_file))
            os.system('rm ./docs/header.tmp ./docs/header1.tmp ./docs/header2.tmp '+str(self.output_file)+'.tmp')
        except:
            print('Error creating and appending ICARTT header to output file.')
    #########################################################################
    # Define function to format AMES header
    ########################################################################
    def AMESHeader(self, ames_header):

        # try renaming the time var to Start_UTC
        try:
            ames_header = pd.DataFrame(ames_header.rename(columns={'Time': 'UTs'}))
        except:
            print('UTs rename failed')
        # get the varNumber from the # of columns in the dataframe
        self.varNumber = str(len(ames_header.columns)-1)
        ames_header.to_csv(self.output_file, header=True, index=False, na_rep='99999')
        try:
            self.columns = pd.DataFrame(ames_header.columns.values.tolist())
            self.fileheader = self.fileheader.loc[self.fileheader[0].isin(self.columns[0])]
            self.data_date = str(self.dtime_sep[0].iloc[1])
            self.data_date = self.data_date.replace('-', ', ')
            # start going through the template text docs
            os.system('cp ./docs/header1_ames.txt ./docs/header1_ames.tmp')
            os.system("ex -s -c '5i' -c x ./docs/header1_ames.tmp")
            os.system('cp ./docs/header2_ames.txt ./docs/header2_ames.tmp')
            # get today's date
            self.today = datetime.today().strftime('%Y, %m, %d')
            # perform the replacements on the first header file
            with open('./docs/header1_ames.tmp', 'r+') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if line.startswith('Flight data from:'):
                        lines[i] = lines[i].strip()+' '+self.platform+'\n'
                    if line.startswith('<PROJECT MANAGER>'):
                        lines[i] = self.project_manager+'\n'
                    if line.startswith('<PROJECT>'):
                        lines[i] = self.project_name+'\n'
                    if line.startswith('<YYYY, MM, DD,>'):
                        lines[i] = self.data_date+', '+self.today+'\n'
                    if line.startswith('<varNumber>'):
                        lines[i] = self.varNumber+'\n'
                    if line.startswith('<0.1>'):
                        lines[i] = '0.1,' * int(self.varNumber)+'\n'
                        lines[i] = lines[i][:-2]+'\n'
                    if line.startswith('<9999>'):
                        lines[i] = '9999,' * int(self.varNumber)+'\n'
                        lines[i] = lines[i][:-2]+'\n'
                f.seek(0)
                for line in lines:
                    f.write(line)
            # combine and perform replacement on the combined header file
            self.fileheader.to_csv('./docs/header1_ames.tmp', mode='a', header=False, index=False)
            os.system('cat ./docs/header1_ames.tmp ./docs/header2_ames.tmp > ./docs/header_ames.tmp')
            with open('./docs/header_ames.tmp', 'r+') as f:
                lines = f.readlines()
                count = str(len(lines))+', 1001'
                print(count)
                for i, line in enumerate(lines):
                    if line.startswith('<ROWCOUNT>'):
                        lines[i] = count+'\n'
                f.seek(0)
                for line in lines:
                    f.write(line)
            os.system('head -n -3 ./docs/header_ames.tmp > ./docs/trim.tmp ; mv ./docs/trim.tmp ./docs/header_ames.tmp')
            os.system('mv '+str(self.output_file)+' '+str(self.output_file)+'.tmp')
            os.system('cat ./docs/header_ames.tmp '+str(self.output_file)+'.tmp >> '+str(self.output_file))
            os.system('rm ./docs/header_ames.tmp ./docs/header1_ames.tmp ./docs/header2_ames.tmp '+str(self.output_file)+'.tmp')
        except:
            print('Error creating and appending AMES header to output file.')
    #########################################################################
    # Define function to notify user that processing was successful.
    #########################################################################
    def processingSuccess_GUI(self):

        processing_complete = QMessageBox()
        processing_complete.setWindowTitle("Success!")
        ret = QMessageBox.question(self, 'Success!', "Data was written to the output file.", QMessageBox.Ok)
    #########################################################################
    # Define function to format the preview portion of the output file
    #########################################################################
    def formatPreview_GUI(self):

        with open(self.output_file) as preview:
            head = str(preview.readlines()[0:10])
            head = head.replace('\\n', '\n')
            head = head.replace('\\n', '\n')
            head = head.replace('[', '')
            head = head.replace(']', '')
            head = head.replace("', '", '')
            head = head.replace("'", '')
        self.outputpreview.setText(head)
    #########################################################################
    # Define function for handling date and time 
    # Formatting for previewData_GUI and writeData functions
    #########################################################################
    def timeHandler(self, datasource):

        try:
            datasource.insert(loc=0, column='Time', value=self.dtime_time)
        except:
            print('Error inserting separate time series.')      
        try:
            datasource.insert(loc=0, column='Date', value=self.dtime_date)
        except:
            print('Error inserting separate date series.')
        try:
            datasource.pop('DateTime')
        except:
            print('Error dropping DateTime')
#############################################################################
# Function previewData_GUI creates an example output based on user settings and
# populates the Preview field in the gui. It is set up to autmatically update
# based on the selection of the vars in selectVars, selectAll_GUI, or deselectAll_GUI.
#############################################################################
   
    #########################################################################
    # Define function to preview data output within the app
    #########################################################################
    def previewData_GUI(self):

        # assign self.asc_new or self.asc to self.preview dataframe
        try:
            try:
                self.preview = self.asc_new_batch
            except:
                self.preview = self.asc_new
        except:
            self.preview = self.asc
        # get the output file from the text box
        self.output_file = self.outputdirbox.text()+self.outputfilebox.text()
        # get the start and end times from the text box in the gui
        start = self.start.text()
        end = self.end.text()
        try:
            # get the averaging information if it exists
            self.averaging_window = self.averagingbox.text()
            if len(self.averaging_window)!=0:
                self.averaging_window=int(self.averaging_window)
                self.preview = self.preview.rolling(self.averaging_window, min_periods=0).mean()
                self.preview = self.preview.iloc[::self.averaging_window, :]
            else:
                pass
            #################################################################
            # data and time combination checks for preview field
            ################################################################
            if self.date1.isChecked()==True and self.time1.isChecked()==True:
                try:
                    self.preview.pop('Time')
                except:
                    print('Error dropping Time')
                try:
                    self.preview.insert(loc=0, column='DateTime', value=self.dtime)
                except:
                    print('Error inserting DateTime for subselection.')
                try:
                    self.preview = self.preview[self.preview['DateTime']>start]
                except:
                    print('Error subselecting based on start time.')
                try:
                    self.preview = self.preview[self.preview['DateTime']<end]
                except:
                    print('Error subselecting based on end time.')
                self.timeHandler(self.preview)

            elif self.date1.isChecked()==True and self.time2.isChecked()==True:
                try:
                    self.preview.pop('Time')
                except:
                    print('Error dropping Time')
                try:
                    self.preview.insert(loc=0, column='DateTime', value=self.dtime)
                except:
                    print('Error inserting DateTime for subselection.')
                try:
                    self.preview = self.preview[self.preview['DateTime']>start]
                except:
                    print('Error subselecting based on start time.')
                try:
                    self.preview = self.preview[self.preview['DateTime']<end]
                except:
                    print('Error subselecting based on end time.')
                self.timeHandler(self.preview)
                self.preview['Time']=self.preview['Time'].str.replace(':', ' ')
            elif self.date1.isChecked()==True and self.time3.isChecked()==True:
                try:
                    self.preview.insert(loc=0, column='DateTime', value=self.dtime)
                except:
                    print('No insert of DateTime')
                try:
                    self.preview = self.preview[self.preview['DateTime']>start]
                except:
                    print('No time selection based on start time')
                try:
                    self.preview = self.preview[self.preview['DateTime']<end]
                except:
                    print('No time selection based on end time')
                try:
                    self.preview.insert(loc=0, column='Date', value=self.dtime_date)
                except:
                    print('No insert of Date')
                try:
                    self.preview.pop('DateTime')
                except:
                    print('No drop of DateTime')
            elif self.date2.isChecked()==True and self.time1.isChecked()==True:
                try:
                    self.preview.pop('Time')
                except:
                    print('Error dropping Time')
                try:
                    self.preview.insert(loc=0, column='DateTime', value=self.dtime)
                except:
                    print('Error inserting DateTime for subselection.')
                try:
                    self.preview = self.preview[self.preview['DateTime']>start]
                except:
                    print('Error subselecting based on start time.')
                try:
                    self.preview = self.preview[self.preview['DateTime']<end]
                except:
                    print('Error subselecting based on end time.')
                self.timeHandler(self.preview)
                self.preview['Date']=self.preview['Date'].str.replace('-', ' ')
            elif self.date2.isChecked()==True and self.time2.isChecked()==True:
                try:
                    self.preview.pop('Time')
                except:
                    print('Error dropping Time')
                try:
                    self.preview.insert(loc=0, column='DateTime', value=self.dtime)
                except:
                    print('Error inserting DateTime for subselection.')
                try:
                    self.preview = self.preview[self.preview['DateTime']>start]
                except:
                    print('Error subselecting based on start time.')
                try:
                    self.preview = self.preview[self.preview['DateTime']<end]
                except:
                    print('Error subselecting based on end time.')
                self.timeHandler(self.preview)
                self.preview['Date']=self.preview['Date'].str.replace('-', ' ')
                self.preview['Time']=self.preview['Time'].str.replace(':', ' ')
            elif self.date2.isChecked()==True and self.time3.isChecked()==True:
                try:
                    self.preview.insert(loc=0, column='DateTime', value=self.dtime)
                except:
                    print('No insert of DateTime')
                try:
                    self.preview = self.preview[self.preview['DateTime']>start]
                except:
                    print('No time selection based on start time')
                try:
                    self.preview = self.preview[self.preview['DateTime']<end]
                except:
                    print('No time selection based on end time')
                try:
                    self.preview.insert(loc=0, column='Date', value=self.dtime_date)
                except:
                    print('No insert of Date')
                try:
                    self.preview.pop('DateTime')
                except:
                    print('No drop of DateTime')
                try:
                    self.preview['Date']=self.preview['Date'].str.replace('-', ' ')
                except:
                    print('No replacement of -')
            elif self.date3.isChecked()==True and self.time1.isChecked()==True:
                try:
                    self.preview.pop('Time')
                except:
                    print('Error dropping Time')
                try:
                    self.preview.insert(loc=0, column='DateTime', value=self.dtime)
                except:
                    print('Error inserting DateTime for subselection.')
                try:
                    self.preview = self.preview[self.preview['DateTime']>start]
                except:
                    print('Error subselecting based on start time.')
                try:
                    self.preview = self.preview[self.preview['DateTime']<end]
                except:
                    print('Error subselecting based on end time.')
                self.timeHandler(self.preview)
                self.preview.pop('Date')
            elif self.date3.isChecked()==True and self.time2.isChecked()==True:
                try:
                    self.preview.pop('Time')
                except:
                    print('Error dropping Time')
                try:
                    self.preview.insert(loc=0, column='DateTime', value=self.dtime)
                except:
                    print('Error inserting DateTime for subselection.')
                try:
                    self.preview = self.preview[self.preview['DateTime']>start]
                except:
                    print('Error subselecting based on start time.')
                try:
                    self.preview = self.preview[self.preview['DateTime']<end]
                except:
                    print('Error subselecting based on end time.')
                self.timeHandler(self.preview)
                self.preview.pop('Date')
                self.preview['Time']=self.preview['Time'].str.replace(':', ' ')
            elif self.date3.isChecked()==True and self.time3.isChecked()==True:
                try:
                    self.preview.insert(loc=0, column='DateTime', value=self.dtime)
                except:
                    print('Error inserting DateTime for subselection.')
                try:
                    self.preview = self.preview[self.preview['DateTime']>start]
                except:
                    print('Error subselecting based on start time.')
                try:
                    self.preview = self.preview[self.preview['DateTime']<end]
                except:
                    print('Error subselecting based on end time.')
                pass
                try:
                    self.preview.pop('DateTime')
                except:
                    print('DateTime not dropped.')
            else:
                pass
            # Plain header
            if self.header1.isChecked()==True:
                if self.comma.isChecked()==True:
                    if self.fillvalue1.isChecked()==True:
                        self.preview.head(20).to_csv(self.output_file, header=True, index=False, na_rep='-32767.0')
                        self.formatPreview_GUI()
                    elif self.fillvalue2.isChecked()==True:
                        self.preview.head(20).to_csv(self.output_file, header=True, index=False, na_rep='')
                        self.formatPreview_GUI()
                    elif self.fillvalue3.isChecked()==True:
                        self.preview = self.preview.fillna(method='ffill')
                        self.preview.head(20).to_csv(self.output_file, header=True, index=False)
                        self.formatPreview_GUI()
                    else:
                        print('Error converting file: '+self.input_file)
                elif self.space.isChecked()==True:
                    if self.fillvalue1.isChecked()==True:
                        self.preview.head(20).to_csv(self.output_file, header=True, index=False, na_rep='-32767.0', sep=' ')
                        self.formatPreview_GUI()
                    elif self.fillvalue2.isChecked()==True:
                        self.preview.head(20).to_csv(self.output_file, header=True, index=False, na_rep='', sep=' ')
                        self.formatPreview_GUI()
                    elif self.fillvalue3.isChecked()==True:
                        self.preview = self.preview.fillna(method='ffill')
                        self.preview.head(20).to_csv(self.output_file, header=True, index=False, sep=' ')
                        self.formatPreview_GUI()
                    else:
                        print('Error converting file: '+self.input_file)
                else:
                    print('Error converting file: '+self.input_file)
            # ICARTT header
            elif self.header2.isChecked()==True:
                self.ICARTTHeader(self.preview)
                with open(self.output_file) as preview:
                    head = str(preview.readlines()[0:75])
                    head = head.replace('\\n', '\n')
                    head = head.replace('[', '')
                    head = head.replace(']', '')
                    head = head.replace("', '", '')
                    head = head.replace("'", '')
                self.outputpreview.setText(head)
            elif self.header3.isChecked()==True:
                self.AMESHeader(self.preview)
                with open(self.output_file) as preview:
                    head = str(preview.readlines()[0:75])
                    head = head.replace('\\n', '\n')
                    head = head.replace('[', '')
                    head = head.replace(']', '')
                    head = head.replace("', '", '')
                    head = head.replace("'", '')
                self.outputpreview.setText(head)
        except:
            processing_complete = QMessageBox()
            processing_complete.setWindowTitle("Error")
            processing_complete.setText("There was an error writing your ASCII file. Please try again.")
            x = processing_complete.exec_()
        else:
            pass

    #########################################################################
    # Define function to write data to output file
    #########################################################################
    def writeData(self):

        #####################################################################
        # Get inputs from GUI or CL depending on mode
        #####################################################################
        # determine which dataframe to use based on mode
        try:
            try:
                self.write = self.asc_new_batch
            except:
                self.write = self.asc_new
        except:
            self.write = self.asc

        # determine which output file to use based on mode
        try:
            try:
                # gui field
                self.output_file = self.outputdirbox.text()+self.outputfilebox.text()
            except:
                # command line arg
                self.output_file = self.args(output_file)
        except:
            # batchfile
            self.output_file = self.output_file
        # try to get the start and end time from the gui then from the batchfile
        try:
            # gui fields
            start = self.start.text()
            end = self.end.text()
        except:
            # batchfile
            start = self.start_time
            end = self.end_time
        # determine the date option based on gui or batchfile
        try:
            if self.date1.isChecked()==True:
                self.date = 'yyyy-mm-dd'
            elif self.date2.isChecked()==True:
                self.date = 'yyyy mm dd'
            elif self.date3.isChecked()== True:
                self.date = 'NoDate'
        except:
            self.date = self.date
        try:
            if self.time1.isChecked()==True:
                self.time = 'hh:mm:ss'
            elif self.time2.isChecked()==True:
                self.time = 'hh mm ss'
            elif self.time3.isChecked()==True:
                self.time = 'SecOfDay'
        except:
            self.time = self.time
        try:
            if self.comma.isChecked()==True:
                self.delimiter = 'comma'
            elif self.space.isChecked()==True:
                self.delimiter = 'space'
        except:
            self.delimiter = self.delimiter
        try:
            if self.fillvalue1.isChecked()==True:
                self.fillvalue = '-32767'
            elif self.fillvalue2.isChecked()==True:
                self.fillvalue = 'Blank'
            elif self.fillvalue3.isChecked()==True:
                self.fillvalue = 'Replicate'
        except:
            self.fillvalue = self.fillvalue
        try:
            if self.header1.isChecked()==True:
                self.header = 'Plain'
            elif self.header2.isChecked()==True:
                self.header = 'ICARTT'
            elif self.header3.isChecked()==True:
                self.header = 'AMES'
        except:
            self.header = self.header
        try:
            # get averaging information from window then batchfile
            try:
                self.averaging_window = self.averagingbox.text()
            except: 
                self.averaging_window = self.avg
            if len(self.averaging_window)!=0:
                self.averaging_window=int(self.averaging_window)
                self.write = self.write.rolling(self.averaging_window, min_periods=0).mean()
                self.write = self.write.iloc[::self.averaging_window, :]
            else:
                pass
            #################################################################
            # Date and time combination checks for output file
            #################################################################
            if self.date == 'yyyy-mm-dd' and self.time == 'hh:mm:ss':
                try:
                    self.write.pop('Time')
                except:
                    print('Error dropping Time')
                try:
                    self.write.insert(loc=0, column='DateTime', value=self.dtime)
                except:
                    print('Error inserting DateTime for subselection.')
                try:
                    self.write = self.write[self.write['DateTime']>start]
                except:
                    print('Error subselecting based on start time.')
                try:
                    self.write = self.write[self.write['DateTime']<end]
                except:
                    print('Error subselecting based on end time.')
                try:
                    self.write.insert(loc=0, column='Time', value=self.dtime_time)
                except:
                    print('Error inserting separate time series.')
                try:
                    self.write.insert(loc=0, column='Date', value=self.dtime_date)
                except:
                    print('Error inserting separate date series.')
                try:
                    self.write.pop('DateTime')
                except:
                    print('Error dropping DateTime')
                self.write.pop('Date')
                self.write.insert(loc=0, column='Date', value=self.dtime_date) 
            elif self.date == 'yyyy-mm-dd' and self.time == 'hh mm ss':
                try:
                    self.write.pop('Time')
                except:
                    print('Error dropping Time')
                try:
                    self.write.insert(loc=0, column='DateTime', value=self.dtime)
                except:
                    print('Error inserting DateTime for subselection.')
                try:
                    self.write = self.write[self.write['DateTime']>start]
                except:
                    print('Error subselecting based on start time.')
                try:
                    self.write = self.write[self.write['DateTime']<end]
                except:
                    print('Error subselecting based on end time.')
                try:
                    self.write.insert(loc=0, column='Time', value=self.dtime_time)
                except:
                    print('Error inserting separate time series.')
                try:
                    self.write.insert(loc=0, column='Date', value=self.dtime_date)
                except:
                    print('Error inserting separate date series.')
                try:
                    self.write.pop('DateTime')
                except:
                    print('Error dropping DateTime')
                self.write.pop('Date')
                self.write.insert(loc=0, column='Date', value=self.dtime_date)
                self.write['Time']=self.write['Time'].str.replace(':', ' ')
            elif self.date == 'yyyy-mm-dd' and self.time =='SecOfDay':
                try:
                    self.write.insert(loc=0, column='DateTime', value=self.dtime)
                except:
                    print('No insert of DateTime')
                try:
                    self.write = self.write[self.write['DateTime']>start]
                except:
                    print('No time selection based on start time')
                try:
                    self.write = self.write[self.write['DateTime']<end]
                except:
                    print('No time selection based on end time')
                try:
                    self.write.insert(loc=0, column='Date', value=self.dtime_date)
                except:
                    print('No insert of Date')
                try:
                    self.write.pop('DateTime')
                except:
                    print('No drop of DateTime')
            elif self.date == 'yyyy mm dd' and self.time == 'hh:mm:ss':
                try:
                    self.write.pop('Time')
                except:
                    print('Error dropping Time')
                try:
                    self.write.insert(loc=0, column='DateTime', value=self.dtime)
                except:
                    print('Error inserting DateTime for subselection.')
                try:
                    self.write = self.write[self.write['DateTime']>start]
                except:
                    print('Error subselecting based on start time.')
                try:
                    self.write = self.write[self.write['DateTime']<end]
                except:
                    print('Error subselecting based on end time.')
                try:
                    self.write.insert(loc=0, column='Time', value=self.dtime_time)
                except:
                    print('Error inserting separate time series.')
                try:
                    self.write.insert(loc=0, column='Date', value=self.dtime_date)
                except:
                    print('Error inserting separate date series.')
                try:
                    self.write.pop('DateTime')
                except:
                    print('Error dropping DateTime')
                self.write.pop('Date')
                self.write.insert(loc=0, column='Date', value=self.dtime_date)
                self.write['Date']=self.write['Date'].str.replace('-', ' ')
            elif self.date == 'yyyy mm dd' and self.time == 'hh mm ss':
                try:
                    self.write.pop('Time')
                except:
                    print('Error dropping Time')
                try:
                    self.write.insert(loc=0, column='DateTime', value=self.dtime)
                except:
                    print('Error inserting DateTime for subselection.')
                try:
                    self.write = self.write[self.write['DateTime']>start]
                except:
                    print('Error subselecting based on start time.')
                try:
                    self.write = self.write[self.write['DateTime']<end]
                except:
                    print('Error subselecting based on end time.')
                try:
                    self.write.insert(loc=0, column='Time', value=self.dtime_time)
                except:
                    print('Error inserting separate time series.')
                try:
                    self.write.insert(loc=0, column='Date', value=self.dtime_date)
                except:
                    print('Error inserting separate date series.')
                try:
                    self.write.pop('DateTime')
                except:
                    print('Error dropping DateTime')
                self.write.pop('Date')
                self.write.insert(loc=0, column='Date', value=self.dtime_date)
                self.write['Date']=self.write['Date'].str.replace('-', ' ')
                self.write['Time']=self.write['Time'].str.replace(':', ' ')
            elif self.date == 'yyyy mm dd' and self.time == 'SecOfDay':
                try:
                    self.write.insert(loc=0, column='DateTime', value=self.dtime)
                except:
                    print('No insert of DateTime')
                try:
                    self.write = self.write[self.write['DateTime']>start]
                except:
                    print('No time selection based on start time')
                try:
                    self.write = self.write[self.write['DateTime']<end]
                except:
                    print('No time selection based on end time')
                try:
                    self.write.insert(loc=0, column='Date', value=self.dtime_date)
                except:
                    print('No insert of Date')
                try:
                    self.write.pop('DateTime')
                except:
                    print('No drop of DateTime')
                try:
                    self.write['Date']=self.write['Date'].str.replace('-', ' ')
                except:
                    print('No replacement of -')
            elif self.date == 'NoDate' and self.time == 'hh:mm:ss':
                try:
                    self.write.pop('Time')
                except:
                    print('Error dropping Time')
                try:
                    self.write.insert(loc=0, column='DateTime', value=self.dtime)
                except:
                    print('Error inserting DateTime for subselection.')
                try:
                    self.write = self.write[self.write['DateTime']>start]
                except:
                    print('Error subselecting based on start time.')
                try:
                    self.write = self.write[self.write['DateTime']<end]
                except:
                    print('Error subselecting based on end time.')
                try:
                    self.write.insert(loc=0, column='Time', value=self.dtime_time)
                except:
                    print('Error inserting separate time series.')
                try:
                    self.write.insert(loc=0, column='Date', value=self.dtime_date)
                except:
                    print('Error inserting separate date series.')
                try:
                    self.write.pop('DateTime')
                except:
                    print('Error dropping DateTime')
                self.write.pop('Date')
            elif self.date == 'NoDate' and self.time == 'hh mm ss':
                try:
                    self.write.pop('Time')
                except:
                    print('Error dropping Time')
                try:
                    self.write.insert(loc=0, column='DateTime', value=self.dtime)
                except:
                    print('Error inserting DateTime for subselection.')
                try:
                    self.write = self.write[self.write['DateTime']>start]
                except:
                    print('Error subselecting based on start time.')
                try:
                    self.write = self.write[self.write['DateTime']<end]
                except:
                    print('Error subselecting based on end time.')
                try:
                    self.write.insert(loc=0, column='Time', value=self.dtime_time)
                except:
                    print('Error inserting separate time series.')
                try:
                    self.write.insert(loc=0, column='Date', value=self.dtime_date)
                except:
                    print('Error inserting separate date series.')
                try:
                    self.write.pop('DateTime')
                except:
                    print('Error dropping DateTime')
                self.write.pop('Date')
                self.write['Time']=self.write['Time'].str.replace(':', ' ')
            elif self.date == 'NoDate' and self.time == 'SecOfDay':
                try:
                    self.write.insert(loc=0, column='DateTime', value=self.dtime)
                except:
                    print('Error inserting DateTime for subselection.')
                try:
                    self.write = self.write[self.write['DateTime']>start]
                except:
                    print('Error subselecting based on start time.')
                try:
                    self.write = self.write[self.write['DateTime']<end]
                except:
                    print('Error subselecting based on end time.')
                try:
                    self.write.pop('DateTime')
                except:
                    print('DateTime not dropped.')
            else:
                pass
            # Plain header
            if self.header == 'Plain':
                if self.delimiter == 'comma':
                    if self.fillvalue == '-32767':
                        self.write.to_csv(self.output_file, header=True, index=False, na_rep='-32767.0')
                        try:
                            self.processingSuccess_GUI()
                            self.deselectAll_GUI()
                        except:
                            pass
                    elif self.fillvalue == 'Blank':
                        self.write.to_csv(self.output_file, header=True, index=False, na_rep='')
                        try:
                            self.processingSuccess_GUI()
                            self.deselectAll_GUI()
                        except:
                            pass
                    elif self.fillvalue == 'Replicate':
                        self.write = self.write.fillna(method='ffill')
                        self.write.to_csv(self.output_file, header=True, index=False)
                        try:
                            self.processingSuccess_GUI()
                            self.deselectAll_GUI()
                        except:
                            pass
                    else:
                        print('Error converting file: '+self.input_file)
                elif self.delimiter == 'space':
                    if self.fillvalue == '-32767':
                        self.write.to_csv(self.output_file, header=True, index=False, na_rep='-32767.0', sep=' ')
                        try:
                            self.processingSuccess_GUI()
                            self.deselectAll_GUI()
                        except:
                            pass
                    elif self.fillvalue == 'Blank':
                        self.write.to_csv(self.output_file, header=True, index=False, na_rep='', sep=' ')
                        try:
                            self.processingSuccess_GUI()
                            self.deselectAll_GUI()
                        except:
                            pass
                    elif self.fillvalue == 'Replicate':
                        self.write = self.write.fillna(method='ffill')
                        self.write.to_csv(self.output_file, header=True, index=False, sep=' ')
                        try:
                            self.processingSuccess()
                            self.deselectAll_GUI()
                        except:
                            pass
                    else:
                       print('Error converting file: '+self.input_file)
                else:
                   print('Error converting file: '+self.input_file)
            # ICARTT header
            elif self.header == 'ICARTT':
                try:
                    self.ICARTTHeader(self.write)
                except: 
                    print('Error creating and appending ICARTT header to output file.')
                try:
                    self.processingSuccess_GUI()
                    self.deselectAll_GUI()
                except:
                    pass
            # AMES header
            elif self.header == 'AMES':
                try:
                    self.AMESHeader(self.write)
                except:
                    print('Error creating and appending AMES header to output file.')
                try:
                    self.processingSuccess_GUI()
                    self.deselectAll_GUI()
                except:
                    pass
        except:
            try:
                processing_complete = QMessageBox()
                processing_complete.setWindowTitle("Error")
                processing_complete.setText("There was an error writing your ASCII file. Please try again.")
                x = processing_complete.exec_()
            except:
                print('Data was not written. Please try again.')
#######################################################################
# Define main function
#######################################################################
def main():

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Windows')
    ex = gui()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()