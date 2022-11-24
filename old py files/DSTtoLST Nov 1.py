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
# from json import load
# from re import T
#from tkinter.tix import COLUMN
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
    
    # Define the parent folder
    parentfolder = 'C:\\Users\\KARMA\\Desktop\\SRML\\'

    
    # Define the data file
    loadthisfile = parentfolder + stationname#  + '_Agrimet.dat' #'CHO.dat' #_2022-03
    
    # Load the prn file 
    df_prn = np.array(pd.read_csv(loadthisfile, sep=r',|\t',header=None, engine='python'))

    # HEADER WAS REMOVED
    # ADDING HEADER BACK MIGHT FIX CODE?
    
    # Get the rain data. Goes to last column
    # [first_row:last_row , column_0] 
    rain = df_prn[:,-1]
    print(rain)
    
    """# Compute the difference between adjacent minutes
    if subtract_rain:

        # rain = np.flip(rain)
        # rain[0] = 34.66;
        # np.flip(rain)
        # rain[0] = 34;
        # zero_rain = rain.fill(0)
        rain_diff = np.full(len(rain) , 0)
        rain_diff[0:-1] = np.diff(rain)
        print(rain_diff)
        print("True here")
    else:
        rain_diff = copy.copy(rain)
        #rain_diff[:-1] = np.diff(rain)"""


    if subtract_rain:
        # fills with 0's
        #rain_diff = np.full(len(rain), 0)
        #rain_diff = np.diff(rain)
        #print(rain_diff)

        """rain_diff[num] = rain[num + 1] - rain[num]
        IndexError: index 106059 is out of bounds for 
        axis 0 with size 106059"""
        
        rain_diff = rain.reshape(len(rain))
        print(rain_diff)
        #np.swapaxes(rain_diff, 0)

        for i in range(len(rain)):
            if i == len(rain):
                break
            else:

                #np.array 



                rain_diff = np.subtract(rain_diff, rain)

        print(rain_diff)



        """for i in range(len(rain)):
            if i == len(rain):
                break
            else:
                #rain_diff = np.diff(rain)
                #np.append(rain_diff, np.diff(rain))
                rain_diff[i] = rain[i+1] - rain[i]"""
                

        #if rain_diff.size > 0:
            #np.append(rain_diff, np.diff(rain))
            #for i in range(len(rain_diff)):
                #rain_diff[i] = rain[i + 1] - rain[i]
                #rain_diff = np.append(rain_diff, np.diff(rain))
        #else:
            #print("size 0")


        #print(rain_diff)
    else:
        rain_diff = copy.copy(rain)
    
        #rain_diff[:-1] = np.diff(rain)
        
    sys.exit()

    # Fix the rain data so that there isn't negative rain (what does that even mean)    
    # Initialize the mask

    #if the max argument of rain_diff is negative 
    ii = np.argmax(rain_diff<0)
          
    # Create a while loop that will go through the negative spots
    count = 0

    while 0 < ii: #len([0]):#&iteration <100:
        print(ii)
        
        count += 1
        # Find the negative spots
        ii = np.argmax(rain_diff<0)
        print("next string")
    
        # If there are not any negative values found then stop
        if 0==ii:
            break
        
        
        if count % 1000==0:
            print(count, ii)
        if count > 10000:
            count = 0
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

        

    #sys.exit()

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
    #df_prn.iloc[1:,-1] = rain
    
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
    
    # Export the file out to the csv
    pd.DataFrame(df_prn).to_csv(parentfolder + stationname.replace('_Agrimet.dat', '.dat') , header=False, index= False, float_format='%g')
   

# Define the parent folder
parentfolder =  'C:\\Users\\KARMA\\Desktop\\SRML\\'
#parentfolder = 'C:\\Users\\jpeters4\\Dropbox\\updatedformat\\'

# Get a list of all files in the folder
listoffiles = os.listdir(parentfolder)



# CHANGE NEW FILES TO HAVE _ARGIMET.dat AT THE END (CHO_ARGIEMNT.dat)
    
#subroutineadjustagriment('CHO.dat', False)
#subroutineadjustagriment('FGO.dat', True)

# Returns 0's
#subroutineadjustagriment('HNO.dat', True)

#subroutineadjustagriment('MAO.dat', False)

for ifile in listoffiles:
    
    # if ('CHO_Agrimet.dat' in ifile):
    #     subroutineadjustagriment(ifile, True)
    
    if ('HNO_Agrimet.dat' in ifile):
        subroutineadjustagriment(ifile, True) 

    if ('FGO_Agrimet.dat' in ifile):
        subroutineadjustagriment(ifile, True)
        
    if ('MAO_Agrimet.dat' in ifile):
        subroutineadjustagriment(ifile, True)  

   

# %%
