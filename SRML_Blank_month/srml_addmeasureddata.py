"""
Last edited on 2022-11-28 JTP

The following program adds the data to a monthly output file
The length of the file coresponds to the minutes in a month
The width of the file coresponds to the number of instruments (plus flags)
The program loads the current output file. Finds the last recorded minute (Where the previous run left off)
Then the program loads the .dat file and gets the data that we need.
The data is processed. Correct responsivities are applied. Adjustments are made, 
output file is updated
File is saved with new changes. 

NOTE:
To create an executalbe in the command prompt type: 
    pyinstaller --hidden-import=openpyxl --onefile srml_adddata.py
The executable doesn't like spaces, and funny characters in file/folder names
"""



"""
Keep track of changes write why and what changed

Create new file 
"""

# Load python packages
import pandas as pd
import numpy as np
import datetime
from calendar import monthrange
import pvlib
import os 
import sys
import time
import PySimpleGUI as sg # to make simple GUIs
import datetime as dt # date time stuff
from srml_makeblankmonth import subroutinegetsitefileinfo # Makes the blank month file




#%%
def subroutineloadcomprehensive(comprehensivelocation):
    # Load the comprehensive file (make it an array) (about .25 seconds)
    comprehensivefile = np.array(pd.read_csv(comprehensivelocation, header = None, dtype=object))
    
    # Search through the comments to see where the last data stopped
    mask = comprehensivefile[:,-1]=='NewDataStartsHere'
    
    # Get the stopping row of the old data (this is the starting row of the new data)
    compstartrow = np.array(range(len(comprehensivefile)))[mask][0]
    
    # Get the stopping date of the old data (This is the starting date of the new data)
    compstartdate = dt.datetime.strptime(comprehensivefile[compstartrow,2], "%Y-%m-%d--%H:%M:%S") #"%d %B, %Y")
    
    return comprehensivefile, compstartrow, compstartdate



# Function to read last N lines of the file
def subroutineloaddat(fname, compstartdate):
    '''
    Read the last N lines of a file. 
    Stop reading when you reach the previous stopping spot.

    Parameters
    ----------
    fname : TYPE
        DESCRIPTION.
    N : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''

    # Initialize a boolean if the dat data is not defined. (Used create a blank array the first time in)
    # This way we get the correct number of columns
    dat_datanotdefinedTF = True
    
    # Make an empty array for the dat data
    dat_dt = np.array([], dtype=object)

    # opening file using with() method, this will close the file when it is finished. 
    with open(fname) as file:
         
        # Read one line at a time. Starting at the bottom. 
        for line in (file.readlines() [-1::-1]):
            
            # Get rid of the end line character "\n"
            line = line.replace('\n','')            
            
            # split the data up by commas
            line = np.array(line.split(','), dtype=float)

            # Convert the the timestamp in this line to a dt timestamp
            # Give it the year, DOY and HHMM
            # Call it the temporary time stamp.
            dat_dt_temp = subroutineyeardoyhhmmtodatetime(line[1], line[2], line[3])

            # If this is the first time into this loop, then create a blank array            
            if dat_datanotdefinedTF:
                # Create the blank array, (make it the same size as the split data)
                dat_data = np.full((0, len(line)), 'NA', dtype=object)
                # Make sure you don't come in here next time.
                dat_datanotdefinedTF = False
                
            # Append the data to the dat_data array
            dat_data = np.vstack([dat_data, np.transpose(line)])

            
            # Append the timestamp to the dat timestamp array           
            dat_dt = np.append(dat_dt, dat_dt_temp)
            
            # Check to see if you reached the starting place in the comprehensive file
            if dat_dt_temp <= compstartdate:
                
                # If you reached the stopping place then stop looking through the dat file (You have the information you need)
                break
            

    # Reverse the order of the dat files. 
    # You added the data in reverse order, By switching the order here you are putting it in correct order
    dat_data = dat_data[::-1]
    dat_dt = dat_dt[::-1]

    return dat_data, dat_dt



def subroutineyeardoyhhmmtodatetime(year, doy, hhmm):
    year = int(year)
    
    if hhmm == 2400:
        doy = doy + 1
        hhmm = 0 
    
        
    doystring = str(int(doy))
    if doy<10:
        doystring = '00'+doystring
    elif doy<100:
        doystring = '0'+doystring
    
    hour = int(hhmm/100)
    minute = int(hhmm%100)
    
    
    
    if hour < 10:
        hourstring = '0' + str(hour)
    else:
        hourstring = str(hour)
        
    if minute < 10:
        minutestring = '0' + str(minute)
    else:
        minutestring = str(minute)                
        

    dat_dt = dt.datetime.strptime(str(year) + '-' + doystring + '--' + hourstring + ':' + minutestring, "%Y-%j--%H:%M") #"%d %B, %Y")
    
    return dat_dt



#%%
def subroutineloadsite(sitefilelocation, dat_dt):
    # Load the sitefile (about .6 seconds the first time, .05 seconds the second)
    sitefile_complete = np.array(pd.read_excel(sitefilelocation, engine='openpyxl'))
    
    # Get the correct sitefile information for this file (this is the information about the columns in the .dat file)    
    # This is a subroutine from the make blank month .py file (loaded when the program started)
    instrumentelementnumbers, instrumentserialnumbers, instrumentshorthand, instrumentprnmultiplier, instrumentshouldbemultiplier, instrumentuncertainty = subroutinegetsitefileinfo(sitefile_complete, dat_dt[0])            
    
    instrumentelementnumbersend, instrumentserialnumbersend, instrumentshorthandend, instrumentprnmultiplierend, instrumentshouldbemultiplierend, instrumentuncertaintyend = subroutinegetsitefileinfo(sitefile_complete, dat_dt[-1])            
    if len(instrumentprnmultiplier)!= len(instrumentprnmultiplierend):
        print('The sitefile changed, THe number of elements is different')
        time.sleep(10)
        sys.exit('line 260')
    
    if np.logical_not(np.array_equal(instrumentprnmultiplier.astype(float),instrumentprnmultiplierend.astype(float), equal_nan=True)):
        print('sitefile prn Multiplier changed')
        time.sleep(10)
        sys.exit('line 266')
        
    if np.logical_not(np.array_equal(instrumentshouldbemultiplier.astype(float),instrumentshouldbemultiplierend.astype(float), equal_nan=True)):
        print('sitefile shouldbe Multiplier changed')    
        time.sleep(10)
        sys.exit('line 271')
            
    return instrumentelementnumbers, instrumentserialnumbers, instrumentshorthand, instrumentprnmultiplier, instrumentshouldbemultiplier, instrumentuncertainty




def subroutinecheckdata(comprehensivefile,compstartrow, dat_dt, dat_data):
    # Get the time interval of the comp file (Convert it to seconds)
    timeinterval = float(comprehensivefile[7,1])*60
    
    station = comprehensivefile[1,1] # [1,1] station name [2,1] station location
    YearMonth = comprehensivefile[8,1]
        
    # Check to make sure that the dat file has all the minutes    
    for idt in range(len(dat_dt)-1):
        # If the two lines are not 61 seconds apart then stop the code
        if ((dat_dt[idt+1] - dat_dt[idt]).total_seconds() != timeinterval):
            print((dat_dt[idt+1] - dat_dt[idt]).total_seconds())
            print('The timestamp of the dat file is not continuous.')
            print('There are missing or extra minutes')
            print('station: ', station, ' Year//Month: ', YearMonth)
            print(dat_data[idt])
            print(dat_data[idt+1])
            print('Make adjustments to the .dat file')
            print('line in code: 213')
            time.sleep(10)
            sys.exit('line 218')
            
    
    # Get the comprehensive end row. Make sure it doesn't go beyond the end of the file
    compendrow = np.min((len(comprehensivefile), compstartrow + len(dat_data)))
    
    return compendrow



def subroutineadddatdata(comprehensivefile, compstartrow, compendrow, dat_data, instrumentelementnumbers, instrumentprnmultiplier, instrumentshouldbemultiplier):
    # Go through all the columns in the comprehnsive file (start with column 7, skip the flag columns)
    for icolumnoutput in range(7,comprehensivefile.shape[1],2):

        # Check to see if the column is measured
        if 'MeasuredColumn' == comprehensivefile[8,icolumnoutput]:
    
            # Go through all the columns of the sitefile (coresponding to the columns in the dat file)
            for icolumnsite in range(len(instrumentelementnumbers)):
                
                # Check to see if the sitefile column coresponds to this column of the comprehensive file
                if str(instrumentelementnumbers[icolumnsite])==str(comprehensivefile[1,icolumnoutput].replace('_original','')):

                    pastethis = np.trunc((dat_data[:,icolumnsite+4] * instrumentshouldbemultiplier[icolumnsite] / instrumentprnmultiplier[icolumnsite]) * 100) / (100) 
                    # print(pastethis)
                    comprehensivefile[compstartrow:compendrow,icolumnoutput] = pastethis                
                    comprehensivefile[compstartrow:compendrow,icolumnoutput+1] = 1
        
        
    comprehensivefile[compstartrow,-1] = '-'    
    comprehensivefile[compendrow-1,-1] = 'NewDataStartsHere'    
    
    return comprehensivefile



def subroutineaddmeasureddata(comprehensivelocation, datlocation, sitefilelocation):
    # Load the comprehensive file
    comprehensivefile, compstartrow, compstartdate = subroutineloadcomprehensive(comprehensivelocation)
    
    # Get the current data from the dat file. (takes about .01 seconds)
    dat_data, dat_dt = subroutineloaddat(datlocation, compstartdate)
    
    instrumentelementnumbers, instrumentserialnumbers, instrumentshorthand, instrumentprnmultiplier, instrumentshouldbemultiplier, instrumentuncertainty = subroutineloadsite(sitefilelocation, dat_dt)
    
    compendrow = subroutinecheckdata(comprehensivefile, compstartrow, dat_dt, dat_data)
    
    subroutineadddatdata(comprehensivefile, compstartrow, compendrow, dat_data, instrumentelementnumbers, instrumentprnmultiplier, instrumentshouldbemultiplier)
    
    # Save the output file 
    np.savetxt(comprehensivelocation, comprehensivefile, delimiter=',', fmt='%s')





if __name__ == "__main__":
    # To stop the imported file from running

    sitefilefolder = 'C:\\Users\\KARMA\\Desktop\\SRML_Blank_month\\'

    comprehensivelocation = sitefilefolder + 'SAO_2023-04_ComprehensiveFormat.csv'

    # Grabs dat location from bat file 
    datlocation = sitefilefolder + sys.argv[1]
    
    # print(sys.argv[1])

    sitefilelocation = sitefilefolder + 'SAO_consolodated_sitefile.xlsx'

    subroutineaddmeasureddata(comprehensivelocation, datlocation, sitefilelocation)   

