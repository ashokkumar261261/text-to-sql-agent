# 🚀 Deploy Text-to-SQL Agent to AWS - Quick Guide

## ⚡ **1-Click Deployment to Public URL**

### **📋 Prerequisites**
- AWS CLI configured (`aws configure`)
- Docker installed and running
- AWS account with Bedrock, Athena, App Runner permissions

### **🚀 Step 1: Create IAM Role**
```bash
# Windows
create-iam-role.bat

# Linux/Mac
chmod +x create-iam-role.sh
./create-iam-role.sh
```

### **🌐 Step 2: Deploy to AWS**
```bash
# Windows
deploy-aws.bat

# Linux/Mac
chmod +x deploy-aws.sh
./deploy-aws.sh
```

### **🎉 Step 3: Access Your Public URL**
After deployment completes (5-10 minutes), you'll get:
- **Public URL**: `https://xxxxx.us-east-1.awsapprunner.com`
- **Demo Credentials**:
  - Admin: `admin` / `admin123`
  - Demo: `demo` / `demo123`
  - Analyst: `analyst` / `analyst123`

---

## 🔧 **Manual Deployment Steps**

### **1. Configure AWS Environment**
```bash
# Set your AWS credentials
aws configure

# Verify access
aws sts get-caller-identity
aws bedrock list-foundation-models --region us-east-1
```

### **2. Build and Test Locally**
```bash
# Build Docker image
docker build -t text-to-sql-agent .

# Test locally
docker run -p 8501:8501 text-to-sql-agent
# Visit http://localhost:8501 to test
```

### **3. Push to AWS ECR**
```bash
# Create ECR repository
aws ecr create-repository --repository-name text-to-sql-agent

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag text-to-sql-agent:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/text-to-sql-agent:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/text-to-sql-agent:latest
```

### **4. Create App Runner Service**
```bash
# Use the provided apprunner-service.json configuration
aws apprunner create-service --cli-input-json file://apprunner-service.json
```

---

## 🔐 **Required AWS Permissions**

Your AWS user/role needs these permissions:
- **ECR**: Create repositories, push images
- **App Runner**: Create and manage services
- **IAM**: Create roles and policies
- **Bedrock**: Access AI models
- **Athena**: Execute queries
- **Glue**: Access data catalog
- **S3**: Read/write query results

---

## 💰 **Cost Estimate**

### **AWS App Runner Pricing**
- **Base**: $0.007 per vCPU-hour + $0.0008 per GB-hour
- **Requests**: $0.40 per million requests
- **Estimated Monthly Cost**: $30-60 for small team usage

### **Other AWS Services**
- **Bedrock**: Pay per API call (~$0.01-0.10 per query)
- **Athena**: $5 per TB of data scanned
- **S3**: Minimal storage costs for query results

---

## 📊 **Monitor Your Deployment**

### **Check Service Status**
```bash
aws apprunner describe-service --service-arn arn:aws:apprunner:us-east-1:ACCOUNT:service/text-to-sql-agent
```

### **View Logs**
```bash
aws logs describe-log-groups --log-group-name-prefix "/aws/apprunner/text-to-sql-agent"
aws logs tail /aws/apprunner/text-to-sql-agent --follow
```

### **Update Deployment**
```bash
# Trigger new deployment
aws apprunner start-deployment --service-arn arn:aws:apprunner:us-east-1:ACCOUNT:service/text-to-sql-agent
```

---

## 🛑 **Cleanup (Delete Resources)**

### **Delete App Runner Service**
```bash
aws apprunner delete-service --service-arn arn:aws:apprunner:us-east-1:ACCOUNT:service/text-to-sql-agent
```

### **Delete ECR Repository**
```bash
aws ecr delete-repository --repository-name text-to-sql-agent --force
```

### **Delete IAM Resources**
```bash
aws iam detach-role-policy --role-name AppRunnerTextToSQLRole --policy-arn arn:aws:iam::ACCOUNT:policy/TextToSQLAgentPolicy
aws iam delete-role --role-name AppRunnerTextToSQLRole
aws iam delete-policy --policy-arn arn:aws:iam::ACCOUNT:policy/TextToSQLAgentPolicy
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

**1. Docker build fails**
```bash
# Ensure Docker is running
docker --version
# Check Dockerfile syntax
```

**2. AWS permissions denied**
```bash
# Verify AWS credentials
aws sts get-caller-identity
# Check IAM permissions
```

**3. App Runner service fails to start**
```bash
# Check logs
aws logs tail /aws/apprunner/text-to-sql-agent --follow
# Verify environment variables
```

**4. Application not accessible**
```bash
# Check service status
aws apprunner describe-service --service-arn YOUR_SERVICE_ARN
# Verify health check endpoint
```

---

## 🎯 **Success Checklist**

- [ ] AWS CLI configured and working
- [ ] Docker installed and running
- [ ] IAM role created successfully
- [ ] Docker image builds without errors
- [ ] Image pushed to ECR successfully
- [ ] App Runner service created
- [ ] Service shows as "RUNNING" status
- [ ] Public URL accessible
- [ ] Login works with demo credentials
- [ ] Queries execute successfully

---

## 🎉 **Your Text-to-SQL Agent is Live!**

Once deployed, your team can access the application at the public URL with these features:
- 🔐 **Secure Authentication** - Username/password login
- 🤖 **Natural Language Queries** - Convert English to SQL
- 📊 **Interactive Visualizations** - 5 chart types with customization
- 💡 **AI Suggestions** - Smart query recommendations
- 📜 **Query History** - Track and reuse queries
- 🗂️ **Data Explorer** - Browse database schemas

**Share the URL with your team and start transforming data access!** 🚀