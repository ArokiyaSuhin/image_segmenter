@echo off
TITLE AI Document Sorter - Installer & Monitor

ECHO ===================================================
ECHO  STEP 1: Checking and Installing Dependencies
ECHO ===================================================
ECHO.
pip install --upgrade -r requirements.txt
ECHO.
ECHO [+] Dependencies are up to date.
ECHO.
ECHO ===================================================
ECHO  STEP 2: Starting the Document Monitor
ECHO ===================================================
ECHO.
python monitor.py

ECHO.
ECHO Script finished.
PAUSE