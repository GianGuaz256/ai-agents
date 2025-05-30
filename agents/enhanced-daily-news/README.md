# Enhanced Daily News Agent System

An intelligent news research and summarization system built with the Agno framework, using GPT-4o-mini, DuckDuckGo search, and Firecrawl for comprehensive daily news summaries with Telegram delivery.

## 🌟 Features

- **Multi-Agent Architecture**: 5 specialized agents working together
- **Customizable Topics**: Preset topic collections or custom topics
- **Web Research**: Real-time news search using DuckDuckGo
- **Content Scraping**: Full article content extraction with Firecrawl
- **Smart Summarization**: AI-powered topic-specific summaries
- **Telegram Integration**: Direct delivery via official Telegram Bot SDK with markdown formatting
- **Error Resilience**: Graceful degradation when services are unavailable

## 🏗️ Architecture

### Agent Team Structure

1. **Research Coordinator** - Plans search strategy for each topic
2. **Web Research Agent** - Executes DuckDuckGo searches
3. **Content Scraper Agent** - Extracts full article content with Firecrawl
4. **Topic Summary Writer Agent** - Creates topic-specific summaries with markdown formatting
5. **Final Assembly Agent** - Combines all summaries into final format
6. **Financial Data Agent** - Retrieves real-time market data (BTC, Gold, EUR/CHF)
7. **TLDR Generator Agent** - Creates concise overview of all topics

### Telegram Integration

- **Official SDK**: Uses `python-telegram-bot` library instead of agent-based delivery
- **MarkdownV2 Support**: Proper formatting with bold text, links, and emojis
- **Message Splitting**: Automatically handles long messages (>4000 chars)
- **Error Handling**: Robust delivery with fallback mechanisms

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** with virtual environment
2. **Required API Keys**:
   - `OPENAI_API_KEY` (required)
   - `FIRECRAWL_API_KEY` (optional, for better content extraction)
   - `TELEGRAM_BOT_TOKEN` & `TELEGRAM_CHAT_ID` (optional, for delivery)

### Installation

1. **Navigate to the agent directory**:
   ```bash
   cd agents/enhanced-daily-news
   ```

2. **Install dependencies**:
   ```bash
   pip install -r ../../requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   export FIRECRAWL_API_KEY="your-firecrawl-api-key"  # Optional
   export TELEGRAM_BOT_TOKEN="your-telegram-bot-token"  # Optional
   export TELEGRAM_CHAT_ID="your-telegram-chat-id"  # Optional
   ```

4. **Test Telegram integration** (optional):
   ```bash
   python test_telegram.py
   ```

5. **Run the system**:
   ```bash
   python run_news.py
   ```

## 📋 Usage Examples

### Basic Usage

```bash
# Use default topics (Bitcoin, AI, Politics, Markets)
python run_news.py

# Use a preset topic collection
python run_news.py --preset crypto_finance

# Use custom topics
python run_news.py --topics "Bitcoin" "Artificial Intelligence" "Climate Change"

# Limit articles per topic
python run_news.py --preset tech_ai --max-articles 3

# Quiet mode (less verbose output)
python run_news.py --preset business_markets --quiet
```

### Direct Python Usage

```python
from agent import run_daily_news_research

# Basic usage with default topics
summary = run_daily_news_research()

# Custom topics with article limits
custom_topics = ["Bitcoin ETF", "AI regulation", "Federal Reserve"]
summary = run_daily_news_research(topics=custom_topics, max_articles_per_topic=3)
```

### Available Presets

```bash
# List all available topic presets
python run_news.py --list-presets
```

**Available Presets:**
- `crypto_finance` - Bitcoin, Ethereum, DeFi, Crypto regulation, Financial markets
- `tech_ai` - AI developments, ML breakthroughs, Tech startups, Big Tech news
- `politics_economy` - US Politics, International relations, Economic policy
- `business_markets` - Stock markets, Corporate earnings, M&A, VC investments
- `science_health` - Medical research, Climate change, Space exploration
- `default` - Balanced mix of Bitcoin, AI, Politics, Markets

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | OpenAI API key for GPT-4o-mini |
| `FIRECRAWL_API_KEY` | ⚠️ Optional | Firecrawl API for better content extraction |
| `TELEGRAM_BOT_TOKEN` | ⚠️ Optional | Telegram bot token for delivery |
| `TELEGRAM_CHAT_ID` | ⚠️ Optional | Telegram chat ID for delivery |

### Telegram Setup

1. **Create a Telegram Bot**:
   - Message @BotFather on Telegram
   - Send `/newbot` and follow instructions
   - Save the bot token

2. **Get Chat ID**:
   - Start a chat with your bot
   - Send a message to the bot
   - Visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
   - Find your chat ID in the response

3. **Set Environment Variables**:
   ```bash
   export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
   export TELEGRAM_CHAT_ID="987654321"
   ```

4. **Test Integration**:
   ```bash
   python test_telegram.py
   ```

### Customization

Edit `config.py` to customize:
- **Topic Presets**: Add your own topic collections
- **Processing Limits**: Adjust article limits and timeouts
- **Model Settings**: Change temperature, max tokens
- **Source Preferences**: Prioritize specific news sources

## 📊 Output Format

The system generates summaries with MarkdownV2 formatting for Telegram:

### Summary Structure

```
*News Agent - [Date]*

*BTC price:* $XX,XXX
*GOLD price:* $X,XXX  
*EUR/CHF:* X.XXXX

*TLDR:* Brief overview of key developments across all topics.

*₿ Bitcoin Update* 🟠
• Key cryptocurrency developments
• Market analysis with *bold* emphasis
• Relevant links: [Source Name](url)

*AI Update* 🤖
• AI breakthroughs and industry news
• Policy and regulatory updates
• Expert opinions and analysis

*Politics Update* ⏳
• Political developments and policy changes
• Election updates and analysis
• International relations

*Finance Update* 💰
• Market movements and analysis
• Economic indicators and trends
• Corporate earnings and M&A
```

### Features

- **Markdown Formatting**: Bold headers, emphasized text, clickable links
- **Emojis**: Topic-specific emojis for visual appeal
- **Real-time Data**: Current BTC, Gold, and EUR/CHF prices
- **Automatic Escaping**: Proper MarkdownV2 character escaping
- **Smart Splitting**: Long messages automatically split across multiple Telegram messages

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors**:
   ```bash
   # Make sure you're in the correct directory
   cd agents/enhanced-daily-news
   python run_news.py
   ```

2. **API Key Issues**:
   ```bash
   # Verify environment variables
   echo $OPENAI_API_KEY
   echo $TELEGRAM_BOT_TOKEN
   ```

3. **Telegram Delivery Issues**:
   ```bash
   # Test Telegram integration
   python test_telegram.py
   
   # Check bot token and chat ID
   echo $TELEGRAM_BOT_TOKEN
   echo $TELEGRAM_CHAT_ID
   ```

4. **Markdown Formatting Issues**:
   - The system automatically escapes MarkdownV2 special characters
   - Test with simple messages first using `test_telegram.py`

5. **No Articles Found**:
   - Check internet connection
   - Try different topics or presets
   - Verify DuckDuckGo is accessible

6. **Firecrawl Errors**:
   - System will fallback to basic content extraction
   - Set `FIRECRAWL_API_KEY` for better results

### Error Handling

The system includes robust error handling:
- **Graceful Degradation**: Continues processing even if some steps fail
- **Fallback Mechanisms**: Uses alternative methods when primary tools fail
- **Detailed Logging**: Clear status updates and error messages
- **Telegram Fallbacks**: Manual assembly if agent-based assembly fails

## 🎯 Performance Tips

1. **Optimize Topic Selection**: Use specific, focused topics for better results
2. **Limit Article Count**: Use `--max-articles 3-5` for faster processing
3. **Use Presets**: Predefined presets are optimized for good coverage
4. **Quiet Mode**: Use `--quiet` for automated/scheduled runs
5. **Test Telegram**: Use `test_telegram.py` to verify delivery before full runs

## 🔄 Automation

### Scheduled Runs

Set up daily automated news summaries:

```bash
# Add to crontab for daily 8 AM execution
0 8 * * * cd /path/to/agents/enhanced-daily-news && python run_news.py --preset crypto_finance --quiet
```

### Integration Examples

```python
# Custom integration example
from agent import run_daily_news_research

def daily_briefing():
    topics = ["AI regulation", "Bitcoin ETF", "Fed policy"]
    summary = run_daily_news_research(topics=topics, max_articles_per_topic=3)
    
    # Custom processing
    if summary and "Critical error" not in summary:
        # Send to custom webhook, email, etc.
        send_to_slack(summary)
        save_to_database(summary)
    
    return summary
```

### Webhook Integration

The system can be integrated into:
- **Slack/Discord bots** (via webhook modifications)
- **Email newsletters** (save to file and email)
- **RSS feeds** (convert output to RSS format)
- **Mobile apps** (via API wrapper)
- **Custom dashboards** (extract and format data)

## 📈 Monitoring

Track system performance:
- **Processing Time**: Monitor execution duration per topic
- **Article Quality**: Review relevance and content extraction success
- **Source Diversity**: Check source distribution across topics
- **Error Rates**: Monitor failed requests and fallback usage
- **Telegram Delivery**: Track successful message delivery

## 🧪 Testing

### Available Tests

1. **Telegram Integration Test**:
   ```bash
   python test_telegram.py
   ```

2. **Example Usage**:
   ```bash
   python example.py
   ```

### Test Coverage

- ✅ Telegram Bot SDK integration with MarkdownV2
- ✅ Message formatting and character escaping
- ✅ Long message splitting functionality
- ✅ Error handling and fallback mechanisms
- ✅ Programmatic usage examples

## 🤝 Contributing

To extend the system:
1. **Add New Tools**: Integrate additional Agno tools
2. **Custom Agents**: Create specialized agents for specific domains
3. **Output Formats**: Add new delivery methods (Email, Slack, etc.)
4. **Topic Presets**: Create domain-specific topic collections
5. **Enhanced Formatting**: Improve Telegram message formatting

## 📚 Dependencies

Key dependencies include:
- `agno>=0.1.0` - Agent framework
- `python-telegram-bot>=21.0.0` - Official Telegram Bot SDK
- `openai>=1.0.0` - OpenAI API client
- `firecrawl>=0.1.0` - Web scraping
- `yfinance>=0.2.28` - Financial data
- `python-dotenv>=1.0.0` - Environment variables

## 📄 License

This project is part of the personal-agent-team repository and follows the same licensing terms.

---

**Built with ❤️ using the Agno framework and official Telegram Bot SDK** 