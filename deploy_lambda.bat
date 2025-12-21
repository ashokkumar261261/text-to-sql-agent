@echo off
echo ========================================
echo   Deploying Text-to-SQL Lambda Function
echo ========================================

REM Check if function name is provided
set FUNCTION_NAME=%1
if "%FUNCTION_NAME%"=="" (
    echo Please provide your Lambda function name as parameter
    echo Usage: deploy_lambda.bat YOUR_FUNCTION_NAME
    echo Example: deploy_lambda.bat text-to-sql-agent
    exit /b 1
)

echo Function Name: %FUNCTION_NAME%
echo.

REM Create deployment package
echo Creating deployment package...
if exist lambda_deployment.zip del lambda_deployment.zip

REM Create a temporary directory for packaging
if exist temp_deploy rmdir /s /q temp_deploy
mkdir temp_deploy

REM Copy lambda function
copy lambda_function.py temp_deploy\
xcopy kb_documents temp_deploy\kb_documents\ /E /I /Q 2>nul || echo kb_documents not found, skipping...

REM Create zip package
cd temp_deploy
powershell -command "Compress-Archive -Path * -DestinationPath ..\lambda_deployment.zip -Force"
cd ..

REM Clean up temp directory
rmdir /s /q temp_deploy

echo Deployment package created: lambda_deployment.zip
echo.

REM Deploy to AWS Lambda
echo Deploying to AWS Lambda...
aws lambda update-function-code ^
    --function-name %FUNCTION_NAME% ^
    --zip-file fileb://lambda_deployment.zip ^
    --region us-east-1

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Lambda function updated successfully!
    echo.
    echo Testing the function...
    aws lambda invoke ^
        --function-name %FUNCTION_NAME% ^
        --payload "{\"requestContext\":{\"http\":{\"method\":\"GET\"}}}" ^
        --region us-east-1 ^
        response.json
    
    echo.
    echo Response saved to response.json
    echo.
    echo 🚀 Your Lambda function is now updated with the fixes!
    echo Try your query again in the web UI.
) else (
    echo.
    echo ❌ Deployment failed. Please check:
    echo 1. AWS credentials are configured: aws configure
    echo 2. Lambda function exists: aws lambda get-function --function-name %FUNCTION_NAME%
    echo 3. You have permissions to update Lambda functions
)

REM Clean up
if exist lambda_deployment.zip del lambda_deployment.zip
if exist response.json del response.json

echo.
pause