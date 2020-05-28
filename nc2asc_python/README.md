### Program to convert netCDF to ASCII

nc2asc includes a GUI that allows a user to read in an existing netCDF file contaning time dimension data, select an output directory and output file name, and then define the processing options of the resulting ASCII file. The processing options are presented as radio buttons.

If the ICARTT option is selected under the "Header" section, then the corresponding ICARTT options for the other sections are automatically selected. 

The user has the ability to sub-select vars from the complete list via the table on the right side of the GUI. Clicking on a cell in a given row saves that variable into memory, and the list of variables is appended with each subsequent variable selected by the user while holding down CTRL. If the user wishes to process all available variables in the input file, they can click the button 'Select All' located above the table on the right hand side. This highlights all variables in the table as well as saves the complete list of variables into the processing options. 

When the user is done processing their file, they can click the 'Exit' button on the bottom of the GUI. 
