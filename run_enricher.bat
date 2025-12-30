@echo off
echo 🚀 Enhanced Medicine Enricher
echo ==============================

REM Activate your Python environment if needed
REM call activate_env.bat

echo.
echo 📁 Drag and drop your Excel file here, or type the full path:
set /p filepath="File path: "

REM Remove quotes if present
set filepath=%filepath:"=%

echo.
echo 📄 Using file: %filepath%
echo.

REM Run the enricher
python run_with_file_path.py "%filepath%"

echo.
echo Press any key to exit...
pause >nul