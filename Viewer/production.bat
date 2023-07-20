@echo OFF

SETLOCAL EnableDelayedExpansion

SET CONDA=D:\__TMB_SeamsReleases\env\seams
SET LOCATION=D:\__TMB_SeamsReleases\H_Processor

SET PATH=%CONDA%\Scripts;%CONDA%;%PATH%

CALL activate base
START python production.py


@echo ON