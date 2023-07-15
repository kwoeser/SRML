
rem added perl program to see if it will work - fev	
rem	2022-02-06 	JTP	Formatted for 01-Sunbeamer (Virtual machine)
rem 2022-12-01 	JTP Added rain difference routine. 
rem 2022-12-01	JTP Compute the .txt file on the new sunbeamer
rem	2022-12-01	JTP Move the .txt file to the old sunbeamer (Not the .dat file)

rem ********************************************************************
rem Clear the variable values
set year=
set month=
set sn3=
set sn2=
set fprocesfolder=
set sitfilefolder=
set inputfolder=
set outputfolder=
set logfolder=
set batname=

set parentfolder=
set station=
set set datlocation=
set agrimetlocation=

rem ********************************************************************

rem Convert the cumulative rain values from the agrimet file to rain difference values in the MAO.dat file
rem Change the directory to the location of the master callouts .py file
rem cd C:\Users\jpeters4\Dropbox\Python\AgrimetRain
rem cd E:\Programs\Python\AgrimetRain

REM rem Define the parent folder where the data is 
REM rem set parentfolder=C:\Users\jpeters4\Dropbox\Python\AgrimetRain\
REM set parentfolder=E:\Data\Step1_CampbellRaw\

REM rem Define the station
REM set station=MAO
REM set datlocation=%parentfolder%%station%.dat
REM set agrimetlocation=%parentfolder%%station%_agrimet.dat
REM rem Run the python code that gets rid of the negative rain
REM python E:\Programs\Python\AgrimetRain\Agrimet_Negative_Rain_2023-03-14.py %1 %datlocation% %agrimetlocation%



C:\Users\KARMA\Desktop\SRML_Blank_month\

REM ALWAYS RUNS?
if not exist C:\Users\KARMA\Desktop\SRML_Blank_month\SAO_2023-04_ComprehensiveFormat.csv (
	py C:\Users\KARMA\Desktop\SRML_Blank_month\srml_makeblankmonth.py	
	REM rem if it doesn't exist then create it and move it over to the correct location
	REM E:
	REM cd E:\SiteFiles
	REM E:\Programs\Pascal\CreateBlank\cr1blk.exe %sn2%RO%year%%month%.txt %sn2% %year% %month% Headers\%sn3%_header.txt
	REM move E:\SiteFiles\%sn2%RO%year%%month%.txt  %outputfolder%\%sn3%\%sn2%RO%year%%month%.txt
	REM echo (year: %year%, month: %month%)
	
)
	
	
REM py C:\Users\KARMA\Desktop\SRML_Blank_month\srml_makeblankmonth.py
echo 1
pause


py C:\Users\KARMA\Desktop\SRML_Blank_month\srml_addmeasureddata.py SAO_A.dat
py C:\Users\KARMA\Desktop\SRML_Blank_month\srml_addmeasureddata.py SAO_B.dat
py C:\Users\KARMA\Desktop\SRML_Blank_month\srml_addmeasureddata.py SAO_C.dat



echo 2
pause


REM rem ********************************************************************



REM rem	Set the date:
REM rem	Set current year (00-99)
REM set year=%date:~12,2%
REM rem To manually set the date (Set this as the current year, two digits)
REM rem set year=22

REM rem	Set current month (01-12)
REM set month=%date:~4,2%
REM rem To manually set the date (keep this at the month you want to make, two digits)
REM rem set month=02

REM rem Define the station name
REM set sn3=MAO
REM set sn2=MA


REM rem define locations
REM set fprocesfolder=E:\Programs\Pascal\Fproces
REM set sitfilefolder=E:\SiteFiles\Sitefile_PreviousFormat
REM set inputfolder=E:\Data\Step1_CampbellRaw
REM set outputfolder=E:\Data\Step3B_Original_Format
REM set logfolder=E:\Log_Files
REM set batname=%sn3%_2022-02-15.bat

REM rem Make sure the RO file exists. Sometimes it is deleted during a previous run
REM if not exist %outputfolder%\%sn3%\%sn2%RO%year%%month%.txt (
	REM rem if it doesn't exist then create it and move it over to the correct location
	REM E:
	REM cd E:\SiteFiles
	REM E:\Programs\Pascal\CreateBlank\cr1blk.exe %sn2%RO%year%%month%.txt %sn2% %year% %month% Headers\%sn3%_header.txt
	REM move E:\SiteFiles\%sn2%RO%year%%month%.txt  %outputfolder%\%sn3%\%sn2%RO%year%%month%.txt
	REM echo (year: %year%, month: %month%)
	
	
REM Rem Need to change to the E drive. (Won't work if you don't)
REM E:
REM cd \Data\Step3B_Original_Format

REM rem Process the data for year and month
REM rem Takes the .dat file, applies the sitefile, and puts the data into the .txt file
REM rem fprocesprogram -- year -- month -- sitefile -- outputlocation -- inputlocation
REM %fprocesfolder%\Fproces1a%SN2%.exe %year% %month% %sitfilefolder%\%sn3% %outputfolder%\%sn3%\%sn2%RO%year%%month%.txt %inputfolder%\%sn3%.dat

REM rem copy the data from new sumbeamer to old sunbeamer
REM xcopy /y /q E:\Data\Step3B_Original_Format\%sn3%\%sn2%RO%year%%month%.txt \\sunbeamer\PC208W\%sn2%RO%year%%month%.txt



REM rem If there were not errors go to the end of the program
REM if not errorlevel 1 goto ENDOFPROGRAM

REM rem	***** HANDLE ERROR *****
REM rem Write to the log file
REM echo %date:~4,10% %time% Error in %batname% (Year: %year%, Month: %month%) >> %logfolder%\%sn3%_20%year%-%month%.log


REM :ENDOFPROGRAM
REM rem pause

REM rem Clear the variable values
REM set year=
REM set month=
REM set sn3=
REM set sn2=
REM set fprocesfolder=
REM set sitfilefolder=
REM set inputfolder=
REM set outputfolder=
REM set logfolder=
REM set batname=

REM set parentfolder=
REM set station=
REM set set datlocation=
REM set agrimetlocation=

REM rem exit the program
REM exit