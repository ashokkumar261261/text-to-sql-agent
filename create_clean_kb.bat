@echo off
echo Creating clean Knowledge Base for Text-to-SQL Agent...
echo ============================================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Trying python3...
    python3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERROR: Python is not installed or not in PATH
        echo Please install Python and try again
        pause
        exit /b 1
    )
    set PYTHON_CMD=python3
) else (
    set PYTHON_CMD=python
)

echo Using Python command: %PYTHON_CMD%
echo.

REM Run the Knowledge Base creation script
%PYTHON_CMD% create_clean_kb.py

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo SUCCESS! Clean Knowledge Base created successfully.
    echo You can now test with: "Show me top 5 customers by revenue"
    echo ============================================================
) else (
    echo.
    echo ============================================================
    echo ERROR: Failed to create Knowledge Base
    echo Check the error messages above
    echo ============================================================
)

pause