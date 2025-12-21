@echo off
echo Fixing S3 Vectors Permissions for Knowledge Base Creation...
echo ============================================================

echo.
echo Updating IAM User permissions...
aws iam put-user-policy --user-name bedrock-kb-admin --policy-name BedrockKnowledgeBaseUserPolicy --policy-document file://bedrock_user_policy_updated.json

if %errorlevel% equ 0 (
    echo ✅ User permissions updated successfully
) else (
    echo ❌ Failed to update user permissions
)

echo.
echo Updating IAM Role permissions...
aws iam put-role-policy --role-name BedrockKnowledgeBaseRole-Clean --policy-name BedrockKnowledgeBasePolicy --policy-document file://bedrock_role_policy_updated.json

if %errorlevel% equ 0 (
    echo ✅ Role permissions updated successfully
) else (
    echo ❌ Failed to update role permissions
)

echo.
echo ============================================================
echo Permissions Update Complete!
echo.
echo Next steps:
echo 1. Login to AWS Console: https://189796657651.signin.aws.amazon.com/console
echo 2. Username: bedrock-kb-admin
echo 3. Password: BedrockKB2024!
echo 4. Create Knowledge Base using S3 vectors (recommended)
echo 5. Use role: BedrockKnowledgeBaseRole-Clean
echo ============================================================

pause