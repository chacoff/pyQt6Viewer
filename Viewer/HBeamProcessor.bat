@echo OFF

SETLOCAL EnableDelayedExpansion


	:JAIME
    if "%COMPUTERNAME%" == "5CG1436PDJ" (
        echo "Jaime PC"
        SET CONDA=C:\Users\gomezja\Anaconda3
        SET LOCATION=C:\Users\gomezja\PycharmProjects\202_SeamsProcessing\Viewer\
        goto LAUNCH
    ) else (
		goto STATION
	)

	:STATION
    if "%COMPUTERNAME%" == "CZC8317B48" (
        echo "Seams Station"
        SET CONDA=C:\Users\gracraob.EUROPE\AppData\Local\miniconda3
        SET LOCATION=F:\00_Seams\PySeamsDetection\Viewer\
        goto LAUNCH
    ) else (
		goto UNKNOWN
	)


:LAUNCH
SET PATH=%CONDA%\Scripts;%CONDA%\envs\seams;%PATH%

	if not DEFINED IS_MINIMIZED set IS_MINIMIZED=1 && start "" /min "%~dpnx0" %* && exit
		PUSHD %LOCATION%
		CALL activate seams
		START pythonw main.py
	exit

:UNKNOWN
echo "Unknown PC. Please define Conda Path and path location"
pause

@echo ON