# PowerShell script to create Knowledge Base with IAM credentials

Write-Host "🚀 Creating Knowledge Base with IAM credentials..." -ForegroundColor Green

# Generate unique index name
$timestamp = [int][double]::Parse((Get-Date -UFormat %s))
$indexName = "kb-clean-$timestamp"

Write-Host "📝 Using index name: $indexName" -ForegroundColor Yellow

# Create Knowledge Base configuration
$kbConfig = @{
    name = "text-to-sql-kb-clean"
    description = "Clean Knowledge Base with simple SQL patterns"
    roleArn = "arn:aws:iam::189796657651:role/BedrockKnowledgeBaseRole"
    knowledgeBaseConfiguration = @{
        type = "VECTOR"
        vectorKnowledgeBaseConfiguration = @{
            embeddingModelArn = "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1"
        }
    }
    storageConfiguration = @{
        type = "OPENSEARCH_SERVERLESS"
        opensearchServerlessConfiguration = @{
            collectionArn = "arn:aws:aoss:us-east-1:189796657651:collection/e9ex0v2xiya5ccb91445"
            vectorIndexName = $indexName
            fieldMapping = @{
                vectorField = "vector"
                textField = "text"
                metadataField = "metadata"
            }
        }
    }
} | ConvertTo-Json -Depth 10

# Save configuration to file
$kbConfig | Out-File -FilePath "kb_final_config.json" -Encoding UTF8

Write-Host "🔨 Creating Knowledge Base..." -ForegroundColor Green

# Create Knowledge Base
try {
    $kbResult = aws bedrock-agent create-knowledge-base --cli-input-json file://kb_final_config.json | ConvertFrom-Json
    $kbId = $kbResult.knowledgeBase.knowledgeBaseId
    Write-Host "✅ Knowledge Base created: $kbId" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create Knowledge Base: $_" -ForegroundColor Red
    exit 1
}

# Create Data Source configuration
$dsConfig = @{
    knowledgeBaseId = $kbId
    name = "s3-clean-source"
    description = "S3 source with clean SQL patterns"
    dataSourceConfiguration = @{
        type = "S3"
        s3Configuration = @{
            bucketArn = "arn:aws:s3:::text-to-sql-kb-demo-2024"
        }
    }
} | ConvertTo-Json -Depth 10

$dsConfig | Out-File -FilePath "ds_config.json" -Encoding UTF8

Write-Host "📂 Creating Data Source..." -ForegroundColor Green

# Create Data Source
try {
    $dsResult = aws bedrock-agent create-data-source --cli-input-json file://ds_config.json | ConvertFrom-Json
    $dsId = $dsResult.dataSource.dataSourceId
    Write-Host "✅ Data Source created: $dsId" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create Data Source: $_" -ForegroundColor Red
    exit 1
}

# Start Ingestion
Write-Host "🔄 Starting ingestion job..." -ForegroundColor Green

try {
    $ingestionResult = aws bedrock-agent start-ingestion-job --knowledge-base-id $kbId --data-source-id $dsId | ConvertFrom-Json
    $jobId = $ingestionResult.ingestionJob.ingestionJobId
    Write-Host "✅ Ingestion job started: $jobId" -ForegroundColor Green
    
    # Wait for ingestion to complete
    Write-Host "⏳ Waiting for ingestion to complete..." -ForegroundColor Yellow
    
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Seconds 10
        $statusResult = aws bedrock-agent get-ingestion-job --knowledge-base-id $kbId --data-source-id $dsId --ingestion-job-id $jobId | ConvertFrom-Json
        $status = $statusResult.ingestionJob.status
        Write-Host "📊 Ingestion status: $status" -ForegroundColor Yellow
        
        if ($status -eq "COMPLETE") {
            Write-Host "✅ Ingestion completed successfully!" -ForegroundColor Green
            break
        } elseif ($status -eq "FAILED") {
            Write-Host "❌ Ingestion failed!" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "❌ Failed to start ingestion: $_" -ForegroundColor Red
    exit 1
}

# Update Lambda Environment
Write-Host "🔧 Updating Lambda environment..." -ForegroundColor Green

try {
    aws lambda update-function-configuration --function-name text-to-sql-agent-demo --environment "Variables={BEDROCK_KNOWLEDGE_BASE_ID=$kbId,GLUE_DATABASE=text_to_sql_demo,BEDROCK_MODEL_ID=amazon.titan-text-express-v1,ATHENA_OUTPUT_LOCATION=s3://text-to-sql-athena-results/}"
    Write-Host "✅ Lambda environment updated!" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Warning: Failed to update Lambda environment: $_" -ForegroundColor Yellow
}

Write-Host @"

🎉 SUCCESS! Knowledge Base setup complete:

📋 Details:
- Knowledge Base ID: $kbId
- Data Source ID: $dsId
- Lambda Function: Updated with new KB ID

🧪 Test Query:
Now you can test: "Show me top 5 customers by revenue"

Expected SQL:
SELECT c.name, c.email, c.city,
       SUM(o.total_amount) as total_revenue
FROM text_to_sql_demo.customers c
JOIN text_to_sql_demo.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email, c.city
ORDER BY total_revenue DESC
LIMIT 5;
"@ -ForegroundColor Green