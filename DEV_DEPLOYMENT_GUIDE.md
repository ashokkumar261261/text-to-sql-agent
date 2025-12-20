# 🚀 Dev Branch Deployment Guide - Streamlit Cloud

## ⚡ **Quick Deployment from Dev Branch**

### **🎯 Objective**
Deploy the Text-to-SQL Agent from the `dev` branch to get a public URL for testing before merging to main.

---

## 🌐 **Option 1: Streamlit Cloud (Recommended - No Docker)**

### **📋 Prerequisites**
- GitHub account
- AWS credentials (Access Key ID & Secret)
- Athena database and S3 bucket configured

### **🚀 Deployment Steps**

#### **1. Access Streamlit Cloud**
- Visit: [share.streamlit.io](https://share.streamlit.io)
- Sign in with GitHub account
- Click "New app"

#### **2. Configure App**
- **Repository**: `ashokkumar261261/text-to-sql-agent`
- **Branch**: `dev` ⚠️ **Important: Use dev branch**
- **Main file**: `web_ui_enhanced.py`
- **App URL**: `text-to-sql-demo-dev` (or your choice)

#### **3. Add Secrets (Environment Variables)**
In "Advanced settings" → "Secrets", paste:

```toml
# AWS Configuration
AWS_DEFAULT_REGION = "us-east-1"
AWS_ACCESS_KEY_ID = "AKIA..."  # Your actual key
AWS_SECRET_ACCESS_KEY = "..."  # Your actual secret

# Athena Configuration
ATHENA_DATABASE = "default"  # Your database name
ATHENA_S3_OUTPUT_LOCATION = "s3://your-bucket/athena-results/"

# Optional: Knowledge Base
BEDROCK_KNOWLEDGE_BASE_ID = "JKGJVVWBDY"  # If you have KB setup
KB_CONFIDENCE_THRESHOLD = "0.7"

# Performance
ENABLE_CACHE = "true"
CACHE_TTL = "3600"
```

#### **4. Deploy**
- Click "Deploy!"
- Wait 2-3 minutes for deployment
- Your app will be available at: `https://text-to-sql-demo-dev.streamlit.app`

---

## 🧪 **Testing Your Deployment**

### **🔐 Test Authentication**
1. Visit your Streamlit Cloud URL
2. Try logging in with demo accounts:
   - **Admin**: `admin` / `admin123`
   - **Demo**: `demo` / `demo123`
   - **Analyst**: `analyst` / `analyst123`

### **🤖 Test Natural Language Queries**
Try these sample queries:
```
"Show me top 5 customers by revenue"
"What are the trending products this month?"
"Find customers in California"
"Show me sales by region"
```

### **📊 Test Visualizations**
1. Execute a query that returns data
2. Check if charts are generated automatically
3. Try changing chart types (Bar → Line → Scatter)
4. Test X/Y axis customization

### **💡 Test AI Suggestions**
1. Go to "Suggestions" tab
2. Check if AI-powered suggestions appear
3. Click on a suggestion to insert it into query tab
4. Process the suggested query

### **📜 Test Query History**
1. Execute several queries
2. Go to "History" tab
3. Verify queries are saved with timestamps
4. Try re-running a previous query

### **🗂️ Test Data Explorer**
1. Go to "Sample Data" tab
2. Check if database tables are listed
3. Verify sample data is displayed
4. Test table schema information

---

## 🔧 **Troubleshooting Common Issues**

### **❌ App Won't Start**
**Problem**: Deployment fails or app crashes
**Solutions**:
1. Check Streamlit Cloud logs for errors
2. Verify all required files are in dev branch
3. Ensure `requirements-web.txt` includes all dependencies

### **❌ AWS Connection Failed**
**Problem**: "AWS credentials not found" or similar
**Solutions**:
1. Double-check AWS credentials in Secrets
2. Verify AWS region is correct (`us-east-1`)
3. Test AWS access: `aws sts get-caller-identity`

### **❌ Athena Queries Fail**
**Problem**: "Database not found" or query execution errors
**Solutions**:
1. Verify `ATHENA_DATABASE` name in secrets
2. Check `ATHENA_S3_OUTPUT_LOCATION` bucket exists
3. Ensure IAM permissions for Athena access

### **❌ Knowledge Base Not Working**
**Problem**: KB suggestions not appearing
**Solutions**:
1. Verify `BEDROCK_KNOWLEDGE_BASE_ID` is correct
2. Check Bedrock permissions in IAM
3. KB is optional - app works without it

### **❌ Authentication Issues**
**Problem**: Login not working
**Solutions**:
1. Use exact credentials: `demo` / `demo123`
2. Clear browser cache and cookies
3. Try different demo account

---

## 📊 **Monitoring Your Dev Deployment**

### **📈 Streamlit Cloud Dashboard**
- Monitor app status and logs
- View deployment history
- Check resource usage
- Manage secrets and settings

### **🔍 Application Logs**
- Check Streamlit Cloud logs for errors
- Monitor query execution times
- Track user authentication attempts
- Review AWS API calls

### **⚡ Performance Monitoring**
- Query response times
- Cache hit rates
- Memory usage
- Error rates

---

## 🎯 **Success Checklist**

Before merging to main, verify:

- [ ] **App deploys successfully** from dev branch
- [ ] **Authentication works** with all demo accounts
- [ ] **Natural language queries** convert to SQL
- [ ] **Query execution** works with Athena
- [ ] **Visualizations** generate correctly
- [ ] **Chart customization** works (X/Y axes, chart types)
- [ ] **AI suggestions** appear and work
- [ ] **Query history** saves and retrieves
- [ ] **Data explorer** shows tables and schemas
- [ ] **Knowledge Base** integration works (if configured)
- [ ] **Error handling** is graceful
- [ ] **Performance** is acceptable (< 5 seconds per query)

---

## 🔄 **Update Process**

### **Making Changes**
1. Make changes in local dev branch
2. Test locally: `streamlit run web_ui_enhanced.py`
3. Commit and push to dev branch
4. Streamlit Cloud auto-deploys changes
5. Test the updated deployment

### **When Ready for Production**
1. Verify all tests pass on dev deployment
2. Create pull request: dev → main
3. Merge to main branch
4. Deploy production version from main branch

---

## 🎉 **Expected Result**

After successful deployment, you'll have:

- **🌐 Public URL**: `https://your-app-name.streamlit.app`
- **🔐 Secure Access**: Authentication-protected interface
- **🤖 AI-Powered**: Natural language to SQL conversion
- **📊 Interactive**: Customizable data visualizations
- **💡 Smart**: AI-powered query suggestions
- **📱 Professional**: Clean, branded interface
- **⚡ Fast**: Cached responses and optimized performance

**Share the URL with your team for testing and feedback!** 🚀

---

## 📞 **Need Help?**

If you encounter issues:
1. Check Streamlit Cloud logs
2. Verify AWS credentials and permissions
3. Test individual components locally
4. Review the troubleshooting section above

**Once everything works perfectly on dev, we'll merge to main!** ✅