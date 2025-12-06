# 🔍 Text-to-SQL AI Agent

An intelligent AI agent that converts natural language questions into SQL queries and executes them on AWS Athena, powered by Amazon Bedrock.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![AWS](https://img.shields.io/badge/AWS-Bedrock%20%7C%20Athena%20%7C%20Glue-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### Core Capabilities
- 🤖 **AI-Powered SQL Generation** - Uses Amazon Bedrock (Claude/Titan) to convert natural language to SQL
- 🗄️ **AWS Athena Integration** - Query your S3 data lake directly
- 📊 **Glue Catalog Support** - Automatic schema discovery from AWS Glue
- 🌐 **Web UI** - Beautiful Streamlit interface for interactive queries

### Advanced Features
- ✅ **Query Validation** - Blocks dangerous SQL operations and detects injection attempts
- ⚡ **Result Caching** - 10-100x faster repeated queries with intelligent caching
- 💡 **Query Explanations** - AI-generated explanations of SQL queries
- 💬 **Conversation History** - Context-aware follow-up questions
- 📈 **Data Visualization** - Auto-generated charts and graphs

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- AWS Account with:
  - Bedrock access (Claude or Titan models)
  - Athena access
  - Glue Catalog database
  - S3 bucket for Athena results

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/text-to-sql-agent.git
cd text-to-sql-agent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure AWS credentials**
```bash
aws configure
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your AWS settings
```

5. **Create sample data (optional)**
```bash
python setup_glue_sample.py
```

### Usage

#### Web UI (Recommended)
```bash
streamlit run web_ui.py
```

#### Python API
```python
from src.agent import TextToSQLAgent

agent = TextToSQLAgent()

# Generate and execute SQL
result = agent.query(
    "Show me all customers from Texas",
    execute=True,
    explain=True
)

print(f"SQL: {result['sql_query']}")
print(f"Results: {result['results']}")
```

#### Command Line
```bash
python example_enhanced.py
```

## 📖 Documentation

- [Getting Started Guide](GETTING_STARTED_ENHANCED.md)
- [Enhanced Features](ENHANCED_FEATURES.md)
- [Sample Data Guide](SAMPLE_DATA_GUIDE.md)
- [IAM Permissions](IAM_PERMISSIONS.md)
- [Windows Setup](WINDOWS_SETUP.md)

## 🎯 Example Queries

Try these natural language questions:

```
"Show me all customers from Texas"
"What are the top 5 products by price?"
"Count total orders by status"
"List all orders with total amount over $500"
"Show me customers who ordered Electronics"
"Calculate total revenue by category"
```

## 🏗️ Architecture

```
┌─────────────────┐
│   Web UI        │
│  (Streamlit)    │
└────────┬────────┘
         │
┌────────▼────────┐
│  Text-to-SQL    │
│     Agent       │
└────┬───┬───┬────┘
     │   │   │
     │   │   └──────────┐
     │   │              │
┌────▼───▼────┐  ┌──────▼──────┐
│   Amazon    │  │   AWS       │
│   Bedrock   │  │   Athena    │
│ (Claude/    │  │             │
│  Titan)     │  │             │
└─────────────┘  └──────┬──────┘
                        │
                 ┌──────▼──────┐
                 │  AWS Glue   │
                 │  Catalog    │
                 └──────┬──────┘
                        │
                 ┌──────▼──────┐
                 │     S3      │
                 │  Data Lake  │
                 └─────────────┘
```

## 🔒 Security Features

- ✅ SQL injection detection
- ✅ Dangerous operation blocking (DROP, DELETE, etc.)
- ✅ Query sanitization
- ✅ Read-only enforcement
- ✅ Input validation

## ⚡ Performance

- **Query Validation**: < 1ms overhead
- **Cache Hits**: 10-100x faster than Athena
- **Explanations**: +2-3s per query
- **Conversation Context**: < 10ms overhead

## 📊 Project Structure

```
text-to-sql-agent/
├── src/
│   ├── agent.py              # Main agent logic
│   ├── database.py           # Athena integration
│   ├── schema.py             # Glue Catalog integration
│   ├── query_validator.py   # SQL validation
│   ├── query_cache.py        # Result caching
│   └── conversation.py       # History management
├── lambda/
│   └── handler.py            # AWS Lambda handler
├── config/
│   └── cloudformation-template.yaml
├── web_ui.py                 # Streamlit web interface
├── example_enhanced.py       # Usage examples
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🛠️ Configuration

### Environment Variables

```env
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.titan-text-express-v1
GLUE_DATABASE=your_database
ATHENA_OUTPUT_LOCATION=s3://your-bucket/athena-results/
ATHENA_WORKGROUP=primary
```

### Supported Models

- Amazon Titan Text Express
- Claude 3 Haiku
- Claude 3 Sonnet
- Claude 3.5 Sonnet
- Meta Llama 3

## 🚢 Deployment

### AWS Lambda

```bash
sam build
sam deploy --guided
```

### Docker

```bash
docker build -t text-to-sql-agent .
docker run -p 8501:8501 text-to-sql-agent
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Amazon Bedrock for AI capabilities
- AWS Athena for query execution
- Streamlit for the web interface
- The open-source community

## 📧 Contact

For questions or support, please open an issue on GitHub.

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Built with ❤️ using AWS Bedrock, Athena, and Glue**
