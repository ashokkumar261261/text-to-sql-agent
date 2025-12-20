#!/usr/bin/env python3
"""
Deploy Text-to-SQL Agent to AWS EC2 (No Docker Required)
Secure deployment with IAM roles instead of hardcoded credentials
"""

import boto3
import time
import json
import base64
from pathlib import Path

def create_user_data_script():
    """Create EC2 user data script for automatic setup"""
    user_data = '''#!/bin/bash
# EC2 User Data Script for Text-to-SQL Agent

# Log everything
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
echo "Starting Text-to-SQL Agent setup..."

# Update system
apt-get update -y
apt-get install -y python3 python3-pip git nginx curl

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

# Create application user
useradd -m -s /bin/bash textosql
cd /home/textosql

# Clone repository (dev branch)
git clone -b dev https://github.com/ashokkumar261261/text-to-sql-agent.git
cd text-to-sql-agent

# Install Python dependencies
pip3 install -r requirements.txt
pip3 install -r requirements-web.txt

# Create environment file (using IAM role, no hardcoded credentials)
cat > .env << EOF
AWS_DEFAULT_REGION=us-east-1
ATHENA_DATABASE=default
ATHENA_S3_OUTPUT_LOCATION=s3://your-athena-results-bucket/
ENABLE_CACHE=true
CACHE_TTL=3600
SESSION_TIMEOUT=3600
ENABLE_AUDIT_LOG=true
EOF

# Create systemd service
cat > /etc/systemd/system/textosql.service << EOF
[Unit]
Description=Text-to-SQL Agent Web UI
After=network.target

[Service]
Type=simple
User=textosql
WorkingDirectory=/home/textosql/text-to-sql-agent
Environment=PATH=/usr/local/bin:/usr/bin:/bin
ExecStart=/usr/local/bin/streamlit run web_ui_enhanced.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Set permissions
chown -R textosql:textosql /home/textosql
chmod +x /home/textosql/text-to-sql-agent/web_ui_enhanced.py

# Configure Nginx reverse proxy
cat > /etc/nginx/sites-available/textosql << EOF
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }
}
EOF

# Enable Nginx site
ln -s /etc/nginx/sites-available/textosql /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# Start and enable services
systemctl daemon-reload
systemctl enable textosql
systemctl start textosql
systemctl enable nginx

# Wait for service to start
sleep 30

# Check if service is running
if systemctl is-active --quiet textosql; then
    echo "✅ Text-to-SQL Agent service started successfully"
else
    echo "❌ Text-to-SQL Agent service failed to start"
    systemctl status textosql
fi

echo "🎉 Setup completed! Text-to-SQL Agent should be accessible on port 80"
'''
    return user_data

def create_iam_role():
    """Create IAM role for EC2 instance"""
    iam = boto3.client('iam')
    
    # Trust policy for EC2
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "ec2.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    # IAM policy for Text-to-SQL Agent
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "BedrockAccess",
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                    "bedrock:RetrieveAndGenerate",
                    "bedrock:Retrieve",
                    "bedrock:ListFoundationModels"
                ],
                "Resource": "*"
            },
            {
                "Sid": "AthenaAccess",
                "Effect": "Allow",
                "Action": [
                    "athena:StartQueryExecution",
                    "athena:GetQueryExecution",
                    "athena:GetQueryResults",
                    "athena:StopQueryExecution",
                    "athena:GetWorkGroup"
                ],
                "Resource": "*"
            },
            {
                "Sid": "GlueAccess",
                "Effect": "Allow",
                "Action": [
                    "glue:GetDatabase",
                    "glue:GetDatabases",
                    "glue:GetTable",
                    "glue:GetTables",
                    "glue:GetPartitions"
                ],
                "Resource": "*"
            },
            {
                "Sid": "S3Access",
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket",
                    "s3:PutObject",
                    "s3:DeleteObject"
                ],
                "Resource": [
                    "arn:aws:s3:::*athena*",
                    "arn:aws:s3:::*athena*/*"
                ]
            }
        ]
    }
    
    role_name = "TextToSQLAgentEC2Role"
    policy_name = "TextToSQLAgentEC2Policy"
    
    try:
        # Create IAM role
        print("🔐 Creating IAM role...")
        iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="IAM role for Text-to-SQL Agent EC2 instance"
        )
        
        # Create and attach policy
        print("📋 Creating IAM policy...")
        policy_response = iam.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document),
            Description="Policy for Text-to-SQL Agent EC2 instance"
        )
        
        # Attach policy to role
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_response['Policy']['Arn']
        )
        
        # Create instance profile
        print("👤 Creating instance profile...")
        iam.create_instance_profile(InstanceProfileName=role_name)
        iam.add_role_to_instance_profile(
            InstanceProfileName=role_name,
            RoleName=role_name
        )
        
        # Wait for instance profile to be ready
        print("⏳ Waiting for instance profile to be ready...")
        time.sleep(10)
        
        print(f"✅ IAM role created: {role_name}")
        return role_name
        
    except iam.exceptions.EntityAlreadyExistsException:
        print(f"✅ IAM role already exists: {role_name}")
        return role_name

def create_security_group():
    """Create security group for EC2 instance"""
    ec2 = boto3.client('ec2')
    
    try:
        # Create security group
        response = ec2.create_security_group(
            GroupName='text-to-sql-agent-sg',
            Description='Security group for Text-to-SQL Agent'
        )
        
        sg_id = response['GroupId']
        print(f"🔒 Created security group: {sg_id}")
        
        # Add inbound rules
        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 80,
                    'ToPort': 80,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'HTTP access'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 443,
                    'ToPort': 443,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'HTTPS access'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'SSH access'}]
                }
            ]
        )
        
        return sg_id
        
    except ec2.exceptions.ClientError as e:
        if 'InvalidGroup.Duplicate' in str(e):
            # Get existing security group
            response = ec2.describe_security_groups(
                GroupNames=['text-to-sql-agent-sg']
            )
            sg_id = response['SecurityGroups'][0]['GroupId']
            print(f"✅ Using existing security group: {sg_id}")
            return sg_id
        else:
            raise

def launch_ec2_instance(role_name, security_group_id):
    """Launch EC2 instance with Text-to-SQL Agent"""
    ec2 = boto3.client('ec2')
    
    # Get latest Ubuntu AMI
    response = ec2.describe_images(
        Owners=['099720109477'],  # Canonical
        Filters=[
            {'Name': 'name', 'Values': ['ubuntu/images/hvm-ssd/ubuntu-22.04-amd64-server-*']},
            {'Name': 'state', 'Values': ['available']}
        ]
    )
    
    # Sort by creation date and get latest
    images = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)
    ami_id = images[0]['ImageId']
    print(f"🖥️ Using AMI: {ami_id}")
    
    # Create user data
    user_data = create_user_data_script()
    user_data_b64 = base64.b64encode(user_data.encode()).decode()
    
    # Launch instance
    print("🚀 Launching EC2 instance...")
    response = ec2.run_instances(
        ImageId=ami_id,
        MinCount=1,
        MaxCount=1,
        InstanceType='t3.medium',  # 2 vCPU, 4 GB RAM
        SecurityGroupIds=[security_group_id],
        IamInstanceProfile={'Name': role_name},
        UserData=user_data_b64,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'Name', 'Value': 'Text-to-SQL-Agent'},
                    {'Key': 'Project', 'Value': 'TextToSQLAgent'},
                    {'Key': 'Environment', 'Value': 'Dev'}
                ]
            }
        ]
    )
    
    instance_id = response['Instances'][0]['InstanceId']
    print(f"🎉 Instance launched: {instance_id}")
    
    # Wait for instance to be running
    print("⏳ Waiting for instance to be running...")
    waiter = ec2.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id])
    
    # Get instance details
    response = ec2.describe_instances(InstanceIds=[instance_id])
    instance = response['Reservations'][0]['Instances'][0]
    public_ip = instance.get('PublicIpAddress')
    public_dns = instance.get('PublicDnsName')
    
    return instance_id, public_ip, public_dns

def main():
    """Main deployment function"""
    print("🚀 Deploying Text-to-SQL Agent to AWS EC2...")
    print("=" * 60)
    
    try:
        # Step 1: Create IAM role
        role_name = create_iam_role()
        
        # Step 2: Create security group
        sg_id = create_security_group()
        
        # Step 3: Launch EC2 instance
        instance_id, public_ip, public_dns = launch_ec2_instance(role_name, sg_id)
        
        print("\n" + "=" * 60)
        print("🎉 Deployment completed successfully!")
        print("=" * 60)
        print(f"📋 Instance ID: {instance_id}")
        print(f"🌐 Public IP: {public_ip}")
        print(f"🔗 Public DNS: {public_dns}")
        print(f"🌍 Web URL: http://{public_ip}")
        print("\n📱 Demo Credentials:")
        print("   • Admin: admin / admin123")
        print("   • Demo: demo / demo123")
        print("   • Analyst: analyst / analyst123")
        
        print("\n⏳ Please wait 5-10 minutes for the application to fully start.")
        print("📊 You can monitor the setup progress by SSH'ing to the instance:")
        print(f"   ssh -i your-key.pem ubuntu@{public_ip}")
        print("   tail -f /var/log/user-data.log")
        
        print("\n🔧 To manage the service:")
        print("   sudo systemctl status textosql")
        print("   sudo systemctl restart textosql")
        print("   sudo journalctl -u textosql -f")
        
        print("\n🗑️ To delete the deployment:")
        print(f"   aws ec2 terminate-instances --instance-ids {instance_id}")
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure AWS CLI is configured with proper permissions")
        print("2. Check if you have EC2, IAM, and VPC permissions")
        print("3. Verify your AWS region is set correctly")

if __name__ == "__main__":
    main()