@echo off

for /d %%i in (C:\Users\gomezja\PycharmProjects\00_dataset\training\Lot_*) do (
    xcopy /s /y "%%i\*.txt" "M:\dataset\training\%%~nxi\"
    xcopy /s /y "%%i\*.xml" "M:\dataset\training\%%~nxi\"
)