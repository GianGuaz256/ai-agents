# 🤖 Personal Agent Team

A production-ready AI agent system built with FastAPI and the Agno framework, featuring multiple specialized agents for news research, content analysis, and automated reporting.

## 🌟 Features

- **Multi-Agent Architecture**: Specialized AI agents working together
- **Production-Ready FastAPI Server**: Built for scalability and monitoring  
- **Docker Support**: Easy deployment with Docker Compose
- **Comprehensive Logging**: Structured logging with request tracking
- **Health Monitoring**: Built-in health checks and metrics
- **Telegram Integration**: Automated notification delivery
- **Real-time News Research**: Multi-source news aggregation and analysis

## 🏗️ Architecture

### Available Agents

#### 1. Enhanced Daily News Agent 📰
**Location**: `agents/enhanced-daily-news/`

A sophisticated 7-agent system for comprehensive daily news research and summarization:

- **Research Coordinator**: Plans search strategy for each topic
- **Web Research Agent**: Executes DuckDuckGo searches for latest news
- **Content Scraper Agent**: Extracts full article content using Firecrawl
- **Topic Summary Writer**: Creates AI-powered topic-specific summaries
- **Final Assembly Agent**: Combines summaries into final formatted report
- **Financial Data Agent**: Retrieves real-time market data (BTC, Gold, EUR/CHF)
- **TLDR Generator**: Creates concise overview of all topics

**Features**:
- Customizable topic presets (crypto, tech, politics, business, etc.)
- Telegram delivery with MarkdownV2 formatting
- Financial market data integration
- Resilient error handling and graceful degradation

#### 2. Book Writer Agent 📚
**Location**: `agents/book_writer/`

Intelligent content creation and analysis agent for long-form writing projects.

### FastAPI Server

The production-ready API server provides:

- **Agent Management**: List, execute, and monitor agent performance
- **Async Execution**: Background task processing with status tracking
- **Request Tracing**: Unique request IDs and comprehensive logging
- **Health Checks**: System status and dependency monitoring
- **Error Handling**: Structured error responses with proper HTTP codes
- **CORS & Security**: Production-ready middleware configuration

**Key Endpoints**:
- `GET /agents/` - List all available agents
- `POST /agents/execute` - Execute any agent with parameters
- `GET /agents/executions/{id}` - Check execution status
- `POST /agents/news/execute` - Specialized news agent endpoint
- `GET /health` - System health check

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** with pip
2. **Docker & Docker Compose** (for production deployment)
3. **Required API Keys**:
   - `OPENAI_API_KEY` (required for all agents)
   - `FIRECRAWL_API_KEY` (optional, improves content extraction)
   - `TELEGRAM_BOT_TOKEN` & `TELEGRAM_CHAT_ID` (optional, for notifications)

### Local Development

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd personal-agent-team
   ```

2. **Set up virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   # Copy the example environment file
   cp api/.env.example .env
   
   # Edit .env with your API keys
   export OPENAI_API_KEY="your-openai-api-key"
   export FIRECRAWL_API_KEY="your-firecrawl-api-key"  # Optional
   export TELEGRAM_BOT_TOKEN="your-telegram-bot-token"  # Optional
   export TELEGRAM_CHAT_ID="your-telegram-chat-id"  # Optional
   ```

5. **Start the API server**:
   ```bash
   # Using the start script
   ./api/start_api.py

   # Or manually with uvicorn
   cd api && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the API**:
   - **API Documentation**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/health
   - **Agent List**: http://localhost:8000/agents/

### Production Deployment with Docker

1. **Prepare environment file**:
   ```bash
   # Create .env file with your production settings
   cat > .env << EOF
   OPENAI_API_KEY=your-openai-api-key
   FIRECRAWL_API_KEY=your-firecrawl-api-key
   TELEGRAM_BOT_TOKEN=your-telegram-bot-token
   TELEGRAM_CHAT_ID=your-telegram-chat-id
   DEBUG=false
   LOG_LEVEL=info
   ENVIRONMENT=production
   EOF
   ```

2. **Deploy with Docker Compose**:
   ```bash
   # Build and start services
   docker-compose up -d

   # View logs
   docker-compose logs -f api

   # Stop services
   docker-compose down
   ```

3. **Health Check**:
   ```bash
   curl http://localhost:8000/health
   ```

## 📋 Usage Examples

### API Usage

#### List Available Agents
```bash
curl -X GET "http://localhost:8000/agents/"
```

#### Execute Enhanced News Agent
```bash
curl -X POST "http://localhost:8000/agents/news/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "topics": ["Bitcoin", "Artificial Intelligence", "Climate Change"],
    "max_articles_per_topic": 5,
    "preset": "tech_ai",
    "async_execution": true
  }'
```

#### Check Execution Status
```bash
curl -X GET "http://localhost:8000/agents/executions/{execution_id}"
```

### Direct Agent Usage

#### Enhanced Daily News Agent
```bash
# Navigate to agent directory
cd agents/enhanced-daily-news

# Run with default topics
python run_news.py

# Use preset topic collection
python run_news.py --preset crypto_finance

# Custom topics with article limit
python run_news.py --topics "Bitcoin ETF" "AI regulation" --max-articles 3

# Quiet mode
python run_news.py --preset business_markets --quiet
```

**Available Presets**:
- `crypto_finance` - Bitcoin, Ethereum, DeFi, Crypto regulation
- `tech_ai` - AI developments, ML breakthroughs, Tech startups
- `politics_economy` - US Politics, International relations, Economic policy
- `business_markets` - Stock markets, Corporate earnings, M&A
- `science_health` - Medical research, Climate change, Space exploration

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | - | OpenAI API key for GPT models |
| `FIRECRAWL_API_KEY` | ⚠️ Optional | - | Firecrawl API for content extraction |
| `TELEGRAM_BOT_TOKEN` | ⚠️ Optional | - | Telegram bot token for notifications |
| `TELEGRAM_CHAT_ID` | ⚠️ Optional | - | Telegram chat ID for delivery |
| `DEBUG` | No | `false` | Enable debug mode and docs |
| `LOG_LEVEL` | No | `info` | Logging level (debug, info, warning, error) |
| `HOST` | No | `0.0.0.0` | API server host |
| `PORT` | No | `8000` | API server port |
| `MODEL_NAME` | No | `gpt-4` | Default OpenAI model |
| `TEMPERATURE` | No | `0.7` | Model temperature |
| `MAX_TOKENS` | No | `2000` | Maximum tokens per response |

### Telegram Setup

1. **Create Bot**: Message @BotFather on Telegram, send `/newbot`
2. **Get Chat ID**: Send message to bot, then visit `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. **Test**: Run `python agents/enhanced-daily-news/test_telegram.py`

## 📊 Monitoring & Logs

### Health Monitoring
- **Health Endpoint**: `/health` - System status and dependency checks
- **Metrics**: Request counts, response times, error rates
- **Docker Health Check**: Automatic container health monitoring

### Logging
- **Structured Logs**: JSON format with request tracing
- **Log Levels**: Configurable via `LOG_LEVEL` environment variable
- **Request IDs**: Unique identifiers for request tracking
- **Error Tracking**: Comprehensive error logging with context

### Volume Mounts (Docker)
- `./logs:/app/logs` - Application logs
- `./data:/app/data` - Persistent data storage

## 🛠️ Development

### Project Structure
```
personal-agent-team/
├── agents/                     # Individual agent implementations
│   ├── enhanced-daily-news/    # Multi-agent news research system
│   └── book_writer/           # Content creation agent
├── api/                       # FastAPI server
│   ├── core/                  # Core configuration and logging
│   ├── models/                # Request/response models
│   ├── routers/               # API endpoints
│   ├── services/              # Business logic services
│   └── main.py               # Application entry point
├── scripts/                   # Utility scripts
├── requirements.txt           # Python dependencies
├── Dockerfile                # Container definition
├── docker-compose.yml        # Production deployment
└── .gitignore                # Version control exclusions
```

### Adding New Agents

1. Create agent directory under `agents/`
2. Implement agent using Agno framework patterns
3. Add agent registration in `api/services/agent_manager.py`
4. Update API documentation and tests

### Running Tests
```bash
# Test individual agents
cd agents/enhanced-daily-news && python test_telegram.py

# Test API endpoints
curl http://localhost:8000/health
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-agent`)
3. Commit your changes (`git commit -m 'Add amazing new agent'`)
4. Push to the branch (`git push origin feature/amazing-agent`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Agno](https://github.com/agno-ai/agno) - Production AI Agent Framework
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [OpenAI](https://openai.com/) - Language model API
- [Firecrawl](https://firecrawl.dev/) - Web scraping and content extraction 