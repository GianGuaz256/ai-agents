"""
Configuration file for the Enhanced Daily News Agent System
"""

import os
from typing import List, Dict

# --- API Configuration ---
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY")

# --- Model Configuration ---
DEFAULT_MODEL = "gpt-4o-mini"  # Using gpt-4o-mini as requested
TEMPERATURE = 0.7
MAX_TOKENS = 4000

# --- Research Configuration ---
MAX_ARTICLES_PER_TOPIC = 5
MAX_SEARCH_QUERIES_PER_TOPIC = 2  # Limited for efficiency
MAX_ARTICLES_TO_SCRAPE = 15
MAX_ARTICLES_TO_ANALYZE = 10
TOP_ARTICLES_FOR_SUMMARY = 15

# --- Topic Presets ---
TOPIC_PRESETS = {
    "bitcoin": [
        "Bitcoin news",
        "Lightning network news",
        "RGB protocol news",
        "Bitcoin adoption",
    ],
    
    "tech_ai": [
        "Artificial Intelligence AI developments",
        "Machine learning breakthroughs",
        "Technology startups funding",
        "OpenAI ChatGPT updates", 
        "Google Research news",
        "Anthropic Research news",
        "AI models and LLMs releases"
    ],
    
    "politics_economy": [
        "US Politics elections",
        "International relations",
        "Economic policy decisions",
        "Federal Reserve interest rates",
        "Global economic indicators"
    ],
    
    "business_markets": [
        "Stock market movements",
        "Corporate earnings reports",
        "Merger acquisition deals",
        "Venture capital investments",
        "Economic indicators GDP"
    ],
    
    "science_health": [
        "Medical research breakthroughs",
        "Climate change developments",
        "Space exploration NASA",
        "Scientific discoveries",
        "Public health updates"
    ],
    
    "default": [
        "Bitcoin cryptocurrency",
        "Artificial Intelligence AI",
        "International news",
        "Financial markets trading"
    ]
}

# --- Source Preferences ---
PREFERRED_SOURCES = [
    "bitcoinmagazine.com",
    "ledgerinsights.com",
    "theblock.co",
    "reuters.com",
    "bloomberg.com", 
    "wsj.com",
    "ft.com",
    "techcrunch.com",
    "coindesk.com",
    "cnn.com",
    "bbc.com",
    "apnews.com",
    "theverge.com",
    "finance.yahoo.com",
    "ycombinator.com/library"
]

# --- Content Filtering ---
EXCLUDE_KEYWORDS = [
    "advertisement",
    "sponsored",
    "casino",
    "gambling",
    "adult content",
    "clickbait"
]

# --- Summary Configuration ---
SUMMARY_LENGTH_TARGET = 1000  # Target word count for summary
READING_TIME_TARGET = 10  # Target reading time in minutes
INCLUDE_LINKS = True
INCLUDE_TIMESTAMPS = True

# --- Delivery Configuration ---
TELEGRAM_MESSAGE_LIMIT = 4096  # Telegram's message character limit
SPLIT_LONG_MESSAGES = True
ADD_EMOJIS = True

# --- Tool Configuration ---
TOOLS_CONFIG = {
    "duckduckgo": {
        "enabled": True,
        "max_results": 5,
        "region": "us-en"
    },
    "firecrawl": {
        "enabled": True,
        "timeout": 30,
        "extract_main_content": True
    }
}

# --- Error Handling ---
RETRY_ATTEMPTS = 2
GRACEFUL_DEGRADATION = True  # Continue processing even if some steps fail

def get_topics_by_preset(preset_name: str) -> List[str]:
    """Get topics by preset name."""
    return TOPIC_PRESETS.get(preset_name, TOPIC_PRESETS["default"])

def get_all_presets() -> Dict[str, List[str]]:
    """Get all available topic presets."""
    return TOPIC_PRESETS

def validate_config() -> bool:
    """Validate that required configuration is present."""
    required_vars = [OPENAI_API_KEY]
    missing = [var for var in required_vars if not var]
    
    if missing:
        print(f"⚠️ Missing required configuration: {missing}")
        return False
    
    # Check optional but recommended vars
    optional_vars = {
        "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
        "TELEGRAM_CHAT_ID": TELEGRAM_CHAT_ID,
        "FIRECRAWL_API_KEY": FIRECRAWL_API_KEY
    }
    
    for var_name, var_value in optional_vars.items():
        if not var_value:
            print(f"⚠️ Optional configuration missing: {var_name}")
    
    return True

def get_model_config() -> Dict:
    """Get model configuration."""
    return {
        "model": DEFAULT_MODEL,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS
    }

def get_research_limits() -> Dict:
    """Get research processing limits."""
    return {
        "max_articles_per_topic": MAX_ARTICLES_PER_TOPIC,
        "max_search_queries_per_topic": MAX_SEARCH_QUERIES_PER_TOPIC,
        "max_articles_to_scrape": MAX_ARTICLES_TO_SCRAPE,
        "max_articles_to_analyze": MAX_ARTICLES_TO_ANALYZE,
        "top_articles_for_summary": TOP_ARTICLES_FOR_SUMMARY
    } 