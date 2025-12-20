# 🚀 AWS EC2 Deployment Guide - Secure & Production Ready

## 🔐 **Why AWS EC2 is More Secure**

✅ **No Third-Party Secrets** - AWS credentials stay in your AWS account
✅ **IAM Roles** - No hardcoded credentials, uses AWS IAM roles
✅ **Full Control** - Complete control over infrastructure and security
✅ **VPC Security** - Deploy in your own Virtual Private Cloud
✅ **Compliance Ready** - Meets enterprise security requirements

---

## ⚡ **Quick Deployment (10 minutes)**

### **📋 Prerequisites**
- AWS CLI configured (`aws configure`)
- AWS account with EC2, IAM, VPC permissions
- S3 bucket for Athena query results

### **🚀 Option 1: Automated Python Deployment**
```bash
# Run the automated deployment script
python deploy-ec2.py
```

### **🚀 Option 2: Windows Batch Deployment**
```bash
# Run the Windows deployment script
deploy-ec2.bat
```

### **🚀 Option 3: Manual Step-by-Step**
Follow the manual steps below for full control.

---

## 🔧 **Manual Deployment Steps**

### **Step 1: Create IAM Role**
```bash
# Create IAM role for EC2 instance
aws iam create-role \
    --role-name TextToSQLAgentEC2Role \
    --assume-role-policy-document file://trust-policy.json

# Attach policy
aws iam attach-role-policy \
    --role-name TextToSQLAgentEC2Role \
    --policy-arn arn:aws:iam::YOUR_ACCOUNT:policy/TextToSQLAgentEC2Policy

# Create instance profile
aws iam create-instance-profile --instance-profile-name TextToSQLAgentEC2Role
aws iam add-role-to-instance-profile \
    --instance-profile-name TextToSQLAgentEC2Role \
    --role-name TextToSQLAgentEC2Role
```

### **Step 2: Create Security Group**
```bash
# Create security group
aws ec2 create-security-group \
    --group-name text-to-sql-agent-sg \
    --description "Security group for Text-to-SQL Agent"

# Add inbound rules
aws ec2 authorize-security-group-ingress \
    --group-name text-to-sql-agent-sg \
    --protocol tcp --port 80 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-name text-to-sql-agent-sg \
    --protocol tcp --port 443 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-name text-to-sql-agent-sg \
    --protocol tcp --port 22 --cidr 0.0.0.0/0
```

### **Step 3: Launch EC2 Instance**
```bash
# Get latest Ubuntu AMI
AMI_ID=$(aws ec2 describe-images \
    --owners 099720109477 \
    --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-22.04-amd64-server-*" \
    --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
    --output text)

# Launch instance
aws ec2 run-instances \
    --image-id $AMI_ID \
    --count 1 \
    --instance-type t3.medium \
    --security-groups text-to-sql-agent-sg \
    --iam-instance-profile Name=TextToSQLAgentEC2Role \
    --user-data file://user-data.sh \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=Text-to-SQL-Agent}]'
```

---

## 🔐 **Security Configuration**

### **🛡️ IAM Role Permissions**
The EC2 instance uses an IAM role with these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:RetrieveAndGenerate",
                "bedrock:Retrieve"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "athena:StartQueryExecution",
                "athena:GetQueryExecution",
                "athena:GetQueryResults"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "glue:GetDatabase",
                "glue:GetTable",
                "glue:GetTables"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::*athena*",
                "arn:aws:s3:::*athena*/*"
            ]
        }
    ]
}
```

### **🔒 Network Security**
- **Security Group** - Controls inbound/outbound traffic
- **VPC** - Deployed in your default VPC (or specify custom VPC)
- **HTTPS Ready** - Can easily add SSL certificate
- **SSH Access** - For administration and troubleshooting

---

## 📊 **Instance Configuration**

### **🖥️ Instance Specifications**
- **Instance Type**: t3.medium (2 vCPU, 4 GB RAM)
- **Operating System**: Ubuntu 22.04 LTS
- **Storage**: 8 GB GP2 SSD (default)
- **Network**: Public IP with security group

### **📦 Installed Software**
- Python 3.10+
- Streamlit
- AWS CLI v2
- Nginx (reverse proxy)
- Git
- All required Python packages

### **🔧 Service Configuration**
- **Systemd Service** - Auto-starts on boot
- **Nginx Reverse Proxy** - Handles HTTP traffic on port 80
- **Streamlit App** - Runs on internal port 8501
- **Auto-restart** - Service restarts automatically if it fails

---

## 🌐 **Accessing Your Deployment**

### **📱 After Deployment (5-10 minutes)**
1. **Get Public IP** from AWS Console or deployment output
2. **Visit**: `http://YOUR_PUBLIC_IP`
3. **Login** with demo credentials:
   - Admin: `admin` / `admin123`
   - Demo: `demo` / `demo123`
   - Analyst: `analyst` / `analyst123`

### **🔍 Monitoring & Troubleshooting**
```bash
# SSH to instance
ssh -i your-key.pem ubuntu@YOUR_PUBLIC_IP

# Check application status
sudo systemctl status textosql

# View application logs
sudo journalctl -u textosql -f

# Check setup logs
sudo tail -f /var/log/user-data.log

# Restart application
sudo systemctl restart textosql

# Check Nginx status
sudo systemctl status nginx
```

---

## 💰 **Cost Estimation**

### **AWS EC2 Costs (us-east-1)**
- **t3.medium**: ~$30/month (24/7 operation)
- **Storage**: ~$1/month (8 GB)
- **Data Transfer**: ~$1-5/month (depending on usage)
- **Total**: ~$32-36/month

### **Other AWS Services**
- **Bedrock**: Pay per API call (~$0.01-0.10 per query)
- **Athena**: $5 per TB of data scanned
- **S3**: Minimal costs for query results

### **💡 Cost Optimization**
- Use **t3.small** for lighter workloads (~$15/month)
- **Stop instance** when not in use (pay only for storage)
- Use **Spot Instances** for development (up to 90% savings)

---

## 🔧 **Advanced Configuration**

### **🌐 Add HTTPS (SSL Certificate)**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate (requires domain name)
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### **🔒 Restrict SSH Access**
```bash
# Update security group to allow SSH only from your IP
aws ec2 authorize-security-group-ingress \
    --group-name text-to-sql-agent-sg \
    --protocol tcp --port 22 --cidr YOUR_IP/32
```

### **📊 Add CloudWatch Monitoring**
```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb

# Configure monitoring
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

### **🔄 Auto-scaling Setup**
```bash
# Create launch template
aws ec2 create-launch-template \
    --launch-template-name text-to-sql-template \
    --launch-template-data file://launch-template.json

# Create auto-scaling group
aws autoscaling create-auto-scaling-group \
    --auto-scaling-group-name text-to-sql-asg \
    --launch-template LaunchTemplateName=text-to-sql-template \
    --min-size 1 --max-size 3 --desired-capacity 1
```

---

## 🔄 **Updates & Maintenance**

### **🔄 Update Application**
```bash
# SSH to instance
ssh -i your-key.pem ubuntu@YOUR_PUBLIC_IP

# Update code from dev branch
cd /home/textosql/text-to-sql-agent
sudo -u textosql git pull origin dev

# Restart service
sudo systemctl restart textosql
```

### **🔧 System Updates**
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Python packages
sudo -u textosql pip3 install --upgrade -r requirements.txt
sudo -u textosql pip3 install --upgrade -r requirements-web.txt

# Restart services
sudo systemctl restart textosql nginx
```

---

## 🗑️ **Cleanup & Deletion**

### **🗑️ Delete Resources**
```bash
# Terminate EC2 instance
aws ec2 terminate-instances --instance-ids i-1234567890abcdef0

# Delete security group
aws ec2 delete-security-group --group-name text-to-sql-agent-sg

# Delete IAM resources
aws iam remove-role-from-instance-profile \
    --instance-profile-name TextToSQLAgentEC2Role \
    --role-name TextToSQLAgentEC2Role

aws iam delete-instance-profile --instance-profile-name TextToSQLAgentEC2Role

aws iam detach-role-policy \
    --role-name TextToSQLAgentEC2Role \
    --policy-arn arn:aws:iam::YOUR_ACCOUNT:policy/TextToSQLAgentEC2Policy

aws iam delete-role --role-name TextToSQLAgentEC2Role
aws iam delete-policy --policy-arn arn:aws:iam::YOUR_ACCOUNT:policy/TextToSQLAgentEC2Policy
```

---

## 🎯 **Success Checklist**

- [ ] **AWS CLI configured** and working
- [ ] **IAM role created** with proper permissions
- [ ] **Security group configured** with correct ports
- [ ] **EC2 instance launched** successfully
- [ ] **Application accessible** via public IP
- [ ] **Authentication works** with demo credentials
- [ ] **Queries execute** successfully on Athena
- [ ] **Visualizations generate** correctly
- [ ] **All features tested** and working

---

## 🎉 **Your Secure AWS Deployment is Ready!**

### **🌟 What You've Achieved:**
✅ **Secure AWS Deployment** - No third-party credential sharing
✅ **Production-Ready** - Systemd service, Nginx proxy, auto-restart
✅ **Scalable Architecture** - Can easily add load balancing and auto-scaling
✅ **Full Control** - Complete control over infrastructure and security
✅ **Cost-Effective** - Pay only for what you use
✅ **Enterprise-Ready** - Meets security and compliance requirements

### **🔗 Share with Your Team:**
- **URL**: `http://YOUR_PUBLIC_IP`
- **Demo Accounts**: admin/admin123, demo/demo123, analyst/analyst123
- **Features**: Natural language to SQL, interactive visualizations, AI suggestions

**Your Text-to-SQL Agent is now securely deployed on AWS and ready for production use!** 🚀