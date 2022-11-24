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


#%%

# Load python packages
import pandas as pd
import numpy as np
import datetime
import os 
import sys
import time
import datetime as dt # date time stuff
import copy

def subroutineadjustagriment(stationname, subtract_rain):
    global rain_diff
    global ii

    # Define the parent folder
    parentfolder = 'C:\\Users\\KARMA\\Desktop\\SRML\\'

    # Define the data file
    loadthisfile = parentfolder + stationname#  + '_Agrimet.dat' #'CHO.dat' #_2022-03
    
    # Load the prn file 
    df_prn = np.array(pd.read_csv(loadthisfile, sep=r',|\t',header=None, engine='python'))

    # Get the rain data
    rain = df_prn[:,-1]
    
    # Checks to see if the file actually went through, CAN DELETE IF YOU WANT TO.
    print("First ten lines ",rain[0:10])
    print("Last line",df_prn[-1])
    
    
    # Compute the difference between adjacent minutes
    if subtract_rain:
        # Fills the rain_diff column with all 0.0
        rain_diff = np.full(len(rain), 0.0)

        # Fills rain_diff with the difference between number ahead of it and the currnet number [i + 1] - [i]
        rain_diff[0:-1] = np.diff(rain)
    else:
        rain_diff = copy.copy(rain)
        
    
    # Fix the rain data so that there isn't negative rain (what does that even mean)    
    # Initialize the mask
    ii = np.argmax(rain_diff<0)

    
    # Create a while loop that will go through the negative spots
    count = 0
    while 0 < ii: #len([0]):#&iteration <100:
        count += 1

        # Find the negative spots
        ii = np.argmax(rain_diff<0)
        
        # If there are not any negative values found then stop
        if 0==ii:
            break
        
        
        # Test to see if you have reached the end of the file
        if (len(rain_diff)<=ii+1): #(iteration>1440) |
            # Eliminate this negative point
            rain_diff[ii] = 0
        
        else:
            # Add the negative rain to the next rain (The next rain could be -, 0, or +)
            # This moves the negative point towards the end of the the month
            rain_diff[ii+1] = rain_diff[ii]+rain_diff[ii+1]
                
            # Set the current location (the spot the negative rain) was to zero
            # you moved the negative spot to the right.
            rain_diff[ii]= 0
            
        

    

    # Find all the places that are very close to zero 
    mask = (-.00001 < rain_diff) & (rain_diff <.00001)
    # Set these very close places actually to zero.
    rain_diff[mask] = 0
    
    # Put the precipitation back into the dataframe  
    df_prn[:,-1] = rain_diff
    # END of negative rain




    
    # Put the rain data back into the file
    # Force the beginning minute to be zero (the difference is one value shorter than the entire month)
    df_prn[0, -1] = 0


    # Put the rain data into the output file
    df_prn[0:, -1] = rain_diff
    
    
    # Get the year of the file
    year = df_prn[0,1]
    
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
    doy = df_prn[:,2]

    # Define the time HHMM from the prn file
    time = df_prn[:,3]

    # Subtract 100 from all time stamps ( you will only use these subtracted times in the summer)
    lsttime = df_prn[:,3] - 100

    # Set the LST DOY to the same as the NON-LST (for 23 hours a day this is correct)
    lstdoy = df_prn[:,2]

    # Find the times when the LSTtime is less than zero 
    mask = lsttime<=0

    # Add 2400 to the extra small times (-30--> 2330)
    lsttime[mask] = lsttime[mask]+2400
    # Shift the DOY of these minutes as well
    lstdoy[mask] = lstdoy[mask] - 1
    
    # Find the days that are completly in the summer (don't look at the days when the time shift happens, we do that next)
    mask = (springdoy < df_prn[:,2]) & (df_prn[:,2] < falldoy)

    # For these days, replace the prn DOY with the LST DOY
    doy[mask] =  lstdoy[mask]
    # For these days, replace the prn time with the LST time
    time[mask] = lsttime[mask]
    
    # On the day of the spring time change, only get the times after 100 (the daytime values are wrong)
    mask = (springdoy == df_prn[:,2]) & (100 < df_prn[:,3])
    doy[mask] =  lstdoy[mask]
    time[mask] = lsttime[mask]
    
    # On the day of the spring time change, only get the times after 100 (the daytime values are wrong)
    mask = (falldoy == df_prn[:,2]) & (100 >= df_prn[:,3])

    doy[mask] =  lstdoy[mask]
    time[mask] = lsttime[mask]
    
    # Put the correct DOY and time back into the df_prn file
    df_prn[:,2] = doy
    df_prn[:,3] = time
    
    # Export the file out to the csv/dat
    pd.DataFrame(df_prn).to_csv(parentfolder + stationname.replace('_Agrimet.dat', '.dat') , header=False, index= False, float_format='%g')

    
    

def fileAppend(fileToTakeFrom, fileToAddTo):

    # Define the parent folder
    parentfolder = 'C:\\Users\\KARMA\\Desktop\\SRML\\'

    # Define the data file (Opening the output dat file)
    fileTake = parentfolder + fileToTakeFrom#  + '_Agrimet.dat' #'CHO.dat' #_2022-03
    
    fileAdd = parentfolder + fileToAddTo

    # Load the prn file 
    # Pandas
    df_take = pd.read_csv(fileTake , sep=r',|\t',header=None, engine='python')

    df_add = pd.read_csv(fileAdd, sep=r',|\t',header=None, engine='python')

    # Numpy
    #df_take = np.array(pd.read_csv(fileTake, sep=r',|\t',header=None, engine='python'))

    #df_add = np.array(pd.read_csv(fileAdd, sep=r',|\t',header=None, engine='python'))

    # Finds last line in first file
    last_line_take = df_take.iloc[-1]
    print(last_line_take)



    row_num = 0 

    for row in df_add:
        # AXIS 0 MEANS ROWS AND AXIS 1 MEANS COLUMNS
        delete_row = df_take.iloc[row_num]
        df_add.drop([delete_row])
        
        delete_row += 1

        # The last line is stopped at the front of the next file (WHY?)
        # If the last line is equal to a line in df_add then it will break
        # because then we've found where the previous file last left off
        if (last_line_take.all() == row[delete_row]):
            print(last_line_take)
            print(row)
            print("here")
            break


    # START FROM BOTTOM
    # delete_row = 0 
    # for row in df_add:
    #     # AXIS 0 MEANS ROWS AND AXIS 1 MEANS COLUMNS
    #     df = np.delete(df_add, delete_row, axis = 0)
    #     delete_row += 1

    #     # The last line is stopped at the front of the next file (WHY?)
    #     # If the last line is equal to a line in df_add then it will break
    #     # because then we've found where the previous file last left off
    #     if (last_line_take.all() == row[delete_row]):
    #         print(last_line_take)
    #         print(row)
    #         print("here")
    #         break

    #print(df)
    # last_line_add = df_add[-1]

    # print(last_line_take)

    # print(last_line_add)

    # # Finds number of lines
    # num_lines_take = sum(1 for line in df_take)
    # print(num_lines_take)

    # num_lines_add = sum(1 for line in df_add)
    # print(num_lines_add)

    
    #pd.DataFrame(df).to_csv(parentfolder + fileToAddTo.replace('.dat', 'new.dat') , header=False, index= False, float_format='%g')
    


# Define the parent folder
parentfolder =  'C:\\Users\\KARMA\\Desktop\\SRML\\'
#parentfolder = 'C:\\Users\\jpeters4\\Dropbox\\updatedformat\\'

# Get a list of all files in the folder
listoffiles = os.listdir(parentfolder)



# subroutineadjustagriment('CHO1_Agrimet.dat', True)
# subroutineadjustagriment('CHO2_Agrimet.dat', True)
# subroutineadjustagriment('CHO3_Agrimet.dat', True)
# subroutineadjustagriment('CHO4_Agrimet.dat', True)

fileAppend('CHO1.dat', 'CHO2.dat')
# fileAppend('CHO2.dat')
# fileAppend('CHO3.dat')
# fileAppend('CHO4.dat')
"""    
# Creates the output files
for ifile in listoffiles:
    
    if ('CHO_Agrimet.dat' in ifile):
        subroutineadjustagriment(ifile, True)
    
    if ('FGO_Agrimet.dat' in ifile):
        subroutineadjustagriment(ifile, True)

    # Weird issue with HNO If I don't format it properly it causes a issue on line 118123 
    # Only happening for HNO as of now but could cause issues for future files
    # pandas.errors.ParserError: Expected 12 fields in line 118123, saw 13. Error could possibly be due to quotes being ignored when a multi-char delimiter is used. 
    if ('HNO_Agrimet.dat' in ifile):
       subroutineadjustagriment(ifile, True) 
    
    if ('MAO_Agrimet.dat' in ifile):
        subroutineadjustagriment(ifile, True)  
"""
   

# %%
