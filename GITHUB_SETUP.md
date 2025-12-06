# GitHub Setup Guide

## Step-by-Step Instructions

### 1. Configure Git (First Time Only)

Open PowerShell and run:

```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 2. Initialize Git Repository

```powershell
cd text-to-sql-agent
git init
```

### 3. Add Files to Git

```powershell
git add .
```

### 4. Commit Changes

```powershell
git commit -m "Initial commit: Text-to-SQL AI Agent with enhanced features"
```

### 5. Create GitHub Repository

1. Go to https://github.com/new
2. Fill in:
   - **Repository name**: `text-to-sql-agent`
   - **Description**: `AI agent that converts natural language to SQL queries using AWS Bedrock and Athena`
   - **Visibility**: Public or Private (your choice)
   - **DO NOT** check "Initialize with README" (we already have one)
3. Click "Create repository"

### 6. Link Local Repository to GitHub

Copy the repository URL from GitHub (looks like: `https://github.com/username/text-to-sql-agent.git`)

Then run:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/text-to-sql-agent.git
git branch -M main
git push -u origin main
```

### 7. Verify

Go to your GitHub repository URL and verify all files are there!

## Quick Commands Reference

```powershell
# Check status
git status

# Add new changes
git add .

# Commit changes
git commit -m "Your commit message"

# Push to GitHub
git push

# Pull latest changes
git pull

# View commit history
git log --oneline
```

## What Gets Pushed

✅ **Included:**
- All source code
- Documentation
- Configuration files
- Examples
- Requirements

❌ **Excluded (via .gitignore):**
- `.env` file (contains secrets)
- `.cache/` folder
- `.history/` folder
- `__pycache__/` folders
- Virtual environments

## Troubleshooting

### "Git is not recognized"
Install Git from: https://git-scm.com/download/win

### "Permission denied"
Use HTTPS URL instead of SSH, or set up SSH keys:
https://docs.github.com/en/authentication/connecting-to-github-with-ssh

### "Remote already exists"
```powershell
git remote remove origin
git remote add origin YOUR_GITHUB_URL
```

### "Nothing to commit"
```powershell
git add .
git commit -m "Your message"
```

## Repository Description

Use this for your GitHub repository description:

```
🔍 AI-powered Text-to-SQL agent that converts natural language questions into SQL queries. 
Features: Query validation, result caching, AI explanations, conversation history, and a 
beautiful web UI. Built with AWS Bedrock, Athena, and Glue Catalog.
```

## Topics/Tags

Add these topics to your GitHub repository:
- `ai`
- `aws`
- `bedrock`
- `athena`
- `sql`
- `natural-language-processing`
- `text-to-sql`
- `streamlit`
- `python`
- `data-analytics`

## README Badges

Your README already includes badges for:
- Python version
- AWS services
- License

## Next Steps After Pushing

1. ⭐ Star your own repository
2. 📝 Add topics/tags
3. 🔗 Share the link
4. 📊 Enable GitHub Pages (optional)
5. 🤝 Invite collaborators (optional)

Enjoy your GitHub repository! 🎉
