#!/opt/local/anaconda3/bin/python3.7

#######################################################################
# Python based netCDF to ASCII converter with GUI
# written in Python 3
# Copyright University Corporation for Atmospheric Research (2020)
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
from PyQt5.QtWidgets import QToolBar, QMessageBox, QFileDialog, QTableWidgetItem, QVBoxLayout, QMenu, QMenuBar, QMainWindow, QAction, qApp, QApplication
class gui(QMainWindow):
    def __init__(self):

        super(gui, self).__init__() 


        self.initUI()
#######################################################################
# define layout of gui
#######################################################################
    def initUI(self):               

	# input file 
#        self.inputbtn = QtWidgets.QPushButton('Input File', self)
#        self.inputbtn.resize(self.inputbtn.sizeHint())
#        self.inputbtn.move(20, 20)
#        self.inputbtn.clicked.connect(self.loadData)
#        self.inputbtn.clicked.connect(self.loadVars)
      
        myFont=QtGui.QFont()
        myFont.setBold(True)
 
        self.inputfilebox=QtWidgets.QLineEdit(self)
        self.inputfilebox.move(160, 30)
        self.inputfilebox.resize(350, 20)
        inputlabel=QtWidgets.QLabel(self)
        inputlabel.setText('Input File:')
        inputlabel.move(80, 30) 
        # output dir and file
        self.outputbtn=QtWidgets.QPushButton('Output Directory', self)
        self.outputbtn.resize(self.outputbtn.sizeHint())
        self.outputbtn.move(40, 60)
        self.outputbtn.clicked.connect(self.dirSelect)
        self.outputdirbox=QtWidgets.QLineEdit(self)
        self.outputdirbox.move(160, 60)
        self.outputdirbox.resize(350, 20)
        outputlabel=QtWidgets.QLabel(self)
        outputlabel.setText('Output File:')
        outputlabel.move(50, 100)        
        self.outputfilebox=QtWidgets.QLineEdit(self)
        self.outputfilebox.move(160, 100)
        self.outputfilebox.resize(175, 20)

        # processing options section
        processinglabel = QtWidgets.QLabel(self)
        processinglabel.setText('Options')
        processinglabel.move(20, 140)
        processinglabel.setFont(myFont)

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
        self.date1.setChecked(True)

        # radio buttons for time
        timeformatlabel = QtWidgets.QLabel(self)
        timeformatlabel.setText('Time Format')
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
        self.time1.setChecked(True)

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
        self.comma.setChecked(True)        

        # radio buttons for the fillvalue
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
        self.fillvalue1.setChecked(True)

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
        headergroup = QtWidgets.QButtonGroup(self)
        headergroup.addButton(self.header1)
        headergroup.addButton(self.header2)
        headergroup.addButton(self.header3)
        self.header1.setChecked(True)
        self.header2.clicked.connect(self.ICARTT_toggle)

        # averaging label and box
        averaginglabel=QtWidgets.QLabel(self)
        averaginglabel.setText('Averaging (s):')
        averaginglabel.move(320, 340)
        self.averagingbox = QtWidgets.QLineEdit(self)
        self.averagingbox.move(440, 340)
        self.averagingbox.resize(60, 20)

        # process button calls writeData function
        self.processbtn=QtWidgets.QPushButton('Convert File', self)
        self.processbtn.resize(self.processbtn.sizeHint())
        self.processbtn.clicked.connect(self.outputFile)
        self.processbtn.move(700, 670)
        self.processbtn.clicked.connect(self.writeData)

        # button to select all variables
        self.varbtn=QtWidgets.QPushButton('Select All', self)
        self.varbtn.move(640, 30)
        self.varbtn.clicked.connect(self.selectAll)

        # button to de-select all variables
        self.varbtn2=QtWidgets.QPushButton('Unselect All', self)
        self.varbtn2.move(780, 30)
        self.varbtn2.clicked.connect(self.deselectAll)

        # label for variable list window
        fillvaluelabel = QtWidgets.QLabel(self)
        fillvaluelabel.setText('Selected vars:')
        fillvaluelabel.move(20, 380)
        fillvaluelabel.setFont(myFont)
        self.stdout=QtWidgets.QTextEdit(self)
        self.stdout.move(20, 400)
        self.stdout.resize(500, 50)
        varlabel=QtWidgets.QLabel(self)
        varlabel.setText('Select Vars')
        varlabel.move(550, 30)
        self.var=QtWidgets.QTableWidget(self)
        self.var.setColumnCount(3)
        self.var.setRowCount(15)
        self.var.move(550, 60)
        self.var.resize(350, 430)
        self.var.setHorizontalHeaderLabels(['Var', 'Units', 'Long Name']) 
        self.var.clicked.connect(self.selectVars)

        # fields for start and end time
        timeselectionlabel = QtWidgets.QLabel(self)
        timeselectionlabel.setText('Time Options')
        timeselectionlabel.move(320, 280)
        timeselectionlabel.setFont(myFont)
        startlab = QtWidgets.QLabel(self)
        startlab.setText('Start:')
        endlab = QtWidgets.QLabel(self)
        endlab.setText('End:')
        startlab.move(320,300)
        endlab.move(320,320)
        self.start=QtWidgets.QLineEdit(self)
        self.end=QtWidgets.QLineEdit(self)
        self.start.move(360, 300)
        self.start.resize(140, 20)
        self.end.move(360, 320)
        self.end.resize(140, 20)

        # exit app
#        closebtn=QtWidgets.QPushButton('Exit', self)
#        closebtn.move(810, 670)
#        closebtn.clicked.connect(self.close)

        # header preview
        self.headerpreviewbtn=QtWidgets.QPushButton('Show Preview', self)
        self.headerpreviewbtn.move(20, 460)
        self.headerpreviewbtn.clicked.connect(self.outputFile)
        self.headerpreviewbtn.clicked.connect(self.writeData)
        self.headerpreview=QtWidgets.QTextEdit(self)
        self.headerpreview.move(20, 500)
        self.headerpreview.resize(880, 150)

        # general setup options
        # menu options
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        helpMenu = mainMenu.addMenu('Help')
        importFile = QAction('Import NetCDF File', self)
        saveBatchFile = QAction('Save Batch File', self)
        readBatchFile = QAction('Read Batch File', self)
        exit = QAction('Exit', self)
        importFile.triggered.connect(self.loadData)
        importFile.triggered.connect(self.loadVars)
        exit.triggered.connect(self.close)
        fileMenu.addAction(importFile)               
        fileMenu.addAction(saveBatchFile)
        fileMenu.addAction(readBatchFile)
        fileMenu.addAction(exit)

        self.setGeometry(100, 100, 920, 700)
        self.setWindowTitle('NCAR/EOL RAF Aircraft netCDF to ASCII File Converter')    
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)
        self.show()

#######################################################################
# function definitions for buttons, fields, and table
#######################################################################

    def loadData(self):
        try:
            self.input_file, _ = QFileDialog.getOpenFileName(self,"Select a File to Convert", "/scr/raf_data","filter = nc(*.nc)")
            self.inputfilebox.setText(str(self.input_file))
            print(str(self.input_file)+' selected for conversion')
        except:
            no_process = QMessageBox()
            no_process.setWindowTitle("Error")
            no_process.setText("Cannot Process!")
            x = no_process.exec_()
    
        try:
            nc = netCDF4.Dataset(self.input_file, mode='r')
            self.variables_extract = pd.Series([])
            self.asc = {}
            self.units = {}
            self.long_name = {}
            self.variables= {}
            self.header = {}
            for i in nc.variables.keys():
                dims = str(nc.variables[i].dimensions)
                if dims == "('Time',)":
                    output=nc[i][:]
                    self.asc[i]=pd.DataFrame(output)
                    units = nc.variables[i].getncattr('units')
                    self.units[i]=pd.Series(units)
                    long_name = nc.variables[i].getncattr('long_name')
                    self.long_name[i]=pd.Series(long_name)
                    variables = nc.variables[i].name
                    self.variables[i]=pd.Series(variables)
                else:
                    pass
            self.asc=pd.concat(self.asc, axis=1, ignore_index=False)
            self.dtime=nc.variables['Time']
            self.dtime=netCDF4.num2date(self.dtime[:],self.dtime.units)
            self.dtime=pd.Series(self.dtime).astype(str)
            self.units=pd.concat(self.units, axis=0, ignore_index=True)
            self.long_name=pd.concat(self.long_name, axis=0, ignore_index=True)
            self.variables = pd.concat(self.variables, axis=0, ignore_index=True)
            self.header = pd.concat([self.variables, self.units, self.long_name], axis=1, ignore_index=True)

            self.start_time = self.dtime.iloc[1]
            self.end_time = self.dtime.iloc[-1]
            self.start.setText(self.start_time)
            self.end.setText(self.end_time)
        except:
           print('Error in extracting variable in '+str(self.input_file))
        return self.input_file, self.asc, self.header

    def dirSelect(self):
        self.dirname=QFileDialog.getExistingDirectory()
        self.dirname=self.dirname + '/' 
        self.outputdirbox.setText(self.dirname)
        return self.dirname

    def outputFile(self):
        self.output_file = self.outputfilebox.text()
        return self.output_file

    def selectAll(self):
        try:
            for i in range(self.row_count):
                self.var.item(i, 0).setBackground(QtGui.QColor(71,145,209))
            self.asc = self.asc
            self.stdout.setText('All')
        except:
            no_data = QMessageBox()
            no_data.setWindowTitle("Error")
            no_data.setText("There is no data to select all!")
            x = no_data.exec_() 
            
    def deselectAll(self):
        try:
            for i in range(self.row_count):
                self.var.item(i, 0).setBackground(QtGui.QColor(255,255,255))
            self.asc = self.asc
            self.stdout.setText('None')
        except:
            no_data = QMessageBox()
            no_data.setWindowTitle("Error")
            no_data.setText("There is no data to unselect!")
            x = no_data.exec_()

    def selectVars(self):
        try:
            for i in range(self.row_count):
                self.var.item(i, 0).setBackground(QtGui.QColor(255,255,255))
            output=pd.Series(self.var.item(self.var.currentRow(), 0).text())
            self.variables_extract = self.variables_extract.append(output)
            self.variables_extract = self.variables_extract.drop_duplicates()
            self.asc_new = self.asc[self.variables_extract]
            self.var_selected = str(self.asc_new.columns.values.tolist())
            self.var_selected = self.var_selected.replace('0', '')
            self.var_selected = self.var_selected.replace('(', '')
            self.var_selected = self.var_selected.replace(')', '')
            self.var_selected = self.var_selected.replace("'", '')
            self.var_selected = self.var_selected.replace(',', '')
            self.stdout.setText(self.var_selected+'\n')
            return self.asc_new
        except:
            print("error in getting values from table")
        
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

    def ICARTT_toggle(self):
        self.date3.setChecked(True)
        self.comma.setChecked(True)
        self.fillvalue1.setChecked(True)

    def writeData(self):

        try:
            self.asc = self.asc_new
        except:
            self.asc = self.asc

        self.output_file = self.dirname+"/"+self.output_file
        self.start = self.start.text()
        self.end = self.end.text()

        try:
            if 'Time' not in self.asc.columns: 
                msg = QMessageBox()
                msg.setWindowTitle("Error")
                msg.setText("You must select the Time var, at least.")
                x = msg.exec_()
            else:
                if self.date1.isChecked()==True and self.time1.isChecked()==True:
                    self.asc.pop('Time')
                    self.asc.insert(loc=0, column='DateTime', value=self.dtime)
                    self.asc = self.asc[self.asc['DateTime']>self.start]
                    self.asc = self.asc[self.asc['DateTime']<self.end]
                elif self.date1.isChecked()==True and self.time2.isChecked()==True:
                    self.asc.pop('Time')
                    self.asc.insert(loc=0, column='DateTime', value=self.dtime)
                    self.asc = self.asc[self.asc['DateTime']>self.start]
                    self.asc = self.asc[self.asc['DateTime']<self.end]
                    self.asc['DateTime']=self.asc['DateTime'].str.replace(':', ' ')
                elif self.date1.isChecked()==True and self.time3.isChecked()==True:
                    self.date3.setChecked(True)
                    self.asc.insert(loc=0, column='DateTime', value=self.asc['Time'])
                    self.asc = self.asc[self.asc['DateTime']>self.start]
                    self.asc = self.asc[self.asc['DateTime']<self.end]
                    self.asc.pop('Time')
                elif self.date2.isChecked()==True and self.time1.isChecked()==True:
                    self.asc.pop('Time')
                    self.asc.insert(loc=0, column='DateTime', value=self.dtime)
                    self.asc = self.asc[self.asc['DateTime']>self.start]
                    self.asc = self.asc[self.asc['DateTime']<self.end]
                    self.asc['DateTime']=self.asc['DateTime'].str.replace('-', ' ')
                elif self.date2.isChecked()==True and self.time2.isChecked()==True:
                    self.asc.pop('Time')
                    self.asc.insert(loc=0, column='DateTime', value=self.dtime)
                    self.asc = self.asc[self.asc['DateTime']>self.start]
                    self.asc = self.asc[self.asc['DateTime']<self.end]
                    self.asc['DateTime']=self.asc['DateTime'].str.replace(':', ' ')
                    self.asc['DateTime']=self.asc['DateTime'].str.replace('-', ' ')
                elif self.date2.isChecked()==True and self.time3.isChecked()==True:
                    self.asc.pop('Time')
                    self.asc.insert(loc=0, column='Date', value=self.dtime)
                    self.asc['DateTime']=self.asc[self.asc['DateTime']>self.start]
                    self.asc['DateTime']=self.asc[self.asc['DateTime']<self.end]  
                    self.asc['DateTime']=self.asc['DateTime'].str.replace('-', ' ')
                elif self.date3.isChecked()==True and self.time1.isChecked()==True:
                    self.asc.insert(loc=0, column='DateTime', value=self.asc['Time'])
                    self.asc = self.asc[self.asc['DateTime']>self.start]
                    self.asc = self.asc[self.asc['DateTime']<self.end]
                    self.asc.pop('Time')
                elif self.date3.isChecked()==True and self.time2.isChecked()==True:
                    self.asc.insert(loc=0, column='DateTime', value=self.asc['Time'])
                    self.asc = self.asc[self.asc['DateTime']>self.start]
                    self.asc = self.asc[self.asc['DateTime']<self.end]
                    self.asc.pop('Time')
                elif self.date3.isChecked()==True and self.time3.isChecked()==True:
                    self.asc.insert(loc=0, column='DateTime', value=self.asc['Time'])
                    self.asc = self.asc[self.asc['DateTime']>self.start]
                    self.asc = self.asc[self.asc['DateTime']<self.end]
                    self.asc.pop('Time')
                else:
                    pass
                self.averaging_window = self.averagingbox.text()

                if len(self.averaging_window)!=0:
                    self.averaging_window=int(self.averaging_window)
                    self.asc = self.asc.rolling(self.averaging_window).mean()
                    self.asc = self.asc.iloc[::self.averaging_window, :]
                else:
                    pass
                if self.header1.isChecked()==True:
                    if self.comma.isChecked()==True:
                        if self.fillvalue1.isChecked()==True:
                            self.asc.to_csv(self.output_file, header=True, index=False, na_rep='-32767.0')
                            with open(self.output_file) as preview:
                                head = str(preview.readlines()[0:10])
                                head = head.replace('\\n', '\n')
                            self.headerpreview.setText(head)
                        elif self.fillvalue2.isChecked()==True:
                            self.asc.to_csv(self.output_file, header=True, index=False, na_rep='')
                            with open(self.output_file) as preview:
                                head = str(preview.readlines()[0:10])
                                head = head.replace('\\n', '\n')                        
                            self.headerpreview.setText(head)
                        elif self.fillvalue3.isChecked()==True:
                            self.asc = self.asc.fillna(method='ffill')
                            self.asc.to_csv(self.output_file, header=True, index=False)
                            with open(self.output_file) as preview:
                                head = str(preview.readlines()[0:10])
                                head = head.replace('\\n', '\n')
                            self.headerpreview.setText(head)
                        else:
                            print('Error converting file: '+self.input_file)

                    elif self.space.isChecked()==True:
                        if self.fillvalue1.isChecked()==True:
                            self.asc.to_csv(self.output_file, header=True, index=False, na_rep='-32767.0', sep=' ')
                            with open(self.output_file) as preview:
                                head = str(preview.readlines()[0:10])
                                head = head.replace('\\n', '\n')
                            self.headerpreview.setText(head)
                        elif self.fillvalue2.isChecked()==True:
                            self.asc.to_csv(self.output_file, header=True, index=False, na_rep='', sep=' ')
                            with open(self.output_file) as preview:
                                head = str(preview.readlines()[0:10])
                                head = head.replace('\\n', '\n')
                            self.headerpreview.setText(head)
                        elif self.fillvalue3.isChecked()==True:
                            self.asc = self.asc.fillna(method='ffill')
                            self.asc.to_csv(self.output_file, header=True, index=False, sep=' ')
                            with open(self.output_file) as preview:
                                head = str(preview.readlines()[0:10])
                                head = head.replace('\\n', '\n')
                            self.headerpreview.setText(head)
                        else:
                            print('Error converting file: '+self.input_file)
                    else:
                        print('Error converting file: '+self.input_file)

                elif self.header2.isChecked()==True:
                    self.asc = self.asc.rename(columns={'DateTime': 'Start_UTC'})
                    self.asc.to_csv(self.output_file, header=True, index=False, na_rep='-99999.0')
                    try:
                        self.columns = pd.DataFrame(self.asc.columns.values.tolist())
                        self.header = self.header.loc[self.header[0].isin(self.columns[0])]
                        os.system('cp ./docs/header1.txt ./docs/header1.tmp')
                        os.system("ex -s -c '5i' -c x ./docs/header1.tmp")
                        os.system('cp ./docs/header2.txt ./docs/header2.tmp')
                        self.header.to_csv('./docs/header1.tmp', mode='a', header=False, index=False)
                        os.system('cat ./docs/header1.tmp ./docs/header2.tmp > ./docs/header.tmp')
                        os.system('mv '+str(self.output_file)+' '+str(self.output_file)+'.tmp') 
                        os.system('cat ./docs/header.tmp '+str(self.output_file)+'.tmp >> '+str(self.output_file))
                        os.system('rm ./docs/header.tmp ./docs/header1.tmp ./docs/header2.tmp '+str(self.output_file)+'.tmp')
                    except: 
                        print('Error creating and appending ICARTT header to output file.')
                    with open(self.output_file) as preview:
                        head = str(preview.readlines()[0:5])
                        head = head.replace('\\n', '\n')
                    self.headerpreview.setText(head)
                else:
                    pass 

#            processing_complete = QMessageBox()
#            processing_complete.setWindowTitle("Processing Successful")
#            processing_complete.setText("The ASCII file has been successfully written.")
#            x = processing_complete.exec_()
        except:
            processing_complete = QMessageBox()
            processing_complete.setWindowTitle("Error")
            processing_complete.setText("There was an error writing your ASCII file. Please try again.")
            x = processing_complete.exec_()
        else:
            pass

    #def loadBatchFile(self):
        # read: input filename
        # read: averaging
        # read: start time
        # read: end time
        # read: date format
        # read: time format
        # read: delimiter
        # read: missing value
        # read: header
        # populate each corresponding field before processing

    #def saveBatchFile(self):
        #self.inputfile

#######################################################################
# define main function
#######################################################################
def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = gui()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
