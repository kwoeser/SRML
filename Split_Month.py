"""
Created on Mon May  2 13:49:13 2022
@author: jpeters4
The following program 
1. copies the existing .dat files to the step2A folder
2. Splits the file on the month mark
3. The Previous month data is put in the previous folder (Step2B)
4. The current month data is put back into the Step1 folder
5. Agrimet Stations that have Daylight savings time are handled correctly.

To make a python executable
pyinstaller --hidden-import=openpyxl --onefile Split_Month.py
"""

# Load python packages
import pandas as pd
import numpy as np
import datetime as dt
import os 
import sys
import time
import shutil

# Define the parent folder of the data
parentfolder = 'E:\\Data\\'
#parentfolder = 'C:\\Users\\jpeters4\\Dropbox\\Python\\Split_Months\\'

# Get the current date
# Ideally this program will be run, near the first of the month
# So, the current date should be similar to the dates in the file
now = dt.datetime.now()
currentyear = now.year
currentmonth = now.month

# If you want to manually set the date 
# currentyear = 2024
# currentmonth = imonth

# We are going to be splitting out the previous dates
# Define the previous year/month date from the current values
if currentmonth==1:
    # If it is Janurary, then the previous year is year - 1
    previousyear = currentyear - 1
else:
    # For all other months, the previous year is the same as the current year
    # previous year is the year value of the previous month (often times this is the same year)
    previousyear = currentyear 

# If the currentmonth is Janurary, the previous month is December
if currentmonth==1:
    previousmonth = 12
else:
    # For all other months, simply subtract 1 from the month number
    previousmonth = currentmonth - 1
    
# Define a list of day of the year values for the first day of each month 
# (we will deal with the leap years in a moment)
doyfdomarray = np.array([1,32,60,91,121,152,182,213,244,274,305,335])

# Define the first day of the month value for the current month
currentdoyfdom =  doyfdomarray[currentmonth-1]
# Define the previous month
previousdoyfdom =  doyfdomarray[previousmonth-1]

# If the current year is a leap year (and the month is larger than Feb, then add one to the first day of them onth value)
if (currentyear%4==0) & (currentmonth>2):
    currentdoyfdom = currentdoyfdom + 1

# Previous year    
if (previousyear%4==0) & (previousmonth>2):
    previousdoyfdom = previousdoyfdom + 1


# ****************************************************************************
# Define the location of the step1 file
folder1 = parentfolder + 'Step1_CampbellRaw\\'
# Make sure the folder exists
if np.logical_not(os.path.isdir(folder1)):
    print('****************************************************************************')
    print('Step 1 folder location not found (line 80)')
    print(folder1)
    print('*******************************Pause 20 seconds before exit *********************************************')
    time.sleep(20)
    sys.exit('line 84')

# Define the location of the step 2A folder
folder2A = parentfolder + 'Step2A_Raw_Before_Split\\'
if np.logical_not(os.path.isdir(folder2A)):
    print('****************************************************************************')
    print('Step 2A folder location not found (line 90)')
    print(folder2A)
    print('***********************Pause 20 seconds before exit ************************')
    time.sleep(20)
    sys.exit('line 94')
    
# Define the location of the step 2B folder
folder2B = parentfolder + 'Step2B_Raw_After_Split\\'
if np.logical_not(os.path.isdir(folder2B)):
    print('****************************************************************************')
    print('Step 2B folder location not found (line 100)')
    print(folder2B)
    print('***********************Pause 20 seconds before exit ************************')
    time.sleep(20)
    sys.exit('line 104')

# Get a list of all files in the folder
listoffiles = os.listdir(folder1)

# Go through each of the files
for ifile in listoffiles:
    
    print(ifile)

    # Get the station folder name from the file
    subfoldername = ifile.replace('.dat','')

    # Some of the stations have multiple loggers or bad filenames (fix the name problems)
    if subfoldername =='AWO_RT':subfoldername='AWO'
    if subfoldername =='EUOB':subfoldername='EUO'
    if subfoldername =='EUORSP':subfoldername='EUO'
    if subfoldername =='HNO':subfoldername='HEO'
    if subfoldername =='PSOPV':subfoldername='PSO'
    if subfoldername =='Ref_Cell_PV_Avg_UO':subfoldername='Ref_Cell'
    if subfoldername =='Ref_Cell_PV_Samp_UO':subfoldername='Ref_Cell'

    # Determine the subfolder to put the data    
    # Station\\Station_Year
    subfoldername = subfoldername +'\\' +subfoldername+'_'+ str(previousyear)

    # Define the location you are going to put the Step 2A file        
    paste2Alocation = folder2A + subfoldername 

    # If the directory doesn't exist then create it
    if np.logical_not(os.path.isdir(paste2Alocation)):
        os.makedirs(paste2Alocation)            

    # Add the file name to the ending.        
    # folder\\Step2A_Station_TodaysDate.dat        
    paste2Alocation = paste2Alocation + '\\' + ifile.replace('.dat','_') + dt.datetime.now().strftime("%Y-%m-%d")+ '_Step2A.dat'

    # Get the filename
    getthisfile = folder1 + ifile 

    # Copy the file
    # This is the file exactly as it currently is
    shutil.copyfile(getthisfile, paste2Alocation)

    # Assume that you are going to split each file
    skipfile = False
    # Don't split the AWO_RT File ( It has a different timestamp format)   
    if 'AWO_RT' in ifile:
        skipfile = True
     
    # Assume that the year information is in column 1
    yearcolumn = 1
    # Assume the DOY information is in column 2
    doycolumn = 2
    # Assume the HHMM information is in column 3
    hhmmcolumn = 3
    # The EKO file has different column numbers
    if 'EKO_Spectro' in ifile:
        yearcolumn = 0
        doycolumn = 1
        hhmmcolumn = 2
        
    # Decide if you are going to split this file
    if np.logical_not(skipfile):

        # Load the file
        df = pd.read_csv(getthisfile, header=None, sep=None , engine= 'python', dtype=str)

        # Make sure the file starts in the previous year
        if int(df.iloc[0,yearcolumn])!=previousyear:
            print('Previous year is incorrect. Check start of file')
            print(getthisfile)
            print(df.iloc[0:4,0:5])
            print('***********************Pause 20 seconds before exit ************************')
            time.sleep(20)
            break

        # Make sure the file starts in the previous month
        if int(df.iloc[0,doycolumn])!=previousdoyfdom:
            print('Previous month is incorrect. Check start of file')
            print(getthisfile)
            print(df.iloc[0:4,0:5])
            time.sleep(20)
            print('***********************Pause 20 seconds before exit ************************')            
            break
        
        # Make sure the file starts one minute into the day (hhmm ==1) (the agrimet stations can start at 101)
        if np.logical_not((int(df.iloc[0,hhmmcolumn])==1) | (int(df.iloc[0,hhmmcolumn])==101)):
            print('File does not start one minute after midnight. Check start of file')
            print(getthisfile)
            print(df.iloc[0:4,0:5])
            time.sleep(20)
            print('***********************Pause 20 seconds before exit ************************')            
            break
        
        # # Josh put something here to deal with the end of the file (don't split files that don't have the end of the month, but also you have to deal with the new year too. )
        # if currentmonth>1:
        #     if df.iloc[-1,doycolumn]<=currentdoyfdom:
        #         print('Current month is incorrect. Check end of file')
        #         print(df.iloc[0:-1:1440,0:5])
        #         break
        
   
        # Find the start of the previous month (the row number)
        # Find the previous year, and previous month, (Get the first place it occurs)
        startprevious = np.where((df.iloc[:,yearcolumn]==str(previousyear)) & (df.iloc[:,doycolumn]==str(previousdoyfdom)))[0][0]
        
        # Find the last minute of the previous month 
        # The last day of the previous month is very close to the start of the current month
        # The way that that python handles rows in taking part of arrays this works
        endprevious = np.where((df.iloc[:,yearcolumn]==str(currentyear)) & (df.iloc[:,doycolumn]==str(currentdoyfdom)))[0][0]

        # If Agrimet station, then the time is in dailight savings time, 
        agrimetstationTF = False
        if ('CHO' in ifile): agrimetstationTF = True
        if ('FGO' in ifile): agrimetstationTF = True
        if ('HNO' in ifile): agrimetstationTF = True
        if ('MAO' in ifile): agrimetstationTF = True
        if ('PAI' in ifile): agrimetstationTF = True    
        if ('PII' in ifile): agrimetstationTF = True
        if ('TWI' in ifile): agrimetstationTF = True  

        # If the station is in Daylight savings time then shift the start/end times by an hour.
        if agrimetstationTF: 

            # Define a list of daylight savings times days of the year (year, startDOY, endDOY)
            dstdates = np.array([[2022,72,310],[2023,71,309],[2024,70,308],[2025,68,306],[2026,67,305]])

            # Make sure the list is still valid
            if previousyear>2026:
                print("Add more dates to the daylight savings time list here (line 231)")
                time.sleep(60)
                sys.exit('line 228')
        
            # For a given year define the start and end dst DOY    
            dstmask = dstdates[:,0]==previousyear
            dststart = dstdates[dstmask,1][0]
            dstend = dstdates[dstmask,2][0]
    
            # Dec, Jan, Feb the dates are good
            # March, The start is good. The end needs to be shifted to the right
            # Apr, May, June, July, Aug, Sept, Oct, the start and end need to be shifted
            # Nov the start needs to be shifted the end is good
            # We don't change the dates here, we simply get the correct row numbers, so that after the dates are shifted the files have a complete month
    
            # If the previous month was winter (jan, feb, Dec)
            if (previousmonth <= 2) | (previousmonth == 12):
                1+1
            elif (3 == previousmonth):
                endprevious = endprevious + 60
            elif (4 <= previousmonth) & (previousmonth <= 10):
                startprevious =startprevious  + 60
                endprevious = endprevious + 60
            elif (11 == previousmonth):
                startprevious =startprevious  + 60

        # Find the start of the current month
        # Because python starts counting at 0 (not 1) and because the ending row in a selecting from a data frame is one less this works out.
        startcurrent = endprevious         
        
        # Define the location you are going to put the Step 2B file        
        paste2Blocation = folder2B + subfoldername 

        # If the directory doesn't exist then create it
        if np.logical_not(os.path.isdir(paste2Blocation)):
            os.makedirs(paste2Blocation)            

        # Create a month string with a leading zero for single digit months
        if previousmonth<10: 
            previousmonthstring = '0' +str(previousmonth)
        else:
            previousmonthstring = str(previousmonth)
        
        # Add the file name to the ending.        
        paste2Blocation = paste2Blocation + '\\' + ifile.replace('.dat','_') + str(previousyear) + '-' + previousmonthstring +'.dat'

        # Define the previous month's data as a dataframe        
        outputprevious = df.iloc[startprevious: endprevious]
        # Export the previous months data to a .dat file
        outputprevious.to_csv(paste2Blocation, index=False, header= False, na_rep='NA')    

        # Define where to put the current months data
        paste1location = getthisfile.replace('CampbellRaw','CampbellRaw')
        # Define the current months data         
        outputcurrent = df.iloc[startcurrent:]
        # Put the current months data back in its original location
        outputcurrent.to_csv(paste1location, index=False, header= False, na_rep='NA')    
