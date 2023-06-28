@echo OFF
rem J. - May 2023 >> ask before delete

SETLOCAL EnableDelayedExpansion
SET CONDA=C:\Users\gomezja\Anaconda3
SET PATH=%CONDA%\Scripts;%CONDA%\envs\seams;%PATH%

	if not DEFINED IS_MINIMIZED set IS_MINIMIZED=1 && start "" /min "%~dpnx0" %* && exit
		PUSHD F:\00_Seams\PySeamsDetection\Viewer\
		CALL activate seams
		START pythonw main.py
	exit

@echo ON