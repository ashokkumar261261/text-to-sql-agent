param(
    [Parameter(Mandatory=$true)]
    [string]$FunctionName
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Deploying Text-to-SQL Lambda Function" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Function Name: $FunctionName" -ForegroundColor Yellow
Write-Host ""

# Create deployment package
Write-Host "Creating deployment package..." -ForegroundColor Green

# Remove existing package
if (Test-Path "lambda_deployment.zip") {
    Remove-Item "lambda_deployment.zip" -Force
}

# Create temporary directory
if (Test-Path "temp_deploy") {
    Remove-Item "temp_deploy" -Recurse -Force
}
New-Item -ItemType Directory -Name "temp_deploy" | Out-Null

# Copy files
Copy-Item "lambda_function.py" "temp_deploy/"
if (Test-Path "kb_documents") {
    Copy-Item "kb_documents" "temp_deploy/" -Recurse
}

# Create zip package
Compress-Archive -Path "temp_deploy/*" -DestinationPath "lambda_deployment.zip" -Force

# Clean up temp directory
Remove-Item "temp_deploy" -Recurse -Force

Write-Host "Deployment package created: lambda_deployment.zip" -ForegroundColor Green
Write-Host ""

# Deploy to AWS Lambda
Write-Host "Deploying to AWS Lambda..." -ForegroundColor Green

try {
    $result = aws lambda update-function-code `
        --function-name $FunctionName `
        --zip-file fileb://lambda_deployment.zip `
        --region us-east-1 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Lambda function updated successfully!" -ForegroundColor Green
        Write-Host ""
        
        Write-Host "Testing the function..." -ForegroundColor Yellow
        $testResult = aws lambda invoke `
            --function-name $FunctionName `
            --payload '{"requestContext":{"http":{"method":"GET"}}}' `
            --region us-east-1 `
            response.json 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "🚀 Your Lambda function is now updated with the fixes!" -ForegroundColor Green
            Write-Host "Try your query 'Show me top 5 customers by revenue' again in the web UI." -ForegroundColor Cyan
            Write-Host ""
            
            # Show function URL if available
            Write-Host "Getting function URL..." -ForegroundColor Yellow
            $urlResult = aws lambda get-function-url-config --function-name $FunctionName --region us-east-1 2>&1
            if ($LASTEXITCODE -eq 0) {
                $urlData = $urlResult | ConvertFrom-Json
                Write-Host "🌐 Function URL: $($urlData.FunctionUrl)" -ForegroundColor Cyan
            } else {
                Write-Host "ℹ️  No function URL configured. You can create one with:" -ForegroundColor Yellow
                Write-Host "aws lambda create-function-url-config --function-name $FunctionName --auth-type NONE --region us-east-1" -ForegroundColor Gray
            }
        }
    } else {
        throw "AWS CLI command failed"
    }
} catch {
    Write-Host ""
    Write-Host "❌ Deployment failed. Please check:" -ForegroundColor Red
    Write-Host "1. AWS credentials are configured: aws configure" -ForegroundColor Yellow
    Write-Host "2. Lambda function exists: aws lambda get-function --function-name $FunctionName" -ForegroundColor Yellow
    Write-Host "3. You have permissions to update Lambda functions" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Error details:" -ForegroundColor Red
    Write-Host $result -ForegroundColor Red
}

# Clean up
if (Test-Path "lambda_deployment.zip") {
    Remove-Item "lambda_deployment.zip" -Force
}
if (Test-Path "response.json") {
    Remove-Item "response.json" -Force
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")