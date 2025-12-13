@echo off
echo ========================================
echo Text-to-SQL Agent Knowledge Base Setup
echo ========================================
echo.

REM Check if Python is available
py --version >nul 2>&1
if errorlevel 1 (
    python --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python is not installed or not in PATH
        echo Please install Python 3.9+ and try again
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=python
    )
) else (
    set PYTHON_CMD=py
)

REM Check if required packages are installed
echo Checking dependencies...
%PYTHON_CMD% -c "import boto3, dotenv" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    %PYTHON_CMD% -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Get bucket name from user
set /p BUCKET_NAME="Enter S3 bucket name for knowledge base (e.g., my-text-to-sql-kb): "
if "%BUCKET_NAME%"=="" (
    echo ERROR: Bucket name is required
    pause
    exit /b 1
)

REM Optional parameters
set /p KB_NAME="Enter knowledge base name [text-to-sql-kb]: "
if "%KB_NAME%"=="" set KB_NAME=text-to-sql-kb

set /p ROLE_NAME="Enter IAM role name [BedrockKnowledgeBaseRole]: "
if "%ROLE_NAME%"=="" set ROLE_NAME=BedrockKnowledgeBaseRole

echo.
echo Configuration:
echo - S3 Bucket: %BUCKET_NAME%
echo - KB Name: %KB_NAME%
echo - IAM Role: %ROLE_NAME%
echo.

set /p CONFIRM="Continue with setup? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo Setup cancelled
    pause
    exit /b 0
)

echo.
echo Starting knowledge base setup...
echo.

REM Run the setup script
%PYTHON_CMD% setup_knowledge_base.py --bucket-name "%BUCKET_NAME%" --kb-name "%KB_NAME%" --role-name "%ROLE_NAME%"

if errorlevel 1 (
    echo.
    echo ERROR: Setup failed. Check the output above for details.
    echo.
    echo Common issues:
    echo - AWS credentials not configured (run: aws configure)
    echo - Insufficient permissions
    echo - Bucket name already exists in another region
    echo.
) else (
    echo.
    echo ========================================
    echo Setup completed successfully!
    echo ========================================
    echo.
    echo Next steps:
    echo 1. Complete the setup in AWS Console as instructed above
    echo 2. Update your .env file with BEDROCK_KNOWLEDGE_BASE_ID
    echo 3. Test the integration: %PYTHON_CMD% test_knowledge_base.py
    echo 4. Start the enhanced web UI: %PYTHON_CMD% -m streamlit run web_ui_enhanced.py
    echo.
)

pause