"""
Last edited on 2022-04-18 JTP

The following program formats the Agrimet data
Two main tasks
    1. Makes the timestamp always in Local Standard time (not daylight savings time)
    2. Subtracts the rain data to give an instantaneous rain amount

NOTE:
To create an executalbe in the command prompt type: 
    pyinstaller --hidden-import=openpyxl --onefile DSTtoLST.py
The executable doesn't like spaces, and funny characters in file/folder names
"""




# Load python packages
from json import load
#from tkinter.tix import COLUMN
import pandas as pd
import numpy as np
import datetime
import os 
import sys
import time
import datetime as dt # date time stuff

def subroutineadjustagriment(stationname):
    global rain
    
    # Define the parent folder
    parentfolder = 'C:\\Users\\KARMA\\Desktop\\SRML\\'

    
    # Define the data file
    loadthisfile = parentfolder + stationname#  + '_Agrimet.dat' #'CHO.dat' #_2022-03
    
    # Load the prn file 
    #df_prn = pd.read_csv(loadthisfile, sep=r',|\t', engine='python')
    #df_prn = pd.read_csv(loadthisfile, sep=r',|\t',header=None, engine='python')
    df_prn = np.array(pd.read_csv(loadthisfile, sep=r',|\t',header=None, engine='python'))

    # HEADER WAS REMOVED
    # ADDING HEADER BACK MIGHT FIX CODE?
    
    
    
    #df_prn = pd.read_csv(loadthisfile, delimiter = ';;', dtype = str, engine='python')

    # Get the rain data
    rain = df_prn[:,-1]
    #rain = np.array(df_prn.iloc[:,-1])
    
    # Compute the difference between adjacent minutes
   
    #rain = np.diff(rain)
    
    

    

    # Fix the rain data so that there isn't negative rain (what does that even mean)    
    # Initialize the mask
    ii = np.argmax(rain<0)
    
                   
    # Create a while loop that will go through the negative spots
    count = 0
    while 0<ii: #len([0]):#&iteration <100:
        count += 1
        # Find the negative spots
        ii = np.argmax(rain<0)
            # If there are not any negative values found then stop
        if 0==ii:
            break
        
        
        if count%100==0:
            print(count,ii)
        if count > 1000:
            break
                           
                            # Test to see if you have reached the end of the file
    if (len(rain)<=ii+1): #(iteration>1440) |
                                # Eliminate this negative point
        rain[ii] = 0
    else:
        # Add the negative rain to the next rain (The next rain could be -, 0, or +)
        # This moves the negative point towards the end of the the month
        rain[ii+1] = rain[ii]+rain[ii+1]
                               
        # Set the current location (the spot the negative rain) was to zero
        # you moved the negative spot to the right.
        rain[ii]= 0

    # Find all the places that are very close to zero 
                      
    mask = (-.00001 < rain) & (rain <.00001)
    # Set these very close places actually to zero.
    rain[mask] = 0

    # Put the precipitation back into the dataframe   
    #icol = pd.to_numeric(COLUMN, errors='coerce')
    #icol = COLUMN.fillna(0)
    #icol = COLUMN.at[icol]
    #icol = pd.Series(COLUMN)
    #df_prn[:,icol] = rain
    
    icolum = df_prn.shape[1]
    df_prn[:,-1] = rain
    #.iloc[icolum - 1,:] = rain


    # IT'S NOT COUNTING THE FIRST ROW PRINT IT AND LOOK AT OUTPUT
    
    #df_prn[:,COLUMN] = rain
    
    #df_prn[:, icolumn] = rain  #df.loc[44:,'Precipitation'] = precip
    # END of negative rain




    
    # Put the rain data back into the file
    # Force the beginning minute to be zero (the difference is one value shorter than the entire month)
    df_prn[0, -1] = 0
    #df_prn.iloc[0,-1] = 0
    # Put the rain data into the output file
    df_prn[0:, -1] = rain
    #df_prn.iloc[1:,-1] = rain
    
    # Get the year of the file
    year = df_prn.iloc[0,1]
    
    # Define the spring and fall time change days of the year
    if year==2022:
        springdoy = 72
        falldoy = 310
    elif year == 2023:
        springdoy = 71
        falldoy = 309
    elif year==2024:
        springdoy = 70
        falldoy = 308
    elif year==2025:
        springdoy = 68
        falldoy = 306
    elif year==2026:
        springdoy = 67
        falldoy = 305
    else:
        # You need to add more here in the future
        print('JOSH FIx the agrimet dailight savings time file here. ')
        sys.exit('line 73')
        
    # Define a DOY from the prn file
    doy = np.array(df_prn.iloc[:,2])
    # Define the time HHMM from the prn file
    time = np.array(df_prn.iloc[:,3])
        
    # Subtract 100 from all time stamps ( you will only use these subtracted times in the summer)
    lsttime = np.array(df_prn.iloc[:,3]-100)

    # Set the LST DOY to the same as the NON-LST (for 23 hours a day this is correct)
    lstdoy = np.array(df_prn.iloc[:,2])
    
    # Find the times when the LSTtime is less than zero 
    mask = lsttime<=0
    # Add 2400 to the extra small times (-30--> 2330)
    lsttime[mask] = lsttime[mask]+2400
    # Shift the DOY of these minutes as well
    lstdoy[mask] = lstdoy[mask] - 1
    
    # Find the days that are completly in the summer (don't look at the days when the time shift happens, we do that next)
    mask = (springdoy < df_prn.iloc[:,2]) & (df_prn.iloc[:,2] < falldoy)
    
    # For these days, replace the prn DOY with the LST DOY
    doy[mask] =  lstdoy[mask]
    # For these days, replace the prn time with the LST time
    time[mask] = lsttime[mask]
    
    # On the day of the spring time change, only get the times after 100 (the daytime values are wrong)
    mask = (springdoy == df_prn.iloc[:,2]) & (100 < df_prn.iloc[:,3])
    doy[mask] =  lstdoy[mask]
    time[mask] = lsttime[mask]
    
    # On the day of the spring time change, only get the times after 100 (the daytime values are wrong)
    mask = (falldoy == df_prn.iloc[:,2]) & (100 >= df_prn.iloc[:,3])
    doy[mask] =  lstdoy[mask]
    time[mask] = lsttime[mask]
    
    # Put the correct DOY and time back into the df_prn file
    df_prn.iloc[:,2] =doy
    df_prn.iloc[:,3] = time
    
    # Export the file out to the csv
    df_prn.to_csv(parentfolder + stationname.replace('_Agrimet', '') , header=False, index= False, float_format='%g')

   
# Define the parent folder

parentfolder =  'C:\\Users\\KARMA\\Desktop\\SRML\\'

#parentfolder = 'C:\\Users\\jpeters4\\Dropbox\\updatedformat\\'

# Get a list of all files in the folder
listoffiles = os.listdir(parentfolder)





for ifile in listoffiles:
    
    if ('CHO' in ifile):
        #print(ifile)
        subroutineadjustagriment(ifile)
    
    """if ('FGO' in ifile):
        #print(ifile)
        subroutineadjustagriment(ifile)"""
        
    """if ('MAO' in ifile):
        #print(ifile)
        subroutineadjustagriment(ifile)
    """
"""
# Go through each of the files
for ifile in listoffiles:
    
    if ('CHO.dat' in ifile) & ('_Agrimet' in ifile):
        print(ifile)
        subroutineadjustagriment(ifile)

    if ('FGO.dat' in ifile) & ('_Agrimet' in ifile):
        print(ifile)
        subroutineadjustagriment(ifile)
        
    if ('MAO.dat' in ifile) & ('_Agrimet' in ifile):
        print(ifile)
        subroutineadjustagriment(ifile)        
"""
