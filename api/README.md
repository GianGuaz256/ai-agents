# Personal Agent Team Production API

A production-ready FastAPI application for managing and executing AI agents at scale. Built following [Agno's best practices](https://docs.agno.com/workspaces/introduction) for scalable agentic systems.

## 🌟 Overview

This API provides a RESTful interface for:
- **Agent Management**: List, configure, and monitor available agents
- **Agent Execution**: Execute agents with custom parameters (sync/async)
- **Status Monitoring**: Track execution status and performance metrics
- **Health Checks**: Monitor system health and readiness
- **Specialized Services**: Enhanced endpoints for specific agent types

### Architecture

Following Agno's workspace patterns:
- **REST API (FastAPI)**: Core agent serving and management
- **PostgreSQL Database**: Session and execution storage
- **Redis**: Caching and background task queue
- **Celery**: Asynchronous task processing
- **Structured Logging**: Production monitoring and debugging
- **Docker**: Containerized deployment

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Required API Keys:
  - `OPENAI_API_KEY` (required)
  - `FIRECRAWL_API_KEY` (optional)
  - `TELEGRAM_BOT_TOKEN` & `TELEGRAM_CHAT_ID` (optional)

### Local Development Setup

1. **Clone and navigate to API directory**:
   ```bash
   cd api
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start services with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

4. **Verify deployment**:
   ```bash
   curl http://localhost:8000/health
   ```

5. **Access services**:
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Database: localhost:5432
   - Redis: localhost:6379
   - Celery Monitor: http://localhost:5555

### Production Deployment

#### Using Docker

```bash
# Build production image
docker build -t agent-api:latest .

# Run with production settings
docker run -d \
  --name agent-api \
  -p 8000:8000 \
  -e OPENAI_API_KEY="your-key" \
  -e DATABASE_URL="postgresql://..." \
  -e REDIS_URL="redis://..." \
  agent-api:latest
```

#### Using Docker Compose (Production)

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d
```

#### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/
```

## 📋 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and status |
| `/health` | GET | Health check with dependency status |
| `/health/readiness` | GET | Readiness probe for Kubernetes |
| `/health/liveness` | GET | Liveness probe for Kubernetes |

### Agent Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agents` | GET | List all available agents |
| `/agents/{agent_id}` | GET | Get specific agent information |
| `/agents/execute` | POST | Execute any agent with parameters |
| `/agents/executions/{execution_id}` | GET | Get execution status |
| `/agents/metrics` | GET | Get execution metrics |

### News Agent Specific

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agents/news/execute` | POST | Execute news agent with validation |
| `/agents/news/default-topics` | GET | Get default news topics |
| `/agents/news/validate-topics` | POST | Validate topic list |
| `/agents/news/executions/{id}/summary` | GET | Detailed execution summary |
| `/agents/news/metrics` | GET | News-specific metrics |

## 🔧 Configuration

### Environment Variables

#### Required
```bash
OPENAI_API_KEY=sk-...                    # OpenAI API key
```

#### Optional Agent Features
```bash
FIRECRAWL_API_KEY=fc-...                 # For enhanced content scraping
TELEGRAM_BOT_TOKEN=123456789:ABC...      # For Telegram delivery
TELEGRAM_CHAT_ID=987654321               # Target chat for messages
```

#### Database & Cache
```bash
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://localhost:6379/0
```

#### API Configuration
```bash
DEBUG=false                              # Enable debug mode
LOG_LEVEL=INFO                           # Logging level
HOST=0.0.0.0                            # Server host
PORT=8000                               # Server port
WORKERS=4                               # Number of worker processes
```

#### Security & Performance
```bash
SECRET_KEY=your-secret-key               # JWT secret
MAX_CONCURRENT_AGENTS=5                  # Concurrent execution limit
AGENT_TIMEOUT_SECONDS=300               # Agent execution timeout
RATE_LIMIT_PER_MINUTE=60                # API rate limiting
```

### Agent Configuration

Agents are configured in `core/config.py`:

```python
AVAILABLE_AGENTS = {
    "enhanced-daily-news": {
        "name": "Enhanced Daily News Agent",
        "description": "Comprehensive news research and summarization",
        "module_path": "agents.enhanced-daily-news.agent",
        "function_name": "run_daily_news_research",
        "timeout_seconds": 600,
        "requires_telegram": False,
        "requires_firecrawl": False
    }
    # Add new agents here
}
```

## 📖 Usage Examples

### Execute News Agent

```bash
# Execute with default topics
curl -X POST "http://localhost:8000/agents/news/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "max_articles_per_topic": 3
  }'

# Execute with custom topics
curl -X POST "http://localhost:8000/agents/news/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "topics": ["Bitcoin ETF", "AI regulation", "Federal Reserve"],
    "max_articles_per_topic": 5,
    "enable_telegram": true
  }'
```

### Check Execution Status

```bash
curl "http://localhost:8000/agents/executions/{execution_id}"
```

### Get Agent Metrics

```bash
curl "http://localhost:8000/agents/metrics"
curl "http://localhost:8000/agents/news/metrics"
```

### Python Client Example

```python
import httpx
import asyncio

async def execute_news_agent():
    async with httpx.AsyncClient() as client:
        # Execute agent
        response = await client.post(
            "http://localhost:8000/agents/news/execute",
            json={
                "topics": ["Bitcoin", "AI", "Politics"],
                "max_articles_per_topic": 3
            }
        )
        
        execution = response.json()
        execution_id = execution["execution_id"]
        
        # Poll for completion
        while True:
            status_response = await client.get(
                f"http://localhost:8000/agents/executions/{execution_id}"
            )
            status = status_response.json()
            
            if status["status"] in ["completed", "failed"]:
                print(f"Execution {status['status']}")
                if status["result"]:
                    print(status["result"])
                break
            
            await asyncio.sleep(5)

# Run the example
asyncio.run(execute_news_agent())
```

## 🔍 Monitoring & Observability

### Health Checks

The API provides comprehensive health checks:

```bash
# Basic health check
curl http://localhost:8000/health

# Kubernetes readiness probe
curl http://localhost:8000/health/readiness

# Kubernetes liveness probe
curl http://localhost:8000/health/liveness
```

### Metrics

Access execution metrics and performance data:

```bash
# Overall metrics
curl http://localhost:8000/agents/metrics

# News agent specific metrics
curl http://localhost:8000/agents/news/metrics
```

### Logging

The API uses structured logging with JSON output in production:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "info",
  "logger": "agent_execution",
  "message": "Agent execution completed",
  "agent_id": "enhanced-daily-news",
  "execution_id": "123e4567-e89b-12d3-a456-426614174000",
  "duration_seconds": 45.2
}
```

### Error Handling

All responses include proper error handling with structured error messages:

```json
{
  "error": "agent_not_found",
  "message": "Agent 'invalid-agent' not found",
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_123456"
}
```

## 🧪 Testing

### Manual Testing

```bash
# Test health endpoints
curl http://localhost:8000/health
curl http://localhost:8000/health/readiness

# Test agent listing
curl http://localhost:8000/agents

# Test news agent execution
curl -X POST http://localhost:8000/agents/news/execute \
  -H "Content-Type: application/json" \
  -d '{"max_articles_per_topic": 1}'
```

### Automated Testing

```bash
# Run tests in Docker
docker-compose exec api pytest

# Run with coverage
docker-compose exec api pytest --cov=api

# Load testing
docker-compose exec api locust -f tests/load_test.py
```

## 🔒 Security

### Production Security Checklist

- [ ] Set strong `SECRET_KEY`
- [ ] Configure proper CORS origins
- [ ] Set up trusted host middleware
- [ ] Use HTTPS in production
- [ ] Implement API key authentication
- [ ] Set up rate limiting
- [ ] Monitor and log security events
- [ ] Regular security updates

### API Key Management

Store sensitive keys securely:
- Use environment variables
- Avoid committing keys to version control
- Rotate keys regularly
- Monitor key usage

## 🚀 Scaling & Performance

### Horizontal Scaling

```bash
# Scale API instances
docker-compose up --scale api=3

# Use load balancer
nginx:
  upstream api {
    server api:8000;
    server api:8000;
    server api:8000;
  }
```

### Performance Optimization

1. **Database Optimization**:
   - Index frequently queried fields
   - Use connection pooling
   - Implement read replicas

2. **Caching Strategy**:
   - Redis for execution results
   - Agent configuration caching
   - API response caching

3. **Async Processing**:
   - Use Celery for long-running tasks
   - Implement result callbacks
   - Background job monitoring

## 🛠️ Development

### Adding New Agents

1. **Create agent module** in `agents/` directory
2. **Add agent configuration** in `core/config.py`:
   ```python
   "your-agent-id": {
       "name": "Your Agent Name",
       "description": "Agent description",
       "module_path": "agents.your-agent.agent",
       "function_name": "run_your_agent",
       "timeout_seconds": 300
   }
   ```
3. **Test agent integration**
4. **Update API documentation**

### Code Structure

```
api/
├── main.py                 # FastAPI application
├── core/                   # Configuration and utilities
├── models/                 # Pydantic models
├── routers/                # API endpoints
├── services/               # Business logic
├── tests/                  # Test suite
└── docker-compose.yml      # Development environment
```

### Contributing

1. Follow FastAPI and Pydantic best practices
2. Add comprehensive tests for new features
3. Update documentation
4. Follow structured logging patterns
5. Implement proper error handling

## 📚 References

- [Agno Workspaces Documentation](https://docs.agno.com/workspaces/introduction)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🐛 Troubleshooting

### Common Issues

1. **Agent Import Errors**:
   ```bash
   # Check Python path and module availability
   docker-compose exec api python -c "import agents.enhanced-daily-news.agent"
   ```

2. **Database Connection Issues**:
   ```bash
   # Check database connectivity
   docker-compose exec api python -c "from core.config import get_database_url; print(get_database_url())"
   ```

3. **OpenAI API Issues**:
   ```bash
   # Verify API key
   docker-compose exec api python -c "import os; print(os.environ.get('OPENAI_API_KEY', 'NOT_SET'))"
   ```

4. **Memory Issues**:
   ```bash
   # Monitor resource usage
   docker stats
   ```

### Debug Mode

Enable debug mode for detailed logging:

```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
docker-compose up
```

### Support

For issues and questions:
1. Check the troubleshooting section
2. Review application logs
3. Check health endpoints
4. Consult Agno documentation

---

**Built with ❤️ following Agno's production standards for scalable agentic systems.** 