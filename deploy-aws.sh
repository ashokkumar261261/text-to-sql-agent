#!/bin/bash
# AWS Deployment Script for Text-to-SQL Agent

set -e

echo "🚀 Deploying Text-to-SQL Agent to AWS..."

# Configuration
APP_NAME="text-to-sql-agent"
REGION="us-east-1"
SERVICE_ROLE="arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/AppRunnerInstanceRole"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

echo "✅ AWS CLI configured"

# Build and test Docker image locally first
echo "🔨 Building Docker image..."
docker build -t $APP_NAME .

echo "🧪 Testing Docker image locally..."
docker run -d --name test-container -p 8501:8501 $APP_NAME
sleep 10

# Test if the app is running
if curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
    echo "✅ Local Docker test passed"
    docker stop test-container
    docker rm test-container
else
    echo "❌ Local Docker test failed"
    docker stop test-container
    docker rm test-container
    exit 1
fi

# Create ECR repository if it doesn't exist
echo "📦 Setting up ECR repository..."
aws ecr describe-repositories --repository-names $APP_NAME --region $REGION > /dev/null 2>&1 || \
aws ecr create-repository --repository-name $APP_NAME --region $REGION

# Get ECR login token
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$REGION.amazonaws.com

# Tag and push image
ECR_URI="$(aws sts get-caller-identity --query Account --output text).dkr.ecr.$REGION.amazonaws.com/$APP_NAME:latest"
echo "📤 Pushing image to ECR..."
docker tag $APP_NAME $ECR_URI
docker push $ECR_URI

echo "✅ Image pushed to ECR: $ECR_URI"

# Create App Runner service
echo "🚀 Creating App Runner service..."

# Check if service already exists
if aws apprunner describe-service --service-arn "arn:aws:apprunner:$REGION:$(aws sts get-caller-identity --query Account --output text):service/$APP_NAME" > /dev/null 2>&1; then
    echo "📝 Updating existing App Runner service..."
    aws apprunner start-deployment --service-arn "arn:aws:apprunner:$REGION:$(aws sts get-caller-identity --query Account --output text):service/$APP_NAME"
else
    echo "🆕 Creating new App Runner service..."
    
    # Create service configuration
    cat > apprunner-service.json << EOF
{
    "ServiceName": "$APP_NAME",
    "SourceConfiguration": {
        "ImageRepository": {
            "ImageIdentifier": "$ECR_URI",
            "ImageConfiguration": {
                "Port": "8501",
                "RuntimeEnvironmentVariables": {
                    "PORT": "8501",
                    "STREAMLIT_SERVER_HEADLESS": "true",
                    "STREAMLIT_SERVER_ENABLE_CORS": "false"
                }
            },
            "ImageRepositoryType": "ECR"
        },
        "AutoDeploymentsEnabled": false
    },
    "InstanceConfiguration": {
        "Cpu": "1 vCPU",
        "Memory": "2 GB",
        "InstanceRoleArn": "$SERVICE_ROLE"
    },
    "HealthCheckConfiguration": {
        "Protocol": "HTTP",
        "Path": "/_stcore/health",
        "Interval": 10,
        "Timeout": 5,
        "HealthyThreshold": 1,
        "UnhealthyThreshold": 5
    }
}
EOF

    aws apprunner create-service --cli-input-json file://apprunner-service.json --region $REGION
    rm apprunner-service.json
fi

echo "⏳ Waiting for service to be ready..."
aws apprunner wait service-running --service-arn "arn:aws:apprunner:$REGION:$(aws sts get-caller-identity --query Account --output text):service/$APP_NAME"

# Get service URL
SERVICE_URL=$(aws apprunner describe-service --service-arn "arn:aws:apprunner:$REGION:$(aws sts get-caller-identity --query Account --output text):service/$APP_NAME" --query 'Service.ServiceUrl' --output text)

echo ""
echo "🎉 Deployment completed successfully!"
echo "📱 Your Text-to-SQL Agent is now available at:"
echo "🔗 https://$SERVICE_URL"
echo ""
echo "👥 Demo Credentials for your team:"
echo "   • Admin: admin / admin123"
echo "   • Demo: demo / demo123"
echo "   • Analyst: analyst / analyst123"
echo ""
echo "📊 Monitor your service:"
echo "   aws apprunner describe-service --service-arn arn:aws:apprunner:$REGION:$(aws sts get-caller-identity --query Account --output text):service/$APP_NAME"
echo ""
echo "🗑️  To delete the service:"
echo "   aws apprunner delete-service --service-arn arn:aws:apprunner:$REGION:$(aws sts get-caller-identity --query Account --output text):service/$APP_NAME"