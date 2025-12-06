# Windows Setup Guide

## Python on Windows

On Windows, use `py` command instead of `python`:

```powershell
# Check Python version
py --version

# Run scripts
py example.py

# Install packages
py -m pip install -r requirements.txt
```

## Quick Start

1. **Install dependencies:**
```powershell
cd text-to-sql-agent
py -m pip install -r requirements.txt
```

2. **Configure environment:**
```powershell
copy .env.example .env
# Edit .env with your AWS settings
```

3. **Configure AWS credentials:**
```powershell
aws configure
```

4. **Run example:**
```powershell
py example.py
```

## Common Commands

```powershell
# Create virtual environment (recommended)
py -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies in venv
py -m pip install -r requirements.txt

# Run the agent
py example.py

# Setup sample Glue database
py setup_glue_sample.py
```

## Troubleshooting

### Python not found
- Use `py` instead of `python`
- Or add Python to PATH in Windows settings

### PowerShell execution policy
If you get script execution errors:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### AWS credentials
Make sure you have:
- AWS CLI installed
- Credentials configured (`aws configure`)
- Proper IAM permissions (see IAM_PERMISSIONS.md)
