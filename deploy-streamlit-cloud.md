# 🚀 Deploy to Streamlit Cloud (No Docker Required)

## ⚡ **Easiest Deployment Option - 5 Minutes**

### **🌟 Why Streamlit Cloud?**
- ✅ **No Docker required** - Direct from GitHub
- ✅ **Free tier available** - Perfect for demos
- ✅ **Automatic HTTPS** - Secure public URL
- ✅ **Easy updates** - Auto-deploy from GitHub
- ✅ **Built-in secrets management** - Secure AWS credentials

---

## 🚀 **Step-by-Step Deployment**

### **1. Push Code to GitHub (if not already done)**
```bash
cd text-to-sql-agent
git add .
git commit -m "Add deployment configuration"
git push origin main
```

### **2. Deploy to Streamlit Cloud**

#### **🌐 Visit Streamlit Cloud**
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"

#### **⚙️ Configure Deployment**
- **Repository**: `ashokkumar261261/text-to-sql-agent`
- **Branch**: `main`
- **Main file path**: `web_ui_enhanced.py`
- **App URL**: Choose your custom URL (e.g., `text-to-sql-demo`)

#### **🔐 Add Secrets (Environment Variables)**
In the "Advanced settings" → "Secrets", add:

```toml
# AWS Configuration
AWS_DEFAULT_REGION = "us-east-1"
AWS_ACCESS_KEY_ID = "your_access_key_here"
AWS_SECRET_ACCESS_KEY = "your_secret_key_here"

# Athena Configuration
ATHENA_DATABASE = "your_database_name"
ATHENA_S3_OUTPUT_LOCATION = "s3://your-results-bucket/"

# Optional: Knowledge Base
BEDROCK_KNOWLEDGE_BASE_ID = "your_kb_id"
KB_CONFIDENCE_THRESHOLD = "0.7"

# Performance Settings
ENABLE_CACHE = "true"
CACHE_TTL = "3600"
```

### **3. Deploy and Access**
1. Click "Deploy!"
2. Wait 2-3 minutes for deployment
3. Your app will be available at: `https://your-app-name.streamlit.app`

---

## 🔧 **Alternative: AWS EC2 Deployment**

### **🖥️ Launch EC2 Instance**
```bash
# Launch Ubuntu instance
aws ec2 run-instances \
    --image-id ami-0c02fb55956c7d316 \
    --instance-type t3.medium \
    --key-name your-key-pair \
    --security-group-ids sg-xxxxxxxxx \
    --user-data file://user-data.sh
```

### **📄 Create user-data.sh**
```bash
#!/bin/bash
# EC2 User Data Script

# Update system
apt-get update -y
apt-get install -y python3 python3-pip git

# Clone repository
cd /home/ubuntu
git clone https://github.com/ashokkumar261261/text-to-sql-agent.git
cd text-to-sql-agent

# Install dependencies
pip3 install -r requirements.txt
pip3 install -r requirements-web.txt

# Configure AWS credentials (use IAM role instead)
# aws configure set aws_access_key_id YOUR_KEY
# aws configure set aws_secret_access_key YOUR_SECRET
# aws configure set default.region us-east-1

# Start application
nohup streamlit run web_ui_enhanced.py --server.port=8501 --server.address=0.0.0.0 &
```

### **🔐 Security Group Configuration**
Allow inbound traffic:
- **Port 8501** (HTTP) from 0.0.0.0/0
- **Port 22** (SSH) from your IP only

---

## 🌐 **Alternative: Heroku Deployment**

### **📄 Create Procfile**
```bash
echo "web: streamlit run web_ui_enhanced.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile
```

### **📄 Create runtime.txt**
```bash
echo "python-3.9.18" > runtime.txt
```

### **🚀 Deploy to Heroku**
```bash
# Install Heroku CLI first
heroku create your-app-name
heroku config:set AWS_ACCESS_KEY_ID=your_key
heroku config:set AWS_SECRET_ACCESS_KEY=your_secret
heroku config:set AWS_DEFAULT_REGION=us-east-1
heroku config:set ATHENA_DATABASE=your_database
heroku config:set ATHENA_S3_OUTPUT_LOCATION=s3://your-bucket/

git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

---

## 🎯 **Recommended: Streamlit Cloud**

For your use case, **Streamlit Cloud is the best option** because:

1. **✅ No Docker required** - Works directly from GitHub
2. **✅ Free tier** - Perfect for demos and small teams
3. **✅ Easy setup** - 5-minute deployment
4. **✅ Automatic HTTPS** - Secure public URL
5. **✅ Built-in secrets** - Secure AWS credential management
6. **✅ Auto-updates** - Deploys automatically from GitHub

---

## 🚀 **Quick Start with Streamlit Cloud**

### **Right Now - 5 Minutes:**

1. **Visit**: [share.streamlit.io](https://share.streamlit.io)
2. **Sign in** with GitHub
3. **New app** → Repository: `ashokkumar261261/text-to-sql-agent`
4. **Main file**: `web_ui_enhanced.py`
5. **Add secrets** (AWS credentials)
6. **Deploy!**

### **Result:**
- **Public URL**: `https://your-app.streamlit.app`
- **Demo Accounts**: 
  - `admin` / `admin123`
  - `demo` / `demo123`
  - `analyst` / `analyst123`

---

## 🎉 **Your Text-to-SQL Agent Will Be Live!**

Once deployed, your team can access:
- 🔐 **Secure login** with demo accounts
- 🤖 **Natural language queries** → SQL conversion
- 📊 **Interactive visualizations** with 5 chart types
- 💡 **AI-powered suggestions** for queries
- 📜 **Query history** and management
- 🗂️ **Database schema explorer**

**Share the Streamlit Cloud URL with your team and start transforming data access!** 🚀