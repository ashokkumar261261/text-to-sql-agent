@echo off
REM Create IAM role for App Runner service (Windows)

set ROLE_NAME=AppRunnerTextToSQLRole
set POLICY_NAME=TextToSQLAgentPolicy

echo 🔐 Creating IAM role for Text-to-SQL Agent...

REM Get AWS Account ID
for /f "tokens=*" %%i in ('aws sts get-caller-identity --query Account --output text') do set ACCOUNT_ID=%%i

REM Create trust policy for App Runner
(
echo {
echo     "Version": "2012-10-17",
echo     "Statement": [
echo         {
echo             "Effect": "Allow",
echo             "Principal": {
echo                 "Service": "tasks.apprunner.amazonaws.com"
echo             },
echo             "Action": "sts:AssumeRole"
echo         }
echo     ]
echo }
) > trust-policy.json

REM Create the IAM role
echo 📝 Creating IAM role: %ROLE_NAME%
aws iam create-role --role-name %ROLE_NAME% --assume-role-policy-document file://trust-policy.json --description "IAM role for Text-to-SQL Agent App Runner service" 2>nul || echo Role may already exist

REM Create and attach the policy
echo 📋 Creating IAM policy: %POLICY_NAME%
aws iam create-policy --policy-name %POLICY_NAME% --policy-document file://iam-role-policy.json --description "Policy for Text-to-SQL Agent to access AWS services" 2>nul || echo Policy may already exist

REM Attach policy to role
echo 🔗 Attaching policy to role
aws iam attach-role-policy --role-name %ROLE_NAME% --policy-arn "arn:aws:iam::%ACCOUNT_ID%:policy/%POLICY_NAME%"

REM Clean up temporary files
del trust-policy.json

echo ✅ IAM role created successfully!
echo 📋 Role ARN: arn:aws:iam::%ACCOUNT_ID%:role/%ROLE_NAME%
echo.
echo 🚀 Now you can run: deploy-aws.bat

pause