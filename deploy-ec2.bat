@echo off
REM Deploy Text-to-SQL Agent to AWS EC2 (Windows)

echo 🚀 Deploying Text-to-SQL Agent to AWS EC2...
echo ============================================

REM Check AWS CLI
aws sts get-caller-identity >nul 2>&1
if errorlevel 1 (
    echo ❌ AWS CLI not configured. Please run 'aws configure' first.
    exit /b 1
)

echo ✅ AWS CLI configured

REM Get AWS Account ID
for /f "tokens=*" %%i in ('aws sts get-caller-identity --query Account --output text') do set ACCOUNT_ID=%%i

REM Configuration
set ROLE_NAME=TextToSQLAgentEC2Role
set SG_NAME=text-to-sql-agent-sg
set INSTANCE_TYPE=t3.medium
set KEY_NAME=your-key-pair

echo 🔐 Creating IAM role and policies...

REM Create trust policy
(
echo {
echo     "Version": "2012-10-17",
echo     "Statement": [
echo         {
echo             "Effect": "Allow",
echo             "Principal": {
echo                 "Service": "ec2.amazonaws.com"
echo             },
echo             "Action": "sts:AssumeRole"
echo         }
echo     ]
echo }
) > trust-policy.json

REM Create IAM role
aws iam create-role --role-name %ROLE_NAME% --assume-role-policy-document file://trust-policy.json --description "IAM role for Text-to-SQL Agent EC2" 2>nul || echo Role may already exist

REM Create and attach policy
aws iam create-policy --policy-name TextToSQLAgentEC2Policy --policy-document file://iam-role-policy.json --description "Policy for Text-to-SQL Agent EC2" 2>nul || echo Policy may already exist
aws iam attach-role-policy --role-name %ROLE_NAME% --policy-arn "arn:aws:iam::%ACCOUNT_ID%:policy/TextToSQLAgentEC2Policy"

REM Create instance profile
aws iam create-instance-profile --instance-profile-name %ROLE_NAME% 2>nul || echo Instance profile may already exist
aws iam add-role-to-instance-profile --instance-profile-name %ROLE_NAME% --role-name %ROLE_NAME% 2>nul

echo 🔒 Creating security group...

REM Create security group
aws ec2 create-security-group --group-name %SG_NAME% --description "Security group for Text-to-SQL Agent" 2>nul || echo Security group may already exist

REM Get security group ID
for /f "tokens=*" %%i in ('aws ec2 describe-security-groups --group-names %SG_NAME% --query "SecurityGroups[0].GroupId" --output text') do set SG_ID=%%i

REM Add security group rules
aws ec2 authorize-security-group-ingress --group-id %SG_ID% --protocol tcp --port 80 --cidr 0.0.0.0/0 2>nul || echo Rule may already exist
aws ec2 authorize-security-group-ingress --group-id %SG_ID% --protocol tcp --port 443 --cidr 0.0.0.0/0 2>nul || echo Rule may already exist
aws ec2 authorize-security-group-ingress --group-id %SG_ID% --protocol tcp --port 22 --cidr 0.0.0.0/0 2>nul || echo Rule may already exist

echo 🖥️ Getting latest Ubuntu AMI...

REM Get latest Ubuntu 22.04 AMI
for /f "tokens=*" %%i in ('aws ec2 describe-images --owners 099720109477 --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-22.04-amd64-server-*" "Name=state,Values=available" --query "Images | sort_by(@, &CreationDate) | [-1].ImageId" --output text') do set AMI_ID=%%i

echo 📝 Creating user data script...

REM Create user data script
(
echo #!/bin/bash
echo # EC2 User Data Script for Text-to-SQL Agent
echo exec ^> ^^(tee /var/log/user-data.log^|logger -t user-data -s 2^>/dev/console^^) 2^>^&1
echo echo "Starting Text-to-SQL Agent setup..."
echo apt-get update -y
echo apt-get install -y python3 python3-pip git nginx curl
echo curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
echo unzip awscliv2.zip
echo ./aws/install
echo useradd -m -s /bin/bash textosql
echo cd /home/textosql
echo git clone -b dev https://github.com/ashokkumar261261/text-to-sql-agent.git
echo cd text-to-sql-agent
echo pip3 install -r requirements.txt
echo pip3 install -r requirements-web.txt
echo cat ^> .env ^<^< EOF
echo AWS_DEFAULT_REGION=us-east-1
echo ATHENA_DATABASE=default
echo ATHENA_S3_OUTPUT_LOCATION=s3://your-athena-results-bucket/
echo ENABLE_CACHE=true
echo CACHE_TTL=3600
echo EOF
echo cat ^> /etc/systemd/system/textosql.service ^<^< EOF
echo [Unit]
echo Description=Text-to-SQL Agent Web UI
echo After=network.target
echo [Service]
echo Type=simple
echo User=textosql
echo WorkingDirectory=/home/textosql/text-to-sql-agent
echo Environment=PATH=/usr/local/bin:/usr/bin:/bin
echo ExecStart=/usr/local/bin/streamlit run web_ui_enhanced.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
echo Restart=always
echo RestartSec=10
echo [Install]
echo WantedBy=multi-user.target
echo EOF
echo chown -R textosql:textosql /home/textosql
echo cat ^> /etc/nginx/sites-available/textosql ^<^< EOF
echo server {
echo     listen 80;
echo     server_name _;
echo     location / {
echo         proxy_pass http://127.0.0.1:8501;
echo         proxy_http_version 1.1;
echo         proxy_set_header Upgrade \$http_upgrade;
echo         proxy_set_header Connection "upgrade";
echo         proxy_set_header Host \$host;
echo         proxy_set_header X-Real-IP \$remote_addr;
echo         proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
echo         proxy_set_header X-Forwarded-Proto \$scheme;
echo         proxy_read_timeout 86400;
echo     }
echo }
echo EOF
echo ln -s /etc/nginx/sites-available/textosql /etc/nginx/sites-enabled/
echo rm -f /etc/nginx/sites-enabled/default
echo nginx -t ^&^& systemctl restart nginx
echo systemctl daemon-reload
echo systemctl enable textosql
echo systemctl start textosql
echo systemctl enable nginx
echo sleep 30
echo echo "🎉 Setup completed!"
) > user-data.sh

echo 🚀 Launching EC2 instance...

REM Launch EC2 instance
for /f "tokens=*" %%i in ('aws ec2 run-instances --image-id %AMI_ID% --count 1 --instance-type %INSTANCE_TYPE% --security-group-ids %SG_ID% --iam-instance-profile Name=%ROLE_NAME% --user-data file://user-data.sh --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=Text-to-SQL-Agent},{Key=Project,Value=TextToSQLAgent}]" --query "Instances[0].InstanceId" --output text') do set INSTANCE_ID=%%i

echo ⏳ Waiting for instance to be running...
aws ec2 wait instance-running --instance-ids %INSTANCE_ID%

REM Get instance details
for /f "tokens=*" %%i in ('aws ec2 describe-instances --instance-ids %INSTANCE_ID% --query "Reservations[0].Instances[0].PublicIpAddress" --output text') do set PUBLIC_IP=%%i
for /f "tokens=*" %%i in ('aws ec2 describe-instances --instance-ids %INSTANCE_ID% --query "Reservations[0].Instances[0].PublicDnsName" --output text') do set PUBLIC_DNS=%%i

REM Cleanup
del trust-policy.json
del user-data.sh

echo.
echo ============================================
echo 🎉 Deployment completed successfully!
echo ============================================
echo 📋 Instance ID: %INSTANCE_ID%
echo 🌐 Public IP: %PUBLIC_IP%
echo 🔗 Public DNS: %PUBLIC_DNS%
echo 🌍 Web URL: http://%PUBLIC_IP%
echo.
echo 📱 Demo Credentials:
echo    • Admin: admin / admin123
echo    • Demo: demo / demo123
echo    • Analyst: analyst / analyst123
echo.
echo ⏳ Please wait 5-10 minutes for the application to fully start.
echo.
echo 🗑️ To delete the deployment:
echo    aws ec2 terminate-instances --instance-ids %INSTANCE_ID%

pause