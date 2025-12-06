@echo off
echo ============================================
echo Pushing Text-to-SQL Agent to GitHub
echo ============================================
echo.

REM Check if git is initialized
if not exist .git (
    echo Initializing git repository...
    git init
    echo.
)

REM Configure git (update with your details)
echo Configuring git...
git config user.name "Your Name"
git config user.email "your.email@example.com"
echo.

REM Add all files
echo Adding files to git...
git add .
echo.

REM Commit
echo Committing changes...
git commit -m "Initial commit: Text-to-SQL AI Agent with enhanced features"
echo.

REM Instructions for GitHub
echo ============================================
echo Next Steps:
echo ============================================
echo.
echo 1. Create a new repository on GitHub:
echo    - Go to https://github.com/new
echo    - Name: text-to-sql-agent
echo    - Description: AI agent that converts natural language to SQL
echo    - Make it Public or Private
echo    - Do NOT initialize with README
echo.
echo 2. Copy the repository URL (e.g., https://github.com/username/text-to-sql-agent.git)
echo.
echo 3. Run these commands (replace with your URL):
echo    git remote add origin https://github.com/username/text-to-sql-agent.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo ============================================
pause
