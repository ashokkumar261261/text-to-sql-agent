@echo off
REM AWS Deployment Script for Text-to-SQL Agent (Windows)

echo 🚀 Deploying Text-to-SQL Agent to AWS...

REM Configuration
set APP_NAME=text-to-sql-agent
set REGION=us-east-1

REM Get AWS Account ID
for /f "tokens=*" %%i in ('aws sts get-caller-identity --query Account --output text') do set ACCOUNT_ID=%%i
set SERVICE_ROLE=arn:aws:iam::%ACCOUNT_ID%:role/AppRunnerTextToSQLRole

REM Check if AWS CLI is configured
aws sts get-caller-identity >nul 2>&1
if errorlevel 1 (
    echo ❌ AWS CLI not configured. Please run 'aws configure' first.
    exit /b 1
)

echo ✅ AWS CLI configured

REM Build Docker image
echo 🔨 Building Docker image...
docker build -t %APP_NAME% .
if errorlevel 1 (
    echo ❌ Docker build failed
    exit /b 1
)

REM Create ECR repository if it doesn't exist
echo 📦 Setting up ECR repository...
aws ecr describe-repositories --repository-names %APP_NAME% --region %REGION% >nul 2>&1
if errorlevel 1 (
    aws ecr create-repository --repository-name %APP_NAME% --region %REGION%
)

REM Get ECR login token and login
echo 🔐 Logging into ECR...
for /f "tokens=*" %%i in ('aws ecr get-login-password --region %REGION%') do set ECR_PASSWORD=%%i
echo %ECR_PASSWORD% | docker login --username AWS --password-stdin %ACCOUNT_ID%.dkr.ecr.%REGION%.amazonaws.com

REM Tag and push image
set ECR_URI=%ACCOUNT_ID%.dkr.ecr.%REGION%.amazonaws.com/%APP_NAME%:latest
echo 📤 Pushing image to ECR...
docker tag %APP_NAME% %ECR_URI%
docker push %ECR_URI%

echo ✅ Image pushed to ECR: %ECR_URI%

REM Create App Runner service configuration
echo 🚀 Creating App Runner service...

REM Create service configuration JSON
(
echo {
echo     "ServiceName": "%APP_NAME%",
echo     "SourceConfiguration": {
echo         "ImageRepository": {
echo             "ImageIdentifier": "%ECR_URI%",
echo             "ImageConfiguration": {
echo                 "Port": "8501",
echo                 "RuntimeEnvironmentVariables": {
echo                     "PORT": "8501",
echo                     "STREAMLIT_SERVER_HEADLESS": "true",
echo                     "STREAMLIT_SERVER_ENABLE_CORS": "false"
echo                 }
echo             },
echo             "ImageRepositoryType": "ECR"
echo         },
echo         "AutoDeploymentsEnabled": false
echo     },
echo     "InstanceConfiguration": {
echo         "Cpu": "1 vCPU",
echo         "Memory": "2 GB",
echo         "InstanceRoleArn": "%SERVICE_ROLE%"
echo     },
echo     "HealthCheckConfiguration": {
echo         "Protocol": "HTTP",
echo         "Path": "/_stcore/health",
echo         "Interval": 10,
echo         "Timeout": 5,
echo         "HealthyThreshold": 1,
echo         "UnhealthyThreshold": 5
echo     }
echo }
) > apprunner-service.json

REM Check if service already exists
aws apprunner describe-service --service-arn "arn:aws:apprunner:%REGION%:%ACCOUNT_ID%:service/%APP_NAME%" >nul 2>&1
if errorlevel 1 (
    echo 🆕 Creating new App Runner service...
    aws apprunner create-service --cli-input-json file://apprunner-service.json --region %REGION%
) else (
    echo 📝 Updating existing App Runner service...
    aws apprunner start-deployment --service-arn "arn:aws:apprunner:%REGION%:%ACCOUNT_ID%:service/%APP_NAME%"
)

REM Clean up
del apprunner-service.json

echo ⏳ Waiting for service to be ready...
aws apprunner wait service-running --service-arn "arn:aws:apprunner:%REGION%:%ACCOUNT_ID%:service/%APP_NAME%"

REM Get service URL
for /f "tokens=*" %%i in ('aws apprunner describe-service --service-arn "arn:aws:apprunner:%REGION%:%ACCOUNT_ID%:service/%APP_NAME%" --query "Service.ServiceUrl" --output text') do set SERVICE_URL=%%i

echo.
echo 🎉 Deployment completed successfully!
echo 📱 Your Text-to-SQL Agent is now available at:
echo 🔗 https://%SERVICE_URL%
echo.
echo 👥 Demo Credentials for your team:
echo    • Admin: admin / admin123
echo    • Demo: demo / demo123
echo    • Analyst: analyst / analyst123
echo.
echo 📊 Monitor your service:
echo    aws apprunner describe-service --service-arn arn:aws:apprunner:%REGION%:%ACCOUNT_ID%:service/%APP_NAME%
echo.
echo 🗑️  To delete the service:
echo    aws apprunner delete-service --service-arn arn:aws:apprunner:%REGION%:%ACCOUNT_ID%:service/%APP_NAME%

pause