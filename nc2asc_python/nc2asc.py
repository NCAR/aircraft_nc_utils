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
from PyQt5.QtWidgets import QScrollBar, QToolBar, QMessageBox, QFileDialog, QTableWidgetItem, QVBoxLayout, QMenu, QMenuBar, QMainWindow, QAction, qApp, QApplication

class gui(QMainWindow):
    def __init__(self):

        super(gui, self).__init__() 

        self.initUI()

    #########################################################################
    # define layout of gui
    # set up the fields, table, buttons, and menu
    #########################################################################
    def initUI(self):               

        # bold font to help with organization of processing options
        myFont=QtGui.QFont()
        myFont.setBold(True)

        #####################################################################
        # input file and output dir / file fields
        #####################################################################
        # define input file box and label 
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
        # processing options section
        processinglabel = QtWidgets.QLabel(self)
        processinglabel.setText('Options')
        processinglabel.move(20, 140)
        processinglabel.setFont(myFont)

        #####################################################################
        # date format options
        #####################################################################
        # radio buttons for date
        dateformatlabel = QtWidgets.QLabel(self)
        dateformatlabel.setText('Date Format:')
        dateformatlabel.move(20, 160)
        dateformatlabel.setFont(myFont)
        self.date1=QtWidgets.QRadioButton(self)
        self.date1.setText('yyyy-mm-dd')
        self.date1.move(20, 180)
        self.date2=QtWidgets.QRadioButton(self)
        self.date2.setText('yyyy mm dd')
        self.date2.move(20, 200)
        self.date3=QtWidgets.QRadioButton(self)
        self.date3.setText('NoDate')
        self.date3.move(20, 220)
        dategroup = QtWidgets.QButtonGroup(self)
        dategroup.addButton(self.date1)
        dategroup.addButton(self.date2)
        dategroup.addButton(self.date3)
        # have the default be date 1 but update the preview when any are clicked
        self.date1.setChecked(True)
        self.date1.clicked.connect(self.previewData)
        self.date2.clicked.connect(self.previewData)
        self.date3.clicked.connect(self.previewData)

        #####################################################################
        # time format options
        #####################################################################
        # radio buttons for time
        timeformatlabel = QtWidgets.QLabel(self)
        timeformatlabel.setText('Time Format:')
        timeformatlabel.move(200, 160)
        timeformatlabel.setFont(myFont)
        self.time1=QtWidgets.QRadioButton(self)
        self.time1.setText('hh:mm:ss')
        self.time1.move(200, 180)
        self.time2=QtWidgets.QRadioButton(self)
        self.time2.setText('hh mm ss')
        self.time2.move(200, 200)
        self.time3=QtWidgets.QRadioButton(self)
        self.time3.setText('SecOfDay')
        self.time3.move(200, 220)
        timegroup = QtWidgets.QButtonGroup(self)
        timegroup.addButton(self.time1)
        timegroup.addButton(self.time2)
        timegroup.addButton(self.time3)
        # have default be time 1 but update the preview when any are clicked
        self.time1.setChecked(True)
        self.time1.clicked.connect(self.previewData)
        self.time2.clicked.connect(self.previewData)
        self.time3.clicked.connect(self.previewData)

        #####################################################################
        # delimiter format options
        #####################################################################
        # radio buttons for the delimiter
        delimiterlabel = QtWidgets.QLabel(self)
        delimiterlabel.setText('Delimiter:')
        delimiterlabel.move(380, 160)
        delimiterlabel.setFont(myFont)
        self.comma = QtWidgets.QRadioButton(self)
        self.comma.setText('Comma')
        self.comma.move(380, 180)
        self.space = QtWidgets.QRadioButton(self)
        self.space.setText('Space')
        self.space.move(380, 200)
        delimitergroup = QtWidgets.QButtonGroup(self)
        delimitergroup.addButton(self.comma)
        delimitergroup.addButton(self.space)
        # have default be comma delimited but update the preview when any are clicked
        self.comma.setChecked(True)        
        self.comma.clicked.connect(self.previewData)
        self.space.clicked.connect(self.previewData)

        #####################################################################
        # fill value format options
        ####################################################################
        # radio buttons for the fill value
        fillvaluelabel = QtWidgets.QLabel(self)
        fillvaluelabel.setText('Fill Value:')
        fillvaluelabel.move(20, 280)
        fillvaluelabel.setFont(myFont)
        self.fillvalue1=QtWidgets.QRadioButton(self)
        self.fillvalue1.setText('-32767.0')
        self.fillvalue1.move(20, 300)
        self.fillvalue2=QtWidgets.QRadioButton(self)
        self.fillvalue2.setText('Blank')
        self.fillvalue2.move(20, 320)
        self.fillvalue3=QtWidgets.QRadioButton(self)
        self.fillvalue3.setText('Replicate')
        self.fillvalue3.move(20, 340)
        fillvaluegroup = QtWidgets.QButtonGroup(self)
        fillvaluegroup.addButton(self.fillvalue1)
        fillvaluegroup.addButton(self.fillvalue2)
        fillvaluegroup.addButton(self.fillvalue3)
        # have default be fill value 1 but update the preview when any are clicked
        self.fillvalue1.setChecked(True)
        self.fillvalue1.clicked.connect(self.previewData)
        self.fillvalue2.clicked.connect(self.previewData)
        self.fillvalue3.clicked.connect(self.previewData)

        #####################################################################
        # header format options
        #####################################################################
        # radio buttons for header
        headerformatlabel = QtWidgets.QLabel(self)
        headerformatlabel.setText('Header:')
        headerformatlabel.move(200, 280)
        headerformatlabel.setFont(myFont)
        self.header1 = QtWidgets.QRadioButton(self)
        self.header1.setText('Plain')
        self.header1.move(200, 300)
        self.header2 = QtWidgets.QRadioButton(self)
        self.header2.setText('ICARTT')
        self.header2.move(200, 320)
        self.header3 = QtWidgets.QRadioButton(self)
        self.header3.setText('AMESDef')
        self.header3.move(200, 340)
        self.header3.setEnabled(0)
        headergroup = QtWidgets.QButtonGroup(self)
        headergroup.addButton(self.header1)
        headergroup.addButton(self.header2)
        headergroup.addButton(self.header3)
        # have the default be header 1 (plain) but update the preview when any are clicked
        self.header1.setChecked(True)
        self.header2.clicked.connect(self.ICARTT_toggle)
        self.header1.clicked.connect(self.previewData)
        self.header2.clicked.connect(self.previewData)
        self.header3.clicked.connect(self.previewData)
        # process button calls writeData function
        self.processbtn=QtWidgets.QPushButton('Convert File', self)
        self.processbtn.resize(self.processbtn.sizeHint())
        self.processbtn.move(20, 670)
        self.processbtn.clicked.connect(self.writeData)

        #####################################################################
        # variable table and selection / deselection options
        #####################################################################
        # button to select all variables
        self.varbtn=QtWidgets.QPushButton('Select All', self)
        self.varbtn.move(360, 320)
        self.varbtn.clicked.connect(self.loadVars)
        self.varbtn.clicked.connect(self.selectAll)
        # button to de-select all variables
        self.varbtn2=QtWidgets.QPushButton('Clear All', self)
        self.varbtn2.move(360, 360)
        self.varbtn2.clicked.connect(self.loadVars)
        self.varbtn2.clicked.connect(self.deselectAll)
        # button to remove current variable
        self.deselectvar=QtWidgets.QPushButton('Remove Var', self)
        self.deselectvar.move (360, 400)
        self.deselectvar.clicked.connect(self.deselectVar)
        self.deselectvar.clicked.connect(self.previewData)
        # variable table and buttons with labels
        varlabel=QtWidgets.QLabel(self)
        varlabel.setText('Select Vars:')
        varlabel.move(640, 30)
        varlabel.setFont(myFont)
        self.var=QtWidgets.QTableWidget(self)
        self.var.setColumnCount(3)
        self.var.setColumnWidth(2, 150)
        self.var.setRowCount(15)
        self.var.move(500, 60)
        self.var.resize(400, 430)
        self.var.setHorizontalHeaderLabels(['Var', 'Units', 'Long Name']) 
        self.var.clicked.connect(self.selectVars)
 
        #####################################################################
        # start time, end time, and averaging options
        #####################################################################
        # fields for start and end time
        timeselectionlabel = QtWidgets.QLabel(self)
        timeselectionlabel.setText('Time Options:')
        timeselectionlabel.move(20, 380)
        timeselectionlabel.setFont(myFont)
        startlab = QtWidgets.QLabel(self)
        startlab.setText('Start:')
        endlab = QtWidgets.QLabel(self)
        endlab.setText('End:')
        startlab.move(20,400)
        endlab.move(20,420)
        self.start=QtWidgets.QLineEdit(self)
        self.end=QtWidgets.QLineEdit(self)
        self.start.move(60, 405)
        self.start.resize(140, 20)
        self.end.move(60, 425)
        self.end.resize(140, 20)
        # averaging label and box
        averaginglabel=QtWidgets.QLabel(self)
        averaginglabel.setText('Averaging (s):')
        averaginglabel.move(20, 440)
        averagingnote=QtWidgets.QLabel(self)
        averagingnote.setText("Note: Average calc'd as rolling window mean.")
        averagingnote.move(200, 440)
        averagingnote.resize(300, 20)
        self.averagingbox = QtWidgets.QLineEdit(self)
        self.averagingbox.move(140, 445)
        self.averagingbox.resize(60, 20)

        #####################################################################
        # output preview options
        #####################################################################
        # output preview label
        self.outputpreviewlabel=QtWidgets.QLabel(self)
        self.outputpreviewlabel.move(20, 470)
        self.outputpreviewlabel.setText('Preview')
        self.outputpreviewlabel.setFont(myFont)
        # output preview field with horizontal scroll bar
        self.outputpreview=QtWidgets.QTextEdit(self)
        self.outputpreview.move(20, 500)
        self.outputpreview.resize(880, 150)
        self.outputpreview.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)

        #####################################################################
        # menu options
        #####################################################################
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        helpMenu = mainMenu.addMenu('Help')
        importFile = QAction('Import NetCDF File', self)
        saveBatchFile = QAction('Save Batch File', self)
        readBatchFile = QAction('Read Batch File', self)
        exit = QAction('Exit', self)
        fileMenu.addAction(importFile)
        fileMenu.addAction(saveBatchFile)
        fileMenu.addAction(readBatchFile)
        fileMenu.addAction(exit)
        # connect the menu option File > Import NetCDF File to the data functions
        importFile.triggered.connect(self.loadData)
        importFile.triggered.connect(self.formatData)
        importFile.triggered.connect(self.loadVars)
        # connect the menu option File > Read Batch file to the function
        readBatchFile.triggered.connect(self.readBatchFile)
        # connect the exit menu option to the close function
        exit.triggered.connect(self.close)
        # connect the save batch file menu option to the function
        saveBatchFile.triggered.connect(self.saveBatchFile)

        #####################################################################
        # general setup options
        #####################################################################
        # changing the background color to gray
        self.setWindowIcon(QIcon('raf.png'))
        self.setStyleSheet("background-color: light gray;")
        self.setGeometry(100, 100, 920, 700)
        self.setWindowTitle('NCAR/EOL RAF Aircraft netCDF to ASCII File Converter')    
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)
        self.show()

    #########################################################################
    # function definitions for batch file saving and reading
    #########################################################################
    # if user selects to save a batch file, call function
    def saveBatchFile(self):

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
                    self.batchfile.write('hd=AMESDef\n')
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
                self.batchfile.write('ti='+self.start.text()+' '+self.end.text()+'\n\n')
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
                savebatch.setText("Batch File Successfully Created! Check Output Directory")
                x = savebatch.exec_()
            except:
                # if there is an error, notify user on command line
                print("Error writing batchfile.")


    def readBatchFile(self):

        try:
            self.inputbatch_file, _ = QFileDialog.getOpenFileName(self,"Select a Batch file to Read", "/scr/raf_data","filter = *")
            # notify user that batch file has been read
            readbatch = QMessageBox()
            readbatch.setWindowTitle("Success!")
            readbatch.setText("Batch file successfully imported!")
            x = readbatch.exec_()
        except:
            # notify user that batch file has not been written
            readbatch = QMessageBox()
            readbatch.setWindowTitle("Error")
            readbatch.setText("Error reading batch file. Please try again.")
            x = readbatch.exec_()

        with open(self.inputbatch_file, 'r') as fi:
            self.input_file = []
            self.outputfile = []
            for ln in fi:
                # extract the path of the input file from the batch file
                if ln.startswith('if='):
                    self.input_file.append(ln[2:])
                # extract the path of the output file
                elif ln.startswith('of='): 
                    self.outputfile.append(ln[2:]) 

                # get the header format from the batch file
                elif ln.startswith('hd=Plain'):
                    self.header1.setChecked(True)
                elif ln.startswith('hd=ICARTT'):
                    self.header2.setChecked(True)
                elif ln.startswith('hd=AMESDef'):
                    self.header3.setChecked(True)

                # get the date format from the batch file
                elif ln.startswith('dt=yyyy-mm-dd'):
                    self.date1.setChecked(True)
                elif ln.startswith('dt=yyyy mm dd'):
                    self.date2.setChecked(True)
                elif ln.startswith('dt=NoDate'):
                    self.date3.setChecked(True)
                # get the time format from the batch file
                elif ln.startswith('tm=hh:mm:ss'):
                    self.time1.setChecked(True)
                elif ln.startswith('tm=hh mm ss'):
                    self.time2.setChecked(True)
                elif ln.startswith('tm=SecOfDay'):
                    self.time3.setChceked(True)

                # get the delimiter from the batch faile
                elif ln.startswith('sp=comma'):
                    self.comma.setChecked(True)
                elif ln.startswith('sp=space'):
                    self.space.setChecked(True)

                # get the fill value from the batch file
                elif ln.startswith('fv=-32767'):
                    self.fillvalue1.setChecked(True)
                elif ln.startswith('fv=blank'):
                    self.fillvalue2.setChecked(True)
                elif ln.startswith('fv=replicate'):
                    self.fillvalue3.setChecked(True)

            # format the input file and populate in gui
            self.input_file = str(self.input_file)    
            self.input_file = self.input_file.replace('[', '')
            self.input_file = self.input_file.replace("'", '')
            self.input_file = self.input_file.replace('=', '')
            self.input_file = self.input_file.replace(']', '')
            self.input_file = self.input_file[:-2]
            self.inputfilebox.setText(self.input_file)

            # format the output dir and file and populate in gui
            self.outputfile = str(self.outputfile)
            self.outputfile = self.outputfile.replace('[', '')
            self.outputfile = self.outputfile.replace("'", '')
            self.outputfile = self.outputfile.replace('=', '')
            self.outputfile = self.outputfile.replace(']', '')
            self.outputfile = self.outputfile[:-2]
            self.outputdirbox.setText(os.path.dirname(self.outputfile))
            self.outputfilebox.setText(os.path.basename(self.outputfile))

#######################################################################
# function definitions for data loading, formatting, and processing
#######################################################################
    def loadData(self):

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
            self.header = {}
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
                    # append self.units with netcdf attribute units
                    units = nc.variables[i].getncattr('units')
                    self.units[i]=pd.Series(units)
                    # append self.long_name with netcdf attribute long_name
                    long_name = nc.variables[i].getncattr('long_name')
                    self.long_name[i]=pd.Series(long_name)
                    # append self.variables with netcdf variable names
                    variables = nc.variables[i].name
                    self.variables[i]=pd.Series(variables)
                else:
                    pass

            # concatenate
            self.asc=pd.concat(self.asc, axis=1, ignore_index=False)
            self.asc.columns = self.asc.columns.droplevel(-1)
            # create an object to store the NetCDF variable time          
            self.dtime=nc.variables['Time']
            # use num2date to setup dtime object
            self.dtime=netCDF4.num2date(self.dtime[:],self.dtime.units)
            self.dtime=pd.Series(self.dtime).astype(str)
            self.dtime_sep = self.dtime.str.split(' ', expand=True)
            # concatenate the units, long_name, variables, and header
            self.units=pd.concat(self.units, axis=0, ignore_index=True)
            self.long_name=pd.concat(self.long_name, axis=0, ignore_index=True)
            self.variables = pd.concat(self.variables, axis=0, ignore_index=True)
            self.header = pd.concat([self.variables, self.units, self.long_name], axis=1, ignore_index=True)
            # subset the start and end time from the dtime objet by position
            self.start_time = self.dtime.iloc[1]
            self.end_time = self.dtime.iloc[-1]
            # populate the start_time and end_time fields in the gui
            self.start.setText(self.start_time)
            self.end.setText(self.end_time)
        except:
           print('Error in extracting variable in '+str(self.input_file))
        return self.input_file, self.asc, self.header

    # define function to populate variables in the table
    def loadVars(self):

        try:
            self.header_np = self.header.to_numpy()
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
    def selectAll(self):

        self.formatData()
        self.asc_new = {}
        # iterate over the variables in the list 
        try:
            for i in range(self.row_count):
                self.var.item(i, 0).setBackground(QtGui.QColor(71,145,209))
            del self.asc_new
            self.asc = self.asc
            self.previewData()
        except:
            no_data = QMessageBox()
            no_data.setWindowTitle("Error")
            no_data.setText("There is no data to select all!")
            x = no_data.exec_() 

    # define function to deselect all variables, start from none
    def deselectAll(self):

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
    def selectVars(self):

        try:
            self.output=pd.Series(self.var.item(self.var.currentRow(), 0).text()) 
            self.variables_extract = self.variables_extract.append(self.output)
            self.variables_extract = self.variables_extract.drop_duplicates()
            self.asc_new = self.asc[self.variables_extract]
            print(self.asc_new)
            self.var_selected = str(self.asc_new.columns.values.tolist())
            self.var.item(self.var.currentRow(), 0).setBackground(QtGui.QColor(71,145,209))

            # need to remove the unwanted characters for the batch file
            self.var_selected = self.var_selected.replace('0', '')
            self.var_selected = self.var_selected.replace('(', '')
            self.var_selected = self.var_selected.replace(')', '')
            self.var_selected = self.var_selected.replace("'", '')
            self.var_selected = self.var_selected.replace(',', '')
            self.var_selected = self.var_selected.replace('[', '')
            self.var_selected = self.var_selected.replace(']', '')

            self.previewData()

            return self.asc_new, self.variables_extract, self.var_selected
        except:
            print("error in getting values from table")

    def deselectVar(self):

        self.checkoutput=self.var.item(self.var.currentRow(), 0).text()
        if self.checkoutput in self.variables_extract.values:
            self.variables_extract = self.variables_extract.loc[self.variables_extract.values != self.checkoutput]
            self.asc_new = self.asc_new.drop(self.checkoutput, axis=1)
            self.var_selected = self.var_selected.replace(self.checkoutput, '')
            self.var.item(self.var.currentRow(), 0).setBackground(QtGui.QColor(255,255,255))
        else:
            pass
        return self.asc_new, self.variables_extract, self.var_selected

    # define function to switch radio buttons to align with ICARTT selection
    def ICARTT_toggle(self):
        self.time3.setChecked(True)
        self.date3.setChecked(True)
        self.comma.setChecked(True)
        self.fillvalue1.setChecked(True)
   
    def ICARTTHeader(self, icartt_header):
        try:
            icartt_header = pd.DataFrame(icartt_header.rename(columns={'DateTime': 'Start_UTC'}))
        except:
            icartt_header = pd.DataFrame(icartt_header.rename(columns={'Time': 'Start_UTC'}))
        self.varNumber = str(len(icartt_header.columns)-1)
        icartt_header.head(50).to_csv(self.output_file, header=True, index=False, na_rep='-99999.0')
        try:
            self.columns = pd.DataFrame(icartt_header.columns.values.tolist())
            self.header = self.header.loc[self.header[0].isin(self.columns[0])]
            self.data_date = str(self.dtime_sep[0].iloc[1])
            self.data_date = self.data_date.replace('-', ', ')

            os.system('cp ./docs/header1.txt ./docs/header1.tmp')
            os.system("ex -s -c '5i' -c x ./docs/header1.tmp")
            os.system('cp ./docs/header2.txt ./docs/header2.tmp') 
            self.today = datetime.today().strftime('%Y, %m, %d')
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

            with open('./docs/header2.tmp', 'r+') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if line.startswith('<PLATFORM>'):
                        lines[i] = 'PLATFORM: '+self.platform+'\n'

                f.seek(0)
                for line in lines:
                    f.write(line)

            self.header.to_csv('./docs/header1.tmp', mode='a', header=False, index=False)
            os.system('cat ./docs/header1.tmp ./docs/header2.tmp > ./docs/header.tmp')
            with open('./docs/header.tmp', 'r+') as f:
                lines = f.readlines()
                count = str(len(lines))
                for i, line in enumerate(lines):
                    if line.startswith('<ROWCOUNT>'):
                        lines[i] = count+' ,1001\n'
                f.seek(0)
                for line in lines:
                    f.write(line)
            os.system('mv '+str(self.output_file)+' '+str(self.output_file)+'.tmp')
            os.system('cat ./docs/header.tmp '+str(self.output_file)+'.tmp >> '+str(self.output_file))
            os.system('rm ./docs/header.tmp ./docs/header1.tmp ./docs/header2.tmp '+str(self.output_file)+'.tmp')
        except:
            print('Error creating and appending ICARTT header to output file.')
#############################################################################
# notification that processing was successfule
#############################################################################

    # define function to notify user that processing was successful.
    def processingSuccess(self):

        processing_complete = QMessageBox()
        processing_complete.setWindowTitle("Success!")
        ret = QMessageBox.question(self, 'Success!', "Data was written to the output file.", QMessageBox.Ok)

    # define function to format the preview portion of the output file
    def formatPreview(self):
        with open(self.output_file) as preview:
            head = str(preview.readlines()[0:10])
            head = head.replace('\\n', '\n')
            head = head.replace('\\n', '\n')
            head = head.replace('[', '')
            head = head.replace(']', '')
            head = head.replace("', '", '')
            head = head.replace("'", '')
        self.outputpreview.setText(head)

#############################################################################
# define date and time functions for use in previewData and writeData
#############################################################################

    # define function for handling date and time formatting for previewData and writeData functions
    def timeHandler(self, datasource):

        try:
            datasource.pop('Time')
        except:
            pass
        try:
            datasource.insert(loc=0, column='DateTime', value=self.dtime)
        except:
            pass
        try:
            datasource = datasource+[datasource['DateTime']>start]
        except:
            pass
        try:
            datasource = datasource[datasource['DateTime']<end]
        except:
            pass

#############################################################################
# function previewData creates an example output based on user settings and
# populates the Preview field in the gui. It is set up to autmatically update
# based on the selection of the vars in selectVars, selectAll, or deselectAll.
#############################################################################

    # define function to preview data output within the app
    def previewData(self):
        try:
            self.preview = self.asc_new
        except:
            self.preview = self.asc
        self.output_file = self.outputdirbox.text()+self.outputfilebox.text()
        start = self.start.text()
        end = self.end.text()
        try:
            self.averaging_window = self.averagingbox.text()
            if len(self.averaging_window)!=0:
                self.averaging_window=int(self.averaging_window)
                self.preview = self.preview.rolling(self.averaging_window, min_periods=0).mean().round(decimals=3)
                self.preview = self.preview.iloc[::self.averaging_window, :]
            else:
                pass
            if self.date1.isChecked()==True and self.time1.isChecked()==True:
                self.timeHandler(self.preview)
            elif self.date1.isChecked()==True and self.time2.isChecked()==True:
                self.timeHandler(self.preview)
                self.preview['DateTime']=self.preview['DateTime'].str.replace(':', ' ')
            elif self.date1.isChecked()==True and self.time3.isChecked()==True:
                self.preview.insert(loc=0, column='Date', value=self.dtime_sep[0])
                try:
                    self.preview.drop('DateTime', axis=1, inplace=True)
                except:
                    print('DateTime not dropped')
            elif self.date2.isChecked()==True and self.time1.isChecked()==True:
                self.timeHandler(self.preview)
                self.preview['DateTime']=self.preview['DateTime'].str.replace('-', ' ')
            elif self.date2.isChecked()==True and self.time2.isChecked()==True:
                self.timeHandler(self.preview)
                self.preview['DateTime']=self.preview['DateTime'].str.replace(':', ' ')
                self.preview['DateTime']=self.preview['DateTime'].str.replace('-', ' ')
            elif self.date2.isChecked()==True and self.time3.isChecked()==True:
                self.preview.insert(loc=0, column='Date', value=self.dtime_sep[0])
                self.preview['Date']=self.preview['Date'].str.replace('-', ' ')
                try:
                    self.preview.drop('DateTime', axis=1, inplace=True)
                except:
                    print('DateTime not dropped')
            elif self.date3.isChecked()==True and self.time1.isChecked()==True:
                try:
                    self.preview.pop('Time')
                except:
                    pass
                self.preview.insert(loc=0, column='Time', value=self.dtime_sep[1])
                try:
                    self.preview.drop('DateTime', axis=1, inplace=True)
                except:
                    print('DateTime not dropped')
            elif self.date3.isChecked()==True and self.time2.isChecked()==True:
                try:
                    self.preview.pop('Time')
                except:
                    pass
                self.preview.insert(loc=0, column='Time', value=self.dtime_sep[1])
                self.preview['Time']=self.preview['Time'].str.replace(':', ' ')
                try:
                    self.preview.drop('DateTime', axis=1, inplace=True)
                except:
                    print('DateTime not dropped')
            elif self.date3.isChecked()==True and self.time3.isChecked()==True:
                try:
                    self.prevew = self.preview.drop('Date', axis=1, inplace=True)
                except:
                    print('Date not dropped')
            else:
                pass
            if self.header1.isChecked()==True:
                if self.comma.isChecked()==True:
                    if self.fillvalue1.isChecked()==True:
                        self.preview.head(15).to_csv(self.output_file, header=True, index=False, na_rep='-32767.0')
                        self.formatPreview()
                    elif self.fillvalue2.isChecked()==True:
                        self.preview.head(15).to_csv(self.output_file, header=True, index=False, na_rep='')
                        self.formatPreview()
                    elif self.fillvalue3.isChecked()==True:
                        self.preview = self.preview.fillna(method='ffill')
                        self.preview.head(15).to_csv(self.output_file, header=True, index=False)
                        self.formatPreview()
                    else:
                        print('Error converting file: '+self.input_file)
                elif self.space.isChecked()==True:
                    if self.fillvalue1.isChecked()==True:
                        self.preview.head(15).to_csv(self.output_file, header=True, index=False, na_rep='-32767.0', sep=' ')
                        self.formatPreview()
                    elif self.fillvalue2.isChecked()==True:
                        self.preview.head(15).to_csv(self.output_file, header=True, index=False, na_rep='', sep=' ')
                        self.formatPreview()
                    elif self.fillvalue3.isChecked()==True:
                        self.preview = self.preview.fillna(method='ffill')
                        self.preview.head(15).to_csv(self.output_file, header=True, index=False, sep=' ')
                        self.formatPreview()
                    else:
                        print('Error converting file: '+self.input_file)
                else:
                    print('Error converting file: '+self.input_file)

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
            else:
                pass 
        except:
            processing_complete = QMessageBox()
            processing_complete.setWindowTitle("Error")
            processing_complete.setText("There was an error writing your ASCII file. Please try again.")
            x = processing_complete.exec_()
        else:
            pass

    # define function to write data to an output preview field and to output file
    def writeData(self):

        try:
            self.asc = self.asc_new
        except:
            self.asc = self.asc
        self.output_file = self.outputdirbox.text()+self.outputfilebox.text()
        start = self.start.text()
        end = self.end.text()
        try:
            self.averaging_window = self.averagingbox.text()
            if len(self.averaging_window)!=0:
                self.averaging_window=int(self.averaging_window)
                try:
                    self.asc.set_index('DateTime')
                except:
                    self.asc.set_index('Time')
                self.asc = self.asc.rolling(self.averaging_window, min_periods=0).mean().round(decimals=3)
                self.asc = self.asc.iloc[::self.averaging_window, :]
            else:
                pass
            if self.date1.isChecked()==True and self.time1.isChecked()==True:
                self.timeHandler(self.asc)
            elif self.date1.isChecked()==True and self.time2.isChecked()==True:
                self.timeHandler(self.asc)
                self.preview['DateTime']=self.preview['DateTime'].str.replace(':', ' ')
            elif self.date1.isChecked()==True and self.time3.isChecked()==True:
                self.asc.insert(loc=0, column='Date', value=self.dtime_sep[0])
                try:
                    self.asc.drop('DateTime', axis=1, inplace=True)
                except:
                    print('DateTime not dropped')
            elif self.date2.isChecked()==True and self.time1.isChecked()==True:
                self.timeHandler(self.asc)
                self.preview['DateTime']=self.preview['DateTime'].str.replace('-', ' ')
            elif self.date2.isChecked()==True and self.time2.isChecked()==True:
                self.timeHandler(self.asc)
                self.preview['DateTime']=self.preview['DateTime'].str.replace(':', ' ')
                self.preview['DateTime']=self.preview['DateTime'].str.replace('-', ' ')
            elif self.date2.isChecked()==True and self.time3.isChecked()==True:
                self.asc.insert(loc=0, column='Date', value=self.dtime_sep[0])
                self.asc['Date']=self.asc['Date'].str.replace('-', ' ')
                try:
                    self.asc.drop('DateTime', axis=1, inplace=True)
                except:
                    print('DateTime not dropped')
            elif self.date3.isChecked()==True and self.time1.isChecked()==True:
                try:
                    self.asc.pop('Time')
                except:
                    pass
                self.asc.insert(loc=0, column='Time', value=self.dtime_sep[1])
                try:
                    self.asc.drop('DateTime', axis=1, inplace=True)
                except:
                    print('DateTime not dropped')
            elif self.date3.isChecked()==True and self.time2.isChecked()==True:
                try:
                    self.asc.pop('Time')
                except:
                    pass
                self.asc.insert(loc=0, column='Time', value=self.dtime_sep[1])
                self.asc['Time']=self.asc['Time'].str.replace(':', ' ')
                try:
                    self.asc.drop('DateTime', axis=1, inplace=True)
                except:
                    print('DateTime not dropped')
            elif self.date3.isChecked()==True and self.time3.isChecked()==True:
                pass
            else:
                pass
            if self.header1.isChecked()==True:
                if self.comma.isChecked()==True:
                    if self.fillvalue1.isChecked()==True:
                        self.asc.to_csv(self.output_file, header=True, index=False, na_rep='-32767.0')
                        self.processingSuccess()
                        self.deselectAll()
                    elif self.fillvalue2.isChecked()==True:
                        self.asc.to_csv(self.output_file, header=True, index=False, na_rep='')
                        self.processingSuccess()
                        self.deselectAll()
                    elif self.fillvalue3.isChecked()==True:
                        self.asc = self.asc.fillna(method='ffill')
                        self.asc.to_csv(self.output_file, header=True, index=False)
                        self.processingSuccess()
                        self.deselectAll()
                    else:
                        print('Error converting file: '+self.input_file)
                elif self.space.isChecked()==True:
                    if self.fillvalue1.isChecked()==True:
                        self.asc.to_csv(self.output_file, header=True, index=False, na_rep='-32767.0', sep=' ')
                        self.processingSuccess()
                        self.deselectAll()
                    elif self.fillvalue2.isChecked()==True:
                        self.asc.to_csv(self.output_file, header=True, index=False, na_rep='', sep=' ')
                        self.processingSuccess()
                        self.deselectAll()
                    elif self.fillvalue3.isChecked()==True:
                        self.asc = self.asc.fillna(method='ffill')
                        self.asc.to_csv(self.output_file, header=True, index=False, sep=' ')
                        self.processingSuccess()
                        self.deselectAll()
                    else:
                        print('Error converting file: '+self.input_file)
                else:
                    print('Error converting file: '+self.input_file)
            elif self.header2.isChecked()==True:
                try:
                    self.ICARTTHeader(self.asc)

                except: 
                    print('Error creating and appending ICARTT header to output file.')
                self.processingSuccess()
                self.deselectAll()
            else:
                pass 
        except:
            processing_complete = QMessageBox()
            processing_complete.setWindowTitle("Error")
            processing_complete.setText("There was an error writing your ASCII file. Please try again.")
            x = processing_complete.exec_()
        
#######################################################################
# define main function
#######################################################################
def main():

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Windows')
    ex = gui()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
