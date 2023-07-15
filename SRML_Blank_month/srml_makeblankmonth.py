"""
Last edited on 2022-11-07 JTP

The following program creates a blank monthly output file
The length of the file coresponds to the minutes in a month
The width of the file coresponds to the number of instruments (plus flags))
The instrument information is put into the header
The data area is left blank. This will be filled in during the month.

NOTE:
To create an executalbe in the command prompt type: 
    pyinstaller --hidden-import=openpyxl --onefile subroutinemakemonthblankfile.py
The executable doesn't like spaces, and funny characters in file/folder names
"""

# Load python packages
import pandas as pd
import numpy as np
import pvlib # Solar sun stuff
import os 
import sys
import time
import datetime as dt # date time stuff
from datetime import timedelta
from dateutil.relativedelta import relativedelta


#%%    
# 1. Get a list of datetime values for this month
def subroutinecreatedatetimes(year, month, timeinterval):
    '''
    Gets the current date. Then computes a monthly file for this month
    Generates a list of datetime values for this month
    Do this once before the station loop
    
    Returns 
    daterange, doyfod, yearfoy, datetime_ymdhms
    '''
    
    print('Inside 1. subroutinecreatedatetimes')

    # Decide how many days are in the current year
    if year%4==0:
        daysinyear = 366
    else:
        daysinyear = 365
    
    # Create a start date string value (Starts one minute after midnight)
    startdate = dt.datetime(year=year, month=month, day=1, hour=0, minute=1)

    # Create an end date string value (ends at midnight)    
    enddate = startdate + relativedelta(months=1) + relativedelta(minutes=-1)
 
    # Get the frequency of the data set (make sure it is one minute)
    if timeinterval == 1:
        # 'T' Is one minute frequency
        freq = 'T'
    else:
        # If it is not one minute then put up an error message and stop the program
        print('Time interval not one minute (line 68)')
        print('program stopped, srml_makeblankmonth.py')

        # Station missing?? variable name is shown in main()
        # print('station: ', station)
        time.sleep(30)
        sys.exit('line 59')

    # Create a list of datetime values 
    daterange = pd.date_range(start=startdate, end=enddate, freq= freq)

    # Compute the date difference between the minutes in the month and the start of the year
    datedif = daterange - daterange[1].replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    # Compute the year.fraction of year
    yearfoy = year + (datedif/daysinyear).total_seconds() / timedelta(days=1).total_seconds()
    
    # Round the fraction of a year to 10 decimals
    yearfoy = np.trunc((yearfoy) * 10**10) / (10**10)
    
    # Compute the date difference in seconds
    doyfod = (datedif.total_seconds() / timedelta(days=1).total_seconds()) + 1
    
    # Round to 7 decimal places
    doyfod = np.trunc((doyfod) * 10**7) / (10**7)

    # Datetime in special string formating
    # Josh if you were going to change 00:00:00 to 24:00:00, this is where you would do it.
    datetime_ymdhms = np.array(daterange.strftime("%Y-%m-%d--%H:%M:%S"))
    
    return daterange, doyfod, yearfoy, datetime_ymdhms

#%%

# 2. Get general information about this station from the sitefile
def subroutinecreateheaderoutput(sitefilename, daterange, year, month, timeinterval):
    '''
    Load the sitefile. The sitefile contains a lot of information about the station. 
    Station location
    Create an output header file. Put the station information into the header

    Returns
    outputheader, instrumentelementnumbers, instrumentserialnumbers, instrumentshorthand, instrumentshouldbemultiplier, instrumentuncertainty
    '''
    
    print('Inside 2. subroutinecreateheaderoutput')
    
    # Load the sitefile
    sitefile_complete = np.array(pd.read_excel(sitefilename, engine='openpyxl'))

    # Get station information from the sitefile
    stationidnumber = sitefile_complete[4,1]
    station = sitefile_complete[5,1]
    stationfullname = sitefile_complete[6,1]
    
    # Get the station location
    longitude = sitefile_complete[7,1]
    latitude = sitefile_complete[8,1]
    altitude = sitefile_complete[9,1]
    timezone = sitefile_complete[10,1]
    
    # Put the time zone into python format
    pytimezone = 'Etc/GMT+'+str(np.abs(timezone))        
    
    # Get the instrument column information
    instrumentelementnumbers, instrumentserialnumbers, instrumentshorthand, instrumentprnmultiplier, instrumentshouldbemultiplier, instrumentuncertainty = subroutinegetsitefileinfo(sitefile_complete, daterange[0])            
    
    # Define the a blank output header file
    outputheader = np.full((44, 7), '-',dtype=object)
    
    # Put in station header stuff (upper left corner) 
    outputheader[0, 0] = 'Station_ID_Number:'
    outputheader[0, 1] = stationidnumber
    
    outputheader[1, 0] = 'Station_Name:'
    outputheader[1, 1] = station 
    
    outputheader[2, 0] = 'Station_Location:'
    outputheader[2, 1] = stationfullname 
    
    outputheader[3, 0] = 'Latitude_(+North):'
    outputheader[3, 1] = latitude
    
    outputheader[4, 0] = 'Longitude_(+East):'
    outputheader[4, 1] = longitude 
    
    outputheader[5, 0] = 'Altitude_(m):'
    outputheader[5, 1] = altitude
    
    outputheader[6, 0] = 'Time_Zone_(+East):'
    outputheader[6, 1] = timezone
    
    outputheader[7, 0] = 'Time_Interval_(Minutes):'
    outputheader[7, 1] = timeinterval
    
    outputheader[8, 0] = 'Year//Month'
    # keep the input from the input file, (The month has leading zeros)    
    outputheader[8, 1] = str(year) + "//" + ('0' if (month<10) else '') + str(month) 
        
    #  Define column 6 (labels going across)
    outputheader[0, 6] = 'Type_of_Measurement:'
    outputheader[1, 6] = 'Element:'
    outputheader[2, 6] = 'Instrument_Serial_Number:'
    outputheader[3, 6] = 'Instrument_Shorthand_Name:'
    outputheader[4, 6] = 'Responsivity:'
    outputheader[5, 6] = 'Estimated_Uncertainty_(U95%):'
    outputheader[6, 6] = 'Sample_Method:'
    outputheader[7, 6] = 'Units:'
    outputheader[8, 6] = 'Column_Notes:'
    
    # define labels for daily totals
    outputheader[10, 0] = 'Day_of_month'
    outputheader[10, 1] = 'Day_of_year'
    
    # Get the number of days in the month ( Get the 23:59 minute because it is still in this month (not midnight the at the start of the next month))
    dim = daterange[-2].day

    # Save the Day of the month to the header
    outputheader[11:11+dim,0] = range(1,dim+1)
    # Save the day of the year to the header
    outputheader[11:11+dim, 1] = daterange[::1440].dayofyear 
    
    # Determine the sunrise, sunset, solar noon times
    sunrise, transit, sunset = subroutinecomputesunrisesunsettransit(year, month, pytimezone, latitude, longitude, altitude)

    # Get the sunrise and sunset times
    outputheader[10, 2] = 'Sunrise_Time_(HH::MM:SS)'
    outputheader[11:11+dim, 2] = sunrise
    outputheader[10, 3] = 'Sunset_Time_(HH::MM:SS)'
    outputheader[11:11+dim, 3] = sunset
    outputheader[10, 4] = 'Solar_Noon_Time_(HH::MM:SS)'
    outputheader[11:11+dim, 4] = transit
    
    # Put in the ETR labels 
    # Can not compute the total of the ETR yet, (Can't do this until you have the ETR in the file)
    outputheader[10, 5] = 'ETR_Daily_Total_Energy_(kWh/m^2)'
    outputheader[10, 6] = 'DNI_ClearSkyModel_Daily_Total_Energy_(kWh/m^2)'
    
    # put labels in row 44
    outputheader[43, 0] = 'year.fractionofyear'
    outputheader[43, 1] = 'dayofyear.fractionofday'
    outputheader[43, 2]= 'YYYY-MM-DD--HH:MM:SS'
    outputheader[43, 3] = 'SZA'
    outputheader[43, 4] = 'AZM'
    outputheader[43, 5] = 'ETR_(W/m^2)'
    outputheader[43, 6] = 'DNI_ClearSkyModel_(W/m^2)'
    
    return outputheader, instrumentelementnumbers, instrumentserialnumbers, instrumentshorthand, instrumentprnmultiplier, instrumentshouldbemultiplier, instrumentuncertainty, pytimezone



def subroutinegetsitefileinfo(sitefile_complete, date):
    
#    print('Insside subroutinegetsitefileinfo')

    # Create a blank list of sitefile dates
    sitefiledates = np.empty((0,1),float)
    sitefilerows = np.empty((0,1),float)
    
    # Go through each row of the sitefile.
    for irow in range(len(sitefile_complete)):
        # See if the lookup phrase "newcalibration" is found 
        # newcalibration is one line before the date stamp
        if sitefile_complete[irow,0] =='newcalibration':
            # Get the date from the file (one row after "newcalibration")
            sitefiledates = np.append(sitefiledates, dt.datetime.strptime(sitefile_complete[irow+1,2], '%Y-%m-%d--%H:%M'))
            # get the rows of the dates
            sitefilerows = np.append(sitefilerows,int(irow+1))
    
    # Add a sitefile end date (way in the future)
    # This is needed to know when the last sitefile ends. (there is a sitefile row + 1, that looks at the next record)        
    sitefiledates = np.array(np.append(sitefiledates,dt.datetime.strptime("2100-12-31--23:59", '%Y-%m-%d--%H:%M'))) #str(dt.datetime.now().year+1)+
    sitefilerows = np.array(np.append(sitefilerows,len(sitefile_complete)+1))

    # Go through the various sitefile start dates 
    for isitefilerows in range(len(sitefiledates)):
        # See if the month file start date is greater than the sitefile start date
        # Or in other words, is this month after this sitefile date
        # If the sitefile is bigger than the month, the row is not recorded
        if sitefiledates[isitefilerows] <= date:
           
            # Define the starting row in the sitefile
            sitefilestartrow = int(isitefilerows)

 #   print(sitefilestartrow)            
    # Get information from this sitefile record        
    instrumentelementnumbers = np.array(sitefile_complete[int(sitefilerows[sitefilestartrow])+1:int(sitefilerows[sitefilestartrow+1])-1,0])
 #   print(instrumentelementnumbers)            
    instrumentserialnumbers = np.array(sitefile_complete[int(sitefilerows[sitefilestartrow])+1:int(sitefilerows[sitefilestartrow+1])-1,1])
    instrumentshorthand = np.array(sitefile_complete[int(sitefilerows[sitefilestartrow])+1:int(sitefilerows[sitefilestartrow+1])-1,2])
    
    instrumentprnmultiplier = np.array(sitefile_complete[int(sitefilerows[sitefilestartrow])+1:int(sitefilerows[sitefilestartrow+1])-1,3])
    # Look for places that have na, replace with np.nan
    instrumentprnmultiplier[instrumentprnmultiplier=="na"]=np.nan
    instrumentprnmultiplier[instrumentprnmultiplier=="nan"]=np.nan
    instrumentprnmultiplier[instrumentprnmultiplier=="NA"]=np.nan
    instrumentprnmultiplier[instrumentprnmultiplier=="NAN"]=np.nan

    instrumenttxtmultiplier = np.array(sitefile_complete[int(sitefilerows[sitefilestartrow])+1:int(sitefilerows[sitefilestartrow+1])-1,5])
    instrumenttxtmultiplier[instrumenttxtmultiplier=="na"]=np.nan
    instrumenttxtmultiplier[instrumenttxtmultiplier=="nan"]=np.nan
    instrumenttxtmultiplier[instrumenttxtmultiplier=="NA"]=np.nan
    instrumenttxtmultiplier[instrumenttxtmultiplier=="NAN"]=np.nan    

    instrumentshouldbemultiplier = np.array(sitefile_complete[int(sitefilerows[sitefilestartrow])+1:int(sitefilerows[sitefilestartrow+1])-1,7])
    instrumentshouldbemultiplier[instrumentshouldbemultiplier=="na"]=np.nan
    instrumentshouldbemultiplier[instrumentshouldbemultiplier=="nan"]=np.nan
    instrumentshouldbemultiplier[instrumentshouldbemultiplier=="NA"]=np.nan
    instrumentshouldbemultiplier[instrumentshouldbemultiplier=="NAN"]=np.nan    

    instrumentuncertainty = np.array(sitefile_complete[int(sitefilerows[sitefilestartrow])+1:int(sitefilerows[sitefilestartrow+1])-1,9])
    instrumentuncertainty[instrumentuncertainty=="na"]=np.nan
    instrumentuncertainty[instrumentuncertainty=="nan"]=np.nan            
    instrumentuncertainty[instrumentuncertainty=="NA"]=np.nan
    instrumentuncertainty[instrumentuncertainty=="NAN"]=np.nan    
    
  #  print(instrumentelementnumbers)            
    
    return instrumentelementnumbers, instrumentserialnumbers, instrumentshorthand, instrumentprnmultiplier, instrumentshouldbemultiplier, instrumentuncertainty
    
    
    


# 2.2 Go though the sunrise, sunset, solar noon events for this month
def subroutinecomputesunrisesunsettransit(year, month, pytimezone, latitude, longitude, altitude):
    '''
    Computes the sunrise, sunset, transit good to 1 second. 
    '''
    
 #   print('Inside 2.2 subroutinecomputesunrisesunsettransit')
        
    # create a list of dates (one for each day)
    # In the upcoming search, time 1 is at 11:30 in the morning. Time 2 is at 12:30     
    if month < 12:
        datedaysonly = pd.date_range(str(year) + "-" + str(month) + "-01 11:30:00", str(year) + "-" + str(month+1)+"-01 00:00", freq="1d", tz=pytimezone)
    else:
        datedaysonly = pd.date_range(str(year) + "-" + str(month) + "-01 11:30:00", str(year+1) + "-" + str(1)+"-01 00:00", freq="1d", tz=pytimezone)
    
    # Get the noon times
    transit = findsunrisesunsetnoon(datedaysonly, 180, 'azimuth', -1, latitude, longitude, altitude)
    
    # create a list of dates (one for each day)
    # In the upcoming search, time 1 is at 5:30 in the morning. Time 2 is at 6:30     
    if month <12:
        datedaysonly = pd.date_range(str(year) + "-" + str(month) + "-01 05:30:00", str(year) + "-" + str(month+1)+"-01 00:00", freq="1d", tz=pytimezone)
    else:
        datedaysonly = pd.date_range(str(year) + "-" + str(month) + "-01 05:30:00", str(year+1) + "-" + str(1)+"-01 00:00", freq="1d", tz=pytimezone)
    
    # Get the sunrise times
    sunrise = findsunrisesunsetnoon(datedaysonly, 90.267, 'apparent_zenith', +1, latitude, longitude, altitude)
    
    # create a list of dates (one for each day)
    # In the upcoming search, time 1 is at 17:30 in the afternoon. Time 2 is at 18:30     
    if month < 12:
        datedaysonly = pd.date_range(str(year) + "-" + str(month) + "-01 17:30:00", str(year) + "-" + str(month+1)+"-01 00:00", freq="1d", tz=pytimezone)
    else:
        datedaysonly = pd.date_range(str(year) + "-" + str(month) + "-01 17:30:00", str(year+1) + "-" + str(1)+"-01 00:00", freq="1d", tz=pytimezone)
    
    # Get the sunset times
    sunset = findsunrisesunsetnoon(datedaysonly, 90.267,'apparent_zenith', -1, latitude, longitude, altitude)
    
    return sunrise, transit, sunset 

# 2.2.1 Determine a list of datetimes that corespond to the sun event
def findsunrisesunsetnoon(datedaysonly, findthisangle, szavsazm, plusminus, latitude, longitude, altitude):
    '''
    Do a binary search for the time of sunrise/sunset/transit    
    datetimetest is the starting datetime
    findthisangle is the solar angle to find (SZA or AZM depending)
    szavsazm is a string label for what solar position to get
    Plusminus is a +1 or a -1 switch to move forward or back      
    Outputs a list of times that corespond to the sun event. 
    '''
    
#    print('Inside 2.1.1 findsunrisesunsetnoon')
   
    # define a blank list of times (this will be filled in)
    timelist = np.array([])
    
    datetimetest = datedaysonly[0]
    
    # compute the new datetime Do a search of data points one hour apart
    datetimetest, _ = getnewdatetime(datetimetest, 3600, szavsazm, findthisangle, latitude, longitude, altitude)
    
    # Refine the search to get closer (a one minute search)
    # This gets you pretty close to the correct time, 
    datetimetest, sunposition = getnewdatetime(datetimetest, 60, szavsazm, findthisangle, latitude, longitude, altitude)
    
    # Set the first date back one day ( in the upcoming loop a day is added with each day)
    datetimetest = datetimetest - dt.timedelta(seconds = 86400)
    
    # loop through the different days of the month
    for idatetime in datedaysonly[:]:        
        
        # add a day to the previous sunrise time (each sunrise is close to the previous one)
        datetimetest = datetimetest + dt.timedelta(seconds = 86400)
        
        # Define a set amount to add to the date
        # 2^8 = 256 seconds = 4.5 minutes (divisible by 2 a bunch of times)
        # in the upcoming loop we will be cutting this in half a few times (Which is why it is base 2)
        addthistime = 2**8 
        
        # Start looking for the sunrise in the upcoming while loop
        continuelooking = True
        
        # define an initial value to the previous sunposition value
        sunpositionprevious = sunposition
    
        # Set the itteration count to zero
        iteration = 0    
 
       # while loop to go through finding the data
        while continuelooking:
            
            iteration = iteration + 1
            
            # Get the sun position at this time
            sunposition = pvlib.solarposition.get_solarposition(datetimetest, latitude = latitude, longitude = longitude, altitude=altitude,  pressure=101300, temperature = 25 )[szavsazm][0]
    
            # test the results
            # stop looking if the timestep is one second and the previous and this trial are on opposite sides of sunrisee
            if ( addthistime ==1 ) & ( (sunposition - findthisangle) * (sunpositionprevious - findthisangle) <= 0):         
                # Stop looking if the sun position is at the target position 
                continuelooking = False
                # add this time to the list
                timelist = np.append(timelist,datetimetest.strftime("%H::%M:%S"))#
            
            # stop looking if you made it through 6 hours
            elif (iteration > 21600): #21600
                continuelooking = False
                print("*****************************************************")
                print(["ERROR Sunrise/sunset/transit not found", iteration, datetimetest,sunposition, sunpositionprevious])
                print("*****************************************************")
                print("Pause for 60 seconds")
                time.sleep(60)
                timelist = np.append(timelist,datetimetest.strftime("%H::%M:%S"))
            
            # Not close enough, change the time and try again
            else:            
                # Cut the step size in half
                # Make sure the step size doesn't get smaller than 1 second
                addthistime = int(np.max([1,addthistime/2]))
        
                # test if you went over
                if sunposition <= findthisangle:        
                    # If you went over (take a step back)
                    datetimetest = datetimetest - (plusminus) * dt.timedelta(seconds = addthistime)
                else:
                    # If you didn't go far enough take a step forward
                    datetimetest = datetimetest + (plusminus) * dt.timedelta(seconds = addthistime)
                 
                # record this trial for the next loop
                sunpositionprevious= sunposition
    
    # output the list of times
    return timelist    

# 2.2.1.1 Search function for sunrise, sunset, solar noon
def getnewdatetime(datetimetest, addthistime, suncomponent, findthisangle, latitude, longitude, altitude): 
    '''
    Define some functions for sunrise, sunset, and solar noon calculations
    Given two datetimes and two sun locations (two end points for a line)
    Compute the time the sun is at the desired angle (x intercept at a particular y)
    This is a crude search to get close
    addthistime is in seconds    
    '''

    # get a second time based off the first
    datetimetest2 = datetimetest + dt.timedelta(seconds = addthistime)
   
    # compute sun position at time 1 and time 2
    sunlocation1 = pvlib.solarposition.get_solarposition(datetimetest, latitude = latitude, longitude = longitude, altitude=altitude,  pressure=101300, temperature = 25 )[suncomponent][0]
    sunlocation2 = pvlib.solarposition.get_solarposition(datetimetest2, latitude = latitude, longitude = longitude, altitude=altitude,  pressure=101300, temperature = 25 )[suncomponent][0]
    
    # Compute when the sunevent is happening (based off findings)
    addthistime = np.round(addthistime / (sunlocation2 - sunlocation1) * (findthisangle - sunlocation1))
    
    # adjust the starting time (Should be within a few minutes)
    datetimetestout = datetimetest + dt.timedelta(seconds = addthistime)
    
    # Return the datetime at the desired angle
    return datetimetestout, sunlocation1        
     
#%%

# 3. Create output file
def subroutinecreateoutput(daterange, doyfod, yearfoy, datetime_ymdhms, timeinterval, outputheader, pytimezone):
    '''
    Create blank output file
    Creat blank output header file
    Put the timestamps for this month into the file
    Compute the solar position
    Computes the ETR daily sum values for the header info
    '''
        
    print('Inside 3. subroutinecreateoutput')

    # Create blank output
    output = np.full((len(daterange), 7), '-', dtype=object)
    
    # Put in the timestamps    
    output[:,0] = yearfoy
    output[:,1] = doyfod
    output[:,2] = datetime_ymdhms

    # Compute solar position
    # Get the solar position position (SZA and AZM are in here)
    # Compute the solar position in the middle of the time interval (30 seconds into the minute)
    # This is equivalent to the SPA code.     
    # Since the daterange is time zone niave, we need subtract 8 hours to get everything correct
    solarposition = pvlib.solarposition.get_solarposition(daterange + dt.timedelta(hours = 8)- dt.timedelta(seconds = timeinterval*60/2), latitude = outputheader[3,1], longitude = outputheader[4,1], altitude=outputheader[5,1]) 
  
    # Put the SZA into the output file (only 4 decimals)
    output[:,3] = np.trunc((solarposition.apparent_zenith) * 10**4) / (10**4)

    # Put the AZM into the output file (only 4 decimals)
    output[:,4] = np.trunc((solarposition.azimuth) * 10**4) / (10**4)

    # Get the extraterestrial radiation (normal radiation)
    # In the middle of the time interval
    etrn = np.array(pvlib.irradiance.get_extra_radiation(doyfod - timeinterval*60/2/86400, solar_constant = 1361))
    
    # Get the extraterestrial radiaion (horizontal)
    etr = etrn * np.cos(solarposition.apparent_zenith * np.pi/180)
    
    # create a mask of whent the sun is down.
    etrmask = 90 < solarposition.apparent_zenith
    
    # Force the ETR and ETRn to be zero when the sun is down.
    etr[etrmask]=0.
    etrn[etrmask]=0.
    
    # Put the ETR into the output file
    output[:,5] = np.trunc((etr) * 10**2) / (10**2)    

    # Define a station location    
    tus = pvlib.location.Location(latitude=outputheader[3,1],longitude=outputheader[4,1],altitude=outputheader[5,1],tz=pytimezone)

    # Compute the clear sky model irradiance
    # ineichen with climatology table by default
    clearskymodel = tus.get_clearsky(daterange - dt.timedelta(seconds = timeinterval*60/2), model="simplified_solis", dni_extra = etrn)

    # Define the clear sky DNI value
    dnics = np.array(clearskymodel['dni'])

    # Put the DNI Clear sky model into the output file
    output[:,6] = np.trunc((dnics) * 10**2) / (10**2)
    
    # Go through the days
    pasterow = 11
    for idate in daterange[::1440].date:
     
        # Find the days
        datemask = idate==daterange.date
        
        # Sum up the irradiance (convert to kWh/m^2)
        outputheader[pasterow, 5] = np.trunc(sum(etr[datemask])*timeinterval/(60*1000) * 10**3) / (10**3)
        outputheader[pasterow, 6] = np.trunc(sum(dnics[datemask])*timeinterval/(60*1000) * 10**3) / (10**3)
        pasterow= pasterow + 1
        
    return outputheader, output
#%%

# 4. Create comments columns
def subroutinecreateoutputcommentsblank(output):
    '''
    Create the comments column. The far right side.
    '''
 
    print('Inside 4. subroutinecreateoutputcommentsblank')

    # Create a blank list of header row comments *)
    outputheadercomments = np.full((44, 1), '-', dtype=object)
    
    outputheadercomments[0] = 'NOTES'
    outputheadercomments[1] = 'Contact_Info:_http://solardat.uoregon.edu'
    outputheadercomments[2] = 'File_format_description_at:_"http://solardat.uoregon.edu/download/Papers/Structure_of_a_comprehensive_solar_radiation_dataset_ASES_2017_Final.pdf"'
    outputheadercomments[3] = 'Flag_description_at:_"http://solardat.uoregon.edu/QualityControlFlags.html"'
    outputheadercomments[4] = 'Data_has_been_calibrated_using_the_responsivity_values_listed'
    outputheadercomments[5] = 'The_phrase_"_original"_means_the_data_has_not_had_the_nighttime_offset_subtracted_(or_any_other_adjustments).'
    outputheadercomments[6] = 'Data_that_has_been_"computed"_was_calculated_from_measured_columns'
    outputheadercomments[7] = 'Date_this_file_was_created:_' + dt.datetime.now().strftime("%Y-%m-%d")
    outputheadercomments[8] = 'This_file_was_created_using_code:Version_2.0"'#+temporaryfile.iloc[10][0]+'"'
    outputheadercomments[9] = '-'
    outputheadercomments[10] = 'Assorted_Daily_Values_(Rows_12-42)'
    outputheadercomments[43] = 'Data_Begins_Next_Row'
     
    # ouput comments column
    outputcomments= np.full((len(output), 1), '-',dtype=object)
    
    # In the commnets row, put in a marker to know where to start puttin in the new data.
    # Since this is a brand new file put it at the top.
    outputcomments[0] = 'NewDataStartsHere'
    return outputheadercomments, outputcomments

#%%

# 5. Add instruments to the output file
def subroutineaddmeasured(outputheader, output, station, instrumentelementnumbers, instrumentserialnumbers, instrumentshorthand, instrumentshouldbemultiplier, instrumentuncertainty):
    
    '''
    Add columns for each measured instrumnet.
    '''

    print('Inside 5. subroutineaddmeasured')    
    
    # Go through each element number
    # Each row in the sitefile coresponds to a colum in the data file
    for icolumn in range(len(instrumentelementnumbers)):

        # See if the element number is not equal to zero (Don't add the zero values, Add all the rest)
        if instrumentelementnumbers[icolumn]!=0:
            
            # Add two columns to the header file
            outputheader = np.hstack([outputheader, np.full((len(outputheader),1),'-'), np.full((len(outputheader),1),'-')])
                       
            # Add two columns to the ouput file for this instrument 
            output = np.hstack([output, np.full((len(output),1),'-'), np.full((len(output),1),-99)])

            # Add the sitefile information for this column
            outputheader[1,-2] = instrumentelementnumbers[icolumn]
            outputheader[2,-2] = instrumentserialnumbers[icolumn]
            outputheader[3,-2] = instrumentshorthand[icolumn]
            outputheader[4,-2] = round(1000/instrumentshouldbemultiplier[icolumn],5)
            outputheader[5,-2] = round((((instrumentuncertainty[icolumn]/196)**2+.01**2)**.5)*100 * 1.96,3)
            outputheader[8,-2] = 'MeasuredColumn'

    # 5.1 Apply measurement type specific information to each column            
    outputheader = subroutineaddheaderinformation(outputheader, station)
            
    return outputheader, output
            
# 5.1 Add instrument specific labels to header
def subroutineaddheaderinformation(outputheader,station):
    '''
    Add column specific lables to the columns (values not in the sitefile)
    These are lookup values decided by the measurment type
    '''
    print('Inside 5.1 subroutineaddheaderinformation')
    
    # Go through all columns of the output file
    for icolumn in range(7,outputheader.shape[1],2):
        # Puts in the first few header rows dependent on element number

#        print('Inside 5.1 subroutineaddheaderinformation', outputheader[1,icolumn])
    
        # define reference irradiance sensors
        ghirefnumber = 1000
        dnirefnumber = 2010
        dhirefnumber = 3000
        row0 = "NA"
    
        # Look to see if the element number of this column is actually a number (SD, and _original are not numbers)
        if np.isreal(outputheader[1,icolumn]):
            # If there
            # Test if it is an irradiance column
            if (1000<=outputheader[1,icolumn]) and (outputheader[1,icolumn]<=3999):
        
                # GHI  
                if (1000<=outputheader[1,icolumn]) and (outputheader[1,icolumn]<=1009):
                    # See if this is the reference GHI instrument
                    if  (outputheader[1,icolumn]==ghirefnumber):
                        row0 = "GHI"
                    else:
                        row0 = "GHI_Aux("+str(outputheader[1,icolumn])+")"
                     
                # Upwelling
                elif (1090 <= outputheader[1,icolumn]) and (outputheader[1,icolumn]<=1099):
                        row0 = "Upwelling"
            
                # Global tilted measurements
                elif (1100 <= outputheader[1,icolumn]) and (outputheader[1,icolumn]<=1999):
        
                    # Station specific tilted labels
                    if (station =="ASO"): 
                        row0 = "GTI(15:180)"
                        
                    elif (station =="BDO"): 
                        row0 = "GTI(32:178)"
                        
                    elif (station =="CYW"): 
                        row0 = "GTI(51:180)"
                        
                    elif (station =="EUO"): 
                        if (1360 <= outputheader[1,icolumn]) and (outputheader[1,icolumn]<=1369): 
                            row0 = "GTI(30:180)"
                        elif (1920 <= outputheader[1,icolumn]) and (outputheader[1,icolumn]<=1929): 
                            row0 = "GTI(90:0)"
                        elif (1960 <= outputheader[1,icolumn]) and (outputheader[1,icolumn]<=1969): 
                            row0 = "GTI(90:180)"
                            
                    elif (station =="PSO"): 
                        if (1160 <= outputheader[1,icolumn]) and (outputheader[1,icolumn]<=1169): 
                            row0 = "GTI(16:201)"
                        elif (1360 <= outputheader[1,icolumn]) and (outputheader[1,icolumn]<=1369): 
                            row0 = "GTI(30:201)"
            
                    elif (station =="SAO"): 
                        row0 = "GTI(30:180)"

                    elif (station =="SIO"): 
                        row0 = "GTI(90:180)"
                    
                    else:
                        print("DEFINE A irradiance sensor here (Aborted)")
                        print('Station: ', station)
                        print('Element: ', outputheader[1,icolumn])                    
                        time.sleep(30)
                        sys.exit()     
            
                # DNI
                elif (2010<=outputheader[1,icolumn]) and (outputheader[1,icolumn]<=2019):
                    # See if this is the reference GHI instrument
                    if  (outputheader[1,icolumn]==dnirefnumber):
                        row0 = "DNI"
                    else:
                        row0 = "DNI_Aux("+str(outputheader[1,icolumn])+")"
                        
                # DHI 
                elif (3000<=outputheader[1,icolumn]) and (outputheader[1,icolumn]<=3009):
                    # See if this is the reference GHI instrument
                    if  (outputheader[1,icolumn]==dhirefnumber):
                        row0 = "DHI"
                    else:
                        row0 = "DHI_Aux("+str(outputheader[1,icolumn])+")"
            
                else:
                    print("DEFINE A irradiance sensor here (Aborted)")
                    print('line 664')
                    time.sleep(30)
                    sys.exit()     
                
                # For irradiance sensors, define a few header rows.
                outputheader[43, icolumn] = outputheader[0,icolumn] = row0 
                outputheader[43, icolumn+1] = outputheader[0,icolumn+1] = "Flag_" + row0 
                outputheader[4,icolumn+1] = "microV/(W/m^2)"
                outputheader[6,icolumn] = "Avg"
                outputheader[7,icolumn] = "W/m^2"
            
            # Other sensor types (Not irradiance)
            elif (4000 <= outputheader[1,icolumn]) and (outputheader[1,icolumn]<=4999):
                outputheader[43, icolumn] = outputheader[0,icolumn] = "PV_Current"
                outputheader[43, icolumn+1] = outputheader[0,icolumn+1] = "Flag_PV_Current"
                outputheader[4,icolumn+1] = "Varies"
                outputheader[6,icolumn] = "Avg"
                outputheader[7,icolumn] = "Amps"
    
            elif (5000 <= outputheader[1,icolumn]) and (outputheader[1,icolumn]<=5999):
                outputheader[43, icolumn] = outputheader[0,icolumn] = "PV_Power"
                outputheader[43, icolumn+1] = outputheader[0,icolumn+1] = "Flag_PV_Power"
                outputheader[4,icolumn+1] = "Varies"
                outputheader[6,icolumn] = "Avg"
                outputheader[7,icolumn] = "Watts"
    
            elif (6000 <= outputheader[1,icolumn]) and (outputheader[1,icolumn]<=6999):
                outputheader[43, icolumn] = outputheader[0,icolumn] = "PV_Voltage"
                outputheader[43, icolumn+1] = outputheader[0,icolumn+1] = "Flag_PV_Voltage"
                outputheader[4,icolumn+1] = "Varies"
                outputheader[6,icolumn] = "Avg"
                outputheader[7,icolumn] = "Volts"
        
            elif (7000 <= outputheader[1,icolumn]) and (outputheader[1,icolumn]<=7999):
                
                outputheader[4,icolumn+1] = "microV/(W/m^2)"
                outputheader[6,icolumn] = "Avg"
                outputheader[7,icolumn] = "W/m^2"
                
                if station == "SEW":        
                    outputheader[43, icolumn] = outputheader[0,icolumn] = "UVB"
                    outputheader[43, icolumn+1] = outputheader[0,icolumn+1] = "Flag_UVB"

                
                elif station == "EUO":        
                    if (outputheader[1,icolumn] == 7003):
                        outputheader[43, icolumn] = outputheader[0,icolumn] = "UVB"
                        outputheader[43, icolumn+1] = outputheader[0,icolumn+1] = "Flag_UVB"
                    else:
                        outputheader[43, icolumn] = outputheader[0,icolumn] = "PIR"
                        outputheader[43, icolumn+1] = outputheader[0,icolumn+1] = "Flag_PIR"

                elif station == "BUO":        
                    if( outputheader[1,icolumn] == 7009):
                        outputheader[43, icolumn] = outputheader[0,icolumn] = "PIR_NET_I"
                        outputheader[43, icolumn+1] = outputheader[0,icolumn+1] = "Flag_PIR_NET_I"
                    else:
                        outputheader[43, icolumn] = outputheader[0,icolumn] = "PIR_DW_I"
                        outputheader[43, icolumn+1] = outputheader[0,icolumn+1] = "Flag_PIR_DW_I"
                else:
                    print("need to put the UV here (Aborted)")
                    print('line 725')
                    time.sleep(30)
                    sys.exit()
                
                                
            elif (9150 <= outputheader[1,icolumn]) and (outputheader[1,icolumn]<=9159):        
                outputheader[43, icolumn] = outputheader[0, icolumn] = "Precipitation"
                outputheader[43, icolumn+1] = outputheader[0, icolumn+1] = "Flag_Precipitation"
                outputheader[4, icolumn+1] = "microV?/millimeter"
                outputheader[6, icolumn] = "Avg"
                outputheader[7, icolumn] = "millimeter"
        
            elif (9170 <= outputheader[1,icolumn]) and (outputheader[1,icolumn]<=9179):
                outputheader[43, icolumn] = outputheader[0, icolumn] = "Pressure"
                outputheader[43, icolumn+1] = outputheader[0, icolumn+1] = "Flag_Pressure"
                outputheader[4, icolumn+1] = "microV?/millibar"
                outputheader[6, icolumn] = "Avg"
                outputheader[7, icolumn] = "millibar"
        
            elif (9200 <= outputheader[1,icolumn]) and (outputheader[1,icolumn]<=9209):
                outputheader[43, icolumn] = outputheader[0, icolumn] = "Wind_direction"
                outputheader[43, icolumn+1] = outputheader[0, icolumn+1] = "Flag_Wind_direction"
                outputheader[4, icolumn+1] = "microV?/degree"
                outputheader[6, icolumn] = "Inst"
                outputheader[7, icolumn] = "degree"
        
            elif (9210 <= outputheader[1,icolumn]) and (outputheader[1,icolumn]<=9219):
                outputheader[43, icolumn] = outputheader[0, icolumn] = "Wind_Speed"
                outputheader[43, icolumn+1] = outputheader[0, icolumn+1] = "Flag_Wind_Speed"
                outputheader[4, icolumn+1] = "microV?/m/s"
                outputheader[6, icolumn] = "Avg"
                outputheader[7, icolumn] = "m/s"
        
            elif (9300 <= outputheader[1,icolumn]) and (outputheader[1,icolumn]<=9309):
                outputheader[43, icolumn] = outputheader[0, icolumn] = "Temperature"
                outputheader[43, icolumn+1] = outputheader[0, icolumn+1] = "Flag_Temperature"
                outputheader[4, icolumn+1] = "microV?/C"
                outputheader[6, icolumn] = "Avg"
                outputheader[7, icolumn] = "C"
        
            elif (9330 <= outputheader[1,icolumn]) and (outputheader[1,icolumn]<=9339):
                outputheader[43, icolumn] = outputheader[0, icolumn] = "Humidity"
                outputheader[43, icolumn+1] = outputheader[0, icolumn+1] = "Flag_Humidity"
                outputheader[4, icolumn+1] = "microV?/%"
                outputheader[6, icolumn] = "Avg"
                outputheader[7, icolumn] = "Percent"
        
            elif (9360 <= outputheader[1,icolumn]) and (outputheader[1,icolumn]<=9369):
                outputheader[43, icolumn] = outputheader[0, icolumn] = "SensorTemperature"
                outputheader[43, icolumn+1] = outputheader[0, icolumn+1] = "Flag_SensorTemperature"
                outputheader[4, icolumn+1] = "microV?/C"
                outputheader[6, icolumn] = "Avg"
                outputheader[7, icolumn] = "C"
        
            elif (9370 <= outputheader[1,icolumn]) and (outputheader[1,icolumn]<=9379):
                outputheader[43, icolumn] = outputheader[0, icolumn] = "PanelTemperature"
                outputheader[43, icolumn+1] = outputheader[0, icolumn+1] = "Flag_PanelTemperature"
                outputheader[4, icolumn+1] = "microV?/C"
                outputheader[6, icolumn] = "Avg"
                outputheader[7, icolumn] = "C"
        
            elif (9380 <= outputheader[1,icolumn]) and (outputheader[1,icolumn]<=9389):
                outputheader[43, icolumn] = outputheader[0, icolumn] = "SensorTemperature"
                outputheader[43, icolumn+1] = outputheader[0, icolumn+1] = "Flag_SensorTemperature"
                outputheader[4, icolumn+1] = "microV?/C"
                outputheader[6, icolumn] = "Avg"
                outputheader[7, icolumn] = "K"
        
            else:
    
                print("There is an undefined element number. Define it here and make sure it works. \n Element number: ")
                print(outputheader[1,icolumn])
                print('line 797')
                time.sleep(30)
                sys.exit()
    
        elif "_SD" in outputheader[1,icolumn]:
            
            # Look for this element number in the file (Remove the '_SD' from the current element number)
            findthiselementnumber = int(outputheader[1,icolumn].replace("_SD",""))

            elementnotfound = True    
            # Go through all the columns
            for icolumn2 in range(7,outputheader[1].shape[0],2):
                
                # See if this element number matches the other columns
                if findthiselementnumber == outputheader[1,icolumn2]:
    
                    outputheader[43,icolumn] = outputheader[0,icolumn] = str(outputheader[0,icolumn2]) + '_SD'
                    outputheader[43,icolumn+1] = outputheader[0,icolumn+1] = 'Flag_' + outputheader[0,icolumn] 
                    outputheader[4,icolumn+1] = outputheader[4,icolumn2+1]
                    outputheader[6,icolumn] = 'StdDev'
                    outputheader[7,icolumn] = str(outputheader[7,icolumn2])
                    elementnotfound = False
                    
            if elementnotfound:
                print('The standard deviation column was not found \n Element number: ')
                print(outputheader[1,icolumn])
                time.sleep(30)
                sys.exit()                    
        
    return outputheader
#%%

# 6. add two more adjusted columns for irradiance values
def subroutineaddadjusted(outputheader, output):
    '''
    Adds two columns to the output and output header
    The two additional rows are for adjusted data. 
    Up to this point, data was put into the file without the original label.

    Parameters
    ----------
    outputheader : TYPE
        DESCRIPTION.
    output : TYPE
        DESCRIPTION.

    Returns
    -------
    outputheader : TYPE
        DESCRIPTION.
    output : TYPE
        DESCRIPTION.

    '''

    print('Inside 6. subroutineaddadjusted')  

    # Go through all columns 
    for icolumn in range(7,outputheader.shape[1],2):
        
        # Make sure the element numnber is a number
        if np.isreal(outputheader[1,icolumn]):

            # Only make adjustments to irradiance data (GHI, DHI, DNI)
            if (1000<=outputheader[1,icolumn]) and (outputheader[1,icolumn]<=3999):
                
                # add two more columns for the adjusted columns
                outputheader = np.hstack([outputheader, np.full((len(outputheader),1),'-'), np.full((len(outputheader),1),'-')])

                # icolumn is the original column
                # -2 is the adjusted column

                # Modify the row0 values a bit, so the original and adjusted column is correct (the label is already correct)
                outputheader[43,-2] = outputheader[0,-2] = outputheader[0,icolumn] 
                outputheader[43,-1] = outputheader[0,-1] = outputheader[0,icolumn+1]                

                # Change the original column to have the '_original' label
                outputheader[43,icolumn] = outputheader[0,icolumn] = outputheader[0,icolumn]+ "_original"
                outputheader[43,icolumn +1] = outputheader[0,icolumn+1] = outputheader[0,icolumn+1]+ "_original"#.replace('Flag','Flag_original_')
                
                # Change the element number rows
                outputheader[1,-2] = outputheader[1,icolumn]
                outputheader[1,icolumn] = str(outputheader[1,icolumn])+ "_original"

                # Get the rest of the values from the 
                outputheader[2,-2] = outputheader[2,icolumn]

                outputheader[3,-2] = outputheader[3,icolumn]

                outputheader[4,-2] = outputheader[4,icolumn]
                outputheader[4,-1] = outputheader[4,icolumn+1] #"microV/(W/m^2)"

                outputheader[5,-2] = outputheader[5,icolumn]

                outputheader[6,-2] = outputheader[6,icolumn] #"Avg"

                outputheader[7,-2] = outputheader[7,icolumn]#"W/m^2"

                outputheader[8,-2] = "AdjustedColumn"
                
                # add two more columns for the adjusted columns
                output = np.hstack([output, np.full((len(output),1),'-'), np.full((len(output),1),-99)])
                
    return outputheader, output

#%%                
# 7 GHI_Calc
def subroutineaddGHIcalc(outputheader, output):
    '''
    Add two columns for calculated GHI data

    Parameters
    ----------
    outputheader : TYPE
        DESCRIPTION.
    output : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    
    print("INSIDE 7. subroutineaddGHIcalc")

    # Go through each column
    for icolumndni in range(7,outputheader.shape[1],2):

        # Look for DNI in the output (RSP_DNI isn't created yet)
        if (outputheader[0,icolumndni]=="DNI") & np.logical_not('RSR' in outputheader[2,icolumndni]):

            # look for DHI            
            for icolumndhi in range(7,outputheader.shape[1],2):
                if (outputheader[0,icolumndhi]=="DHI") & np.logical_not('RSR' in outputheader[2,icolumndhi]):
                    
                    # Add two rows for the DrHI column
                    output = np.hstack([output, np.full((len(output),1),'-'), np.full((len(output),1),-99)])
            
                    # Add two rows to the header file
                    outputheader = np.hstack([outputheader, np.full((len(outputheader),1),'-'), np.full((len(outputheader),1),'-')])
                            
                    # Put the row0 value in
                    outputheader[43,-2] = outputheader[0,-2] = "GHI_Calc"
                    outputheader[43,-1] = outputheader[0,-1] = "Flag_GHI_Calc"
                
                    outputheader[1,-2] = 1009
                        
                    outputheader[2,-2] = "Computed_from_DNI_and_DHI"
                    outputheader[3,-2] = '-'
                    outputheader[4,-2] = '-'
                    outputheader[5,-2] = round((outputheader[5,icolumndni]**2 + outputheader[5,icolumndhi]**2)**.5 ,3)
                    outputheader[6,-2] = "-"
                    outputheader[7,-2] = "W/m^2"
                    outputheader[8,-2] = "CalculatedColumn"

    return outputheader, output                
#%%


# 8. RSP_DNI_Calc    
def subroutineaddRSPDNI(outputheader, output):
    '''
    Add two columns for RSP direct normal irradiance 

    Parameters
    ----------
    outputheader : TYPE
        DESCRIPTION.
    output : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''

    print('Inside 8. subroutineaddRSPDNI')

    # Go through each column
    for icolumnghi in range(7,outputheader.shape[1],2):

        # Look for GHI and RSP in the output
        if ("GHI" in outputheader[0,icolumnghi]) & ('RSP' in outputheader[2,icolumnghi]) & np.logical_not('_original' in outputheader[0,icolumnghi]) & np.logical_not('_SD' in outputheader[0,icolumnghi]):

            # look for DHI and RSP in the            
            for icolumndhi in range(7,outputheader.shape[1],2):
                if ("DHI" in outputheader[0,icolumndhi]) & ('RSP' in outputheader[2,icolumndhi]) & np.logical_not('_original' in outputheader[0,icolumndhi]) & np.logical_not('_SD' in outputheader[0,icolumndhi]):
                    
                    # Add two rows for the DNI column
                    output = np.hstack([output, np.full((len(output),1),'-'), np.full((len(output),1),-99)])
            
                    # Add two rows to the header file
                    outputheader = np.hstack([outputheader, np.full((len(outputheader),1),'-'), np.full((len(outputheader),1),'-')])
                            
                    # Put the row0 value in
                    outputheader[43,-2] = outputheader[0,-2] = "DNI_Calc"
                    outputheader[43,-1] = outputheader[0,-1] = "Flag_DNI_Calc"
                
                    outputheader[1,-2] = 2019
                        
                    outputheader[2,-2] = "Computed_from_RSPGHI_and_RSPDHI"
                    outputheader[3,-2] = '-'
                    outputheader[4,-2] = '-'
                    outputheader[5,-2] = round((outputheader[5,icolumnghi]**2 + outputheader[5,icolumndhi]**2)**.5,3) 
                    outputheader[6,-2] = "-"
                    outputheader[7,-2] = "W/m^2"
                    outputheader[8,-2] = "CalculatedColumn"
                   
    return outputheader, output    

#%%
 
# 9. DrHI_Calc    
def subroutineaddDrHI(outputheader, output):
    '''
    Add two columns for Direct horizontal irradiance 

    Parameters
    ----------
    outputheader : TYPE
        DESCRIPTION.
    output : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''

    print('Inside 9. subroutineaddDrHI')

    # Go through each column
    for icolumndni in range(7,outputheader.shape[1],2):

        # Look for DNI or DNI_Calc in the output
        if (outputheader[0,icolumndni]=="DNI") | (outputheader[0,icolumndni]=="DNI_Calc") :
#            print(outputheader[0,icolumndni])
            
            # Add two rows to the header file
            outputheader = np.hstack([outputheader, np.full((len(outputheader),1),'-'), np.full((len(outputheader),1),'-')])
            
            # Put the row0 value in
            outputheader[43,-2] = outputheader[0,-2] = "DrHI_Calc"
            outputheader[43,-1] = outputheader[0,-1] = "Flag_DrHI_Calc"
        
            outputheader[1,-2] = 2000
                
            outputheader[2,-2] = "Computed_from_DNI"
            outputheader[3,-2] = '-'
            outputheader[4,-2] = '-'
            outputheader[5,-2] = outputheader[5,icolumndni]
            outputheader[6,-2] = "-"
            outputheader[7,-2] = "W/m^2"
            outputheader[8,-2] = "CalculatedColumn"
            
            # Add two rows for the DrHI column
            output = np.hstack([output, np.full((len(output),1),'-'), np.full((len(output),1),-99)])
            
            # Stop the loop if you already created one DrHI 
            break
                    
    return outputheader, output    


# 10. subroutinemergeandsave   
def subroutinemergeandsave(outputlocation, outputheader, output, outputheadercomments, outputcomments):
    '''
    Merges the various output files into a single form. 
    Puts the columns in the correct order according to element number
    Saves the file to a csv

    Parameters
    ----------
    outputlocation : TYPE
        DESCRIPTION.
    outputheader : TYPE
        DESCRIPTION.
    output : TYPE
        DESCRIPTION.
    outputheadercomments : TYPE
        DESCRIPTION.
    outputcomments : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''

    print("Inside 10. subroutinemergeandsave")
    
    # Combine the header file with the comments header
    outputthistop = np.concatenate((outputheader, outputheadercomments), axis=1)
    
    # Combine the main output file with the comments 
    outputthisbottom = np.concatenate((output, outputcomments), axis=1)
    
    # Combine the top with the bottom
    outputthis = np.concatenate((outputthistop,outputthisbottom))
    
    # Define a list of values to sort the columns by (initialize the list)
    # this is simply the column number of each column
    sortorder = np.array(range(outputthis.shape[1])).astype(float)
   
    # Go through each column (Don't look at the beginning 7 rows or the comments row)
    for icolumn in range(7,outputthis.shape[1]-1,2):
        
        # If the data is a number...    
        if np.isreal(outputthis[1,icolumn]):

            # Change the sort order to be the element number
            # This will put the 1000 element before 2000 elements
            sortorder[icolumn]=outputthis[1,icolumn]
            # Keep the flag column with the data
            sortorder[icolumn+1]=outputthis[1,icolumn]+.1

        elif "_original" in outputthis[1,icolumn]:

            # Put the original and standard deviation columns at the end        
            # This will put the original data after the adjusted data
            sortorder[icolumn]=float(outputthis[1,icolumn].replace("_original",""))*10**3
            sortorder[icolumn+1]=float(outputthis[1,icolumn].replace("_original",""))*10**3+.1

        elif "_SD" in outputthis[1,icolumn]:
            
            # Put the original and standard deviation columns at the end        
            # This will put the Standard deviation data after the orginal
            sortorder[icolumn]=float(outputthis[1,icolumn].replace("_SD",""))*10**6
            sortorder[icolumn+1]=float(outputthis[1,icolumn].replace("_SD",""))*10**6+.1
        else: 
            print("ERROR assigning the column order (Subroutine 9.0)")
            print(outputthis[1,icolumn])
            time.sleep(60)
            sys.exit('line 1069')
    
    # make sure the notes come at the end
    sortorder[-1]= 10**12
    
    # Sort the columns by the values in the sortorder (Smallest ones first, largest ones last)
    outputthis = outputthis[:,sortorder.argsort()]
    
    # Save the output file 
    np.savetxt(outputlocation, np.array(outputthis), delimiter=',', fmt='%s')
    
#%%
        
def makemonthblank(station, year, month, timeinterval, sitefilename, outputlocation):
    '''
    Master subroutine that creates blank monthly files    

    Parameters
    ----------
    station : string
        three letter station name.
    year : int
        Year of file to create
    month : int
        Month of file to create.
    timeinterval : int
        time interval of file in minutes
    sitefilename : string
        location of where the comprehensive format sitefile is located
    outputlocation : string
        Location of where to save the output file

    Returns
    -------
    Creates an output .csv file

    '''

    # 1. Get the timestamp information for this file
    daterange, doyfod, yearfoy, datetime_ymdhms = subroutinecreatedatetimes(year, month, timeinterval)

    # 2. Load the sitefile
    # Get general information about this station 
    outputheader, instrumentelementnumbers, instrumentserialnumbers, instrumentshorthand, instrumentprnmultiplier, instrumentshouldbemultiplier, instrumentuncertainty, pytimezone = subroutinecreateheaderoutput(sitefilename, daterange, year, month, timeinterval)
    
    # 3. Create blank output file    
    outputheader, output = subroutinecreateoutput(daterange, doyfod, yearfoy, datetime_ymdhms, timeinterval, outputheader, pytimezone)
    
    # 4. Create blank comments file
    outputheadercomments, outputcomments = subroutinecreateoutputcommentsblank(output)
    
    # 5. Add measured data to the output    
    outputheader, output = subroutineaddmeasured(outputheader, output, station, instrumentelementnumbers, instrumentserialnumbers, instrumentshorthand, instrumentshouldbemultiplier, instrumentuncertainty)
    
    # 6. Add adjusted data to the output    
    outputheader, output = subroutineaddadjusted(outputheader, output)
    
    # 7. Compute the Globbal horiztal coponent        
    outputheader, output = subroutineaddGHIcalc(outputheader, output)    
    
    # 8. Compute the RSP Direct normal component
    outputheader, output = subroutineaddRSPDNI(outputheader, output)
    
    # 9. Compute the Direct horizontal component
    outputheader, output = subroutineaddDrHI(outputheader, output)
    
    # 10. Merge and save output file to csv.
    subroutinemergeandsave(outputlocation, outputheader, output, outputheadercomments, outputcomments)
    
    print('Made it to the end')

#%%
    
if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
    
    year = 2023
    month = 4

    # Define the station
    station = 'SAO'

    # Define the sitefile input folder
    sitefilefolder = 'C:\\Users\\KARMA\\Desktop\\SRML_Blank_month\\'

    # Get the sitefile for this station       
    sitefilelocation = sitefilefolder + station + '_consolodated_sitefile.xlsx'

    # Name of the output file.
    outputname = station + '_' + str(year) + '-' + ('0' if (month<10) else '') + str(month) + '_ComprehensiveFormat.csv' 

    # Define the output location
    outputlocation = 'C:\\Users\\KARMA\\Desktop\\SRML_Blank_month\\' + outputname 

    # Define the time interval (in minutes)
    timeinterval = 1

    makemonthblank(station, year, month, timeinterval, sitefilelocation, outputlocation)    

#%%
    
