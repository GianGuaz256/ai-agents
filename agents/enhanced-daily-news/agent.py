from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.firecrawl import FirecrawlTools
from agno.tools.yfinance import YFinanceTools
from agno.models.openai import OpenAIChat
from textwrap import dedent
import dotenv
import os
import json
import re
from datetime import datetime, date
import asyncio
from telegram import Bot
from telegram.constants import ParseMode

dotenv.load_dotenv()

# --- Configuration ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Default topics - can be customized
DEFAULT_TOPICS = [
    "Bitcoin cryptocurrency",
    "Artificial Intelligence AI",
    "Politics elections",
    "Finance markets"
]

# --- Research Coordinator Agent ---
research_coordinator = Agent(
    name="Research Coordinator",
    model=OpenAIChat("gpt-4.1"),
    description="You are a research coordinator who plans and orchestrates news research across multiple topics.",
    instructions=[
        "You coordinate news research for multiple topics of interest.",
        "For each topic provided, you will:",
        "1. Generate 3-4 specific, targeted search queries that will find the most relevant and recent news",
        "2. Consider different angles: breaking news, analysis, market impact, expert opinions",
        "3. Focus on finding high-quality, authoritative sources",
        "4. Prioritize recent content (last 24-48 hours)",
        f"5. IMPORTANT: Always use the current date {date.today().strftime('%Y-%m-%d')} for context and research",
        "Return a JSON object with this structure:",
        "```json",
        "{",
        "  \"research_plan\": {",
        "    \"topic_name\": [",
        "      \"search query 1\",",
        "      \"search query 2\",",
        "      \"search query 3\"",
        "    ]",
        "  }",
        "}",
        "```",
        "IMPORTANT: Return ONLY the JSON object, no other text or formatting."
    ],
    show_tool_calls=True,
    markdown=True,
)

# --- Financial Data Agent ---
financial_data_agent = Agent(
    name="Financial Data Agent",
    model=OpenAIChat("gpt-4.1-mini"),
    description="You get real-time financial market data using YFinance tools.",
    instructions=[
        "You will retrieve current market prices for key financial instruments.",
        "Get the following data:",
        "1. Bitcoin price (BTC-USD)",
        "2. Gold price (GC=F or GOLD)",
        "3. EUR/CHF exchange rate (EURCHF=X)",
        "Use YFinance tools to get the most recent prices.",
        "Return the data in this JSON format:",
        "```json",
        "{",
        "  \"btc_price\": \"$XX,XXX\",",
        "  \"gold_price\": \"$X,XXX\",",
        "  \"eur_chf\": \"X.XXXX\"",
        "}",
        "```",
        "Format prices with appropriate currency symbols and commas for thousands.",
        "IMPORTANT: Return ONLY the JSON object, no other text."
    ],
    tools=[YFinanceTools()],
    show_tool_calls=True,
    markdown=True,
)

# --- Web Research Agent ---
web_researcher = Agent(
    name="Web Research Agent",
    model=OpenAIChat("gpt-4.1-mini"),
    description="You are a web research specialist who finds and extracts relevant news articles using DuckDuckGo search.",
    instructions=[
        "You will receive search queries and use DuckDuckGo search to find relevant news articles.",
        "For each search query:",
        "1. Use DuckDuckGo search to find recent, relevant articles",
        "2. Focus on authoritative news sources and recent content",
        "3. Extract key information: title, URL, snippet, source",
        "4. Filter out irrelevant or low-quality results",
        "5. Limit to top 3 results per query to avoid overwhelming the system",
        f"6. IMPORTANT: Focus on articles from {date.today().strftime('%Y-%m-%d')} or the last 24-48 hours",
        "Return results in this JSON format:",
        "```json",
        "[",
        "  {",
        "    \"title\": \"Article title\",",
        "    \"url\": \"Article URL\",",
        "    \"snippet\": \"Brief description or snippet\",",
        "    \"source\": \"Source website\",",
        "    \"topic\": \"Related topic\",",
        "    \"search_query\": \"Original search query\"",
        "  }",
        "]",
        "```",
        "IMPORTANT: Return ONLY the JSON array, no other text or formatting."
    ],
    tools=[DuckDuckGoTools()],
    show_tool_calls=True,
    markdown=True,
)

# --- Content Scraper Agent ---
content_scraper = Agent(
    name="Content Scraper Agent",
    model=OpenAIChat("gpt-4.1-mini"),
    description="You scrape full content from news article URLs using Firecrawl to get detailed information.",
    instructions=[
        "You will receive a list of news article URLs and scrape their full content.",
        "For each URL:",
        "1. Use Firecrawl to scrape the full article content",
        "2. Extract the main article text, avoiding ads and navigation",
        "3. Identify key information: headline, author, publication date, main content",
        "4. Handle errors gracefully if a URL cannot be scraped",
        "Return results in this JSON format:",
        "```json",
        "[",
        "  {",
        "    \"url\": \"Article URL\",",
        "    \"title\": \"Full article title\",",
        "    \"content\": \"Main article content (first 500 words)\",",
        "    \"author\": \"Author name if available\",",
        "    \"published_date\": \"Publication date if available\",",
        "    \"source\": \"Source website\",",
        "    \"scraped_successfully\": true",
        "  }",
        "]",
        "```",
        "IMPORTANT: Return ONLY the JSON array, no other text or formatting."
    ],
    tools=[FirecrawlTools()],
    show_tool_calls=True,
    markdown=True,
)

# --- Topic Summary Writer Agent ---
topic_summary_writer = Agent(
    name="Topic Summary Writer Agent",
    model=OpenAIChat("gpt-4.1-mini"),
    description="You are an expert news writer who creates topic-specific summaries optimized for Telegram.",
    instructions=[
        "You will receive analyzed news articles for a SINGLE topic and create a focused summary section.",
        "Create a summary section that:",
        "1. Focuses on ONE topic only (Bitcoin, AI, Politics, Finance, etc.)",
        "2. Is optimized for Telegram messaging with markdown formatting",
        "3. Uses Telegram MarkdownV2 formatting for emphasis and structure",
        "4. Keeps sections under 800 characters",
        "5. Uses specific emojis based on topic",
        f"6. Uses the current date {date.today().strftime('%B %d, %Y')} in context",
        "Structure your topic summary with these EXACT formats:",
        "- Bitcoin topics: '*₿ Bitcoin Update* 🟠'",
        "- AI topics: '*AI Update* 🤖'", 
        "- Politics topics: '*Politics Update* ⏳'",
        "- Finance topics: '*Finance Update* 💰'",
        "- Other topics: use appropriate emoji and '*Topic Update* emoji'",
        "Follow this structure:",
        "- Topic header with markdown bold title and designated emoji",
        "- 2-3 bullet points with key developments using • symbol",
        "- Use *bold* for emphasis on key terms and important information",
        "- Include relevant links formatted as [text](url) for Telegram",
        "- Keep it concise and engaging",
        "Format for Telegram MarkdownV2 compatibility:",
        "- Use *bold* for emphasis (single asterisks)",
        "- Use • for bullet points",
        "- Keep line breaks for readability",
        "- Format links as: [descriptive text](url) for Telegram",
        "- Links should be inline within sentences",
        "- Avoid using special characters: . ! # + - = | { } ( ) [ ] ~ ` > in regular text",
        "- The system will automatically escape necessary characters for MarkdownV2",
        "IMPORTANT: Return ONLY the formatted topic summary with proper markdown."
    ],
    show_tool_calls=True,
    markdown=True,
)

# --- TLDR Generator Agent ---
tldr_generator = Agent(
    name="TLDR Generator Agent",
    model=OpenAIChat("gpt-4.1-mini"),
    description="You create concise TLDR summaries from multiple news topics.",
    instructions=[
        "You will receive multiple topic summaries and create a brief TLDR section.",
        "Create a TLDR that:",
        "1. Summarizes the key themes across all topics in 1-2 sentences",
        "2. Focuses on the most important developments",
        "3. Is under 150 characters for quick reading",
        "4. Uses simple, clear language",
        "5. Captures the essence of the day's news",
        "Format requirements:",
        "- Write in present tense",
        "- No emojis in TLDR text",
        "- Keep it factual and concise",
        "- Focus on actionable or impactful information",
        "Example: 'Bitcoin surges past $70k on ETF optimism while AI companies announce major partnerships. Political tensions rise ahead of elections.'",
        "IMPORTANT: Return ONLY the TLDR text, no formatting or extra words."
    ],
    show_tool_calls=True,
    markdown=True,
)

# --- Final Assembly Agent ---
final_assembly_agent = Agent(
    name="Final Assembly Agent", 
    model=OpenAIChat("gpt-4.1"),
    description="You assemble topic summaries, market data, and TLDR into the final news format.",
    instructions=[
        "You will receive market data, TLDR summary, and topic sections to assemble.",
        "Create a complete summary using this EXACT format for Telegram markdown:",
        "",
        f"*News Agent - {date.today().strftime('%B %d, %Y')}*",
        "",
        "*BTC price:* [btc_price]",
        "*GOLD price:* [gold_price]", 
        "*EUR/CHF:* [eur_chf]",
        "",
        "*TLDR:* [tldr_text]",
        "",
        "[topic_sections]",
        "",
        "TELEGRAM MARKDOWNV2 FORMATTING RULES:",
        "1. Replace [btc_price], [gold_price], [eur_chf] with provided market data",
        "2. Replace [tldr_text] with the provided TLDR summary",
        "3. Replace [topic_sections] with all topic summaries in order",
        "4. Keep the exact structure and spacing shown above",
        "5. Use *bold* for labels and headers (single asterisks)",
        "6. Do not manually escape characters - the system handles MarkdownV2 escaping automatically",
        "7. Keep labels as markdown bold: '*BTC price:*' '*GOLD price:*' '*EUR/CHF:*'",
        "8. Keep title as markdown bold: '*News Agent - Date*' (no manual escaping needed)",
        "9. Keep TLDR label as markdown bold: '*TLDR:*'",
        "10. Links should be formatted as [text](url) for Telegram",
        "11. The system will automatically escape special MarkdownV2 characters",
        "IMPORTANT: Return ONLY the complete formatted message with proper markdown."
    ],
    show_tool_calls=True,
    markdown=True,
)

# --- Telegram Utility Functions ---
def escape_markdown_v2(text: str) -> str:
    """
    Escape special characters for Telegram MarkdownV2.
    
    According to Telegram docs, these characters must be escaped:
    '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!'
    
    Args:
        text (str): Text to escape
    
    Returns:
        str: Escaped text
    """
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    
    return text

def format_for_markdown_v2(text: str, preserve_markdown: bool = True) -> str:
    """
    Format text for MarkdownV2, preserving intentional markdown while escaping special chars.
    
    Args:
        text (str): Text to format
        preserve_markdown (bool): Whether to preserve *bold* and [links](url) formatting
    
    Returns:
        str: Formatted text
    """
    if not preserve_markdown:
        return escape_markdown_v2(text)
    
    # Temporarily replace intentional markdown with placeholders
    import re
    
    # Find and replace bold text (*text*)
    bold_pattern = r'\*([^*]+)\*'
    bold_matches = re.findall(bold_pattern, text)
    bold_placeholders = {}
    
    for i, match in enumerate(bold_matches):
        placeholder = f"BOLDPLACEHOLDER{i}BOLDPLACEHOLDER"
        bold_placeholders[placeholder] = f"*{escape_markdown_v2(match)}*"
        text = text.replace(f"*{match}*", placeholder, 1)
    
    # Find and replace links [text](url)
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    link_matches = re.findall(link_pattern, text)
    link_placeholders = {}
    
    for i, (link_text, url) in enumerate(link_matches):
        placeholder = f"LINKPLACEHOLDER{i}LINKPLACEHOLDER"
        link_placeholders[placeholder] = f"[{escape_markdown_v2(link_text)}]({escape_markdown_v2(url)})"
        text = text.replace(f"[{link_text}]({url})", placeholder, 1)
    
    # Escape remaining text
    text = escape_markdown_v2(text)
    
    # Restore placeholders (they should still be intact since we used special strings)
    for placeholder, replacement in bold_placeholders.items():
        text = text.replace(placeholder, replacement)
    
    for placeholder, replacement in link_placeholders.items():
        text = text.replace(placeholder, replacement)
    
    return text

# --- Telegram Delivery Function ---
async def send_telegram_message(message: str, bot_token: str, chat_id: str):
    """
    Send a message to Telegram using the official Bot SDK with markdown formatting.
    
    Args:
        message (str): The message to send
        bot_token (str): Telegram bot token
        chat_id (str): Telegram chat ID
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        bot = Bot(token=bot_token)
        
        # Format message for MarkdownV2
        formatted_message = format_for_markdown_v2(message)
        
        # Telegram has a 4096 character limit per message
        max_length = 4000  # Leave some buffer
        
        if len(formatted_message) <= max_length:
            # Send as single message
            await bot.send_message(
                chat_id=chat_id,
                text=formatted_message,
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=False
            )
            print("  ✅ Message sent successfully via Telegram")
            return True
        else:
            # Split message intelligently if too long
            print(f"  📝 Message too long ({len(formatted_message)} chars), splitting...")
            
            # Split by double newlines (between sections)
            sections = formatted_message.split('\n\n')
            current_message = ""
            message_count = 0
            
            for section in sections:
                if len(current_message + section + '\n\n') <= max_length:
                    current_message += section + '\n\n'
                else:
                    if current_message:
                        await bot.send_message(
                            chat_id=chat_id,
                            text=current_message.strip(),
                            parse_mode=ParseMode.MARKDOWN_V2,
                            disable_web_page_preview=False
                        )
                        message_count += 1
                        current_message = section + '\n\n'
                    else:
                        # Section itself is too long, send as is
                        await bot.send_message(
                            chat_id=chat_id,
                            text=section,
                            parse_mode=ParseMode.MARKDOWN_V2,
                            disable_web_page_preview=False
                        )
                        message_count += 1
            
            # Send remaining content
            if current_message.strip():
                await bot.send_message(
                    chat_id=chat_id,
                    text=current_message.strip(),
                    parse_mode=ParseMode.MARKDOWN_V2,
                    disable_web_page_preview=False
                )
                message_count += 1
            
            print(f"  ✅ Message split into {message_count} parts and sent successfully")
            return True
            
    except Exception as e:
        print(f"  ❌ Error sending Telegram message: {str(e)}")
        import traceback
        print(f"  📍 Telegram error traceback: {traceback.format_exc()}")
        return False

def send_telegram_message_sync(message: str, bot_token: str, chat_id: str):
    """
    Synchronous wrapper for the async Telegram function.
    
    Args:
        message (str): The message to send
        bot_token (str): Telegram bot token  
        chat_id (str): Telegram chat ID
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run the async function
        return loop.run_until_complete(
            send_telegram_message(message, bot_token, chat_id)
        )
    except Exception as e:
        print(f"  ❌ Error in sync wrapper: {str(e)}")
        return False

# --- Utility Functions ---
def extract_json_from_response(response_text):
    """Extract JSON from agent response, handling various formats."""
    if not response_text:
        print("        🔍 No response text provided for JSON extraction")
        return None
    
    # Convert response to string if it's not already
    text = str(response_text)
    print(f"        📝 Response text length: {len(text)} characters")
    print(f"        📝 Response preview: {text[:200]}...")
    
    # Try to find JSON in markdown code blocks
    json_match = re.search(r'```json\n(.*?)\n```', text, re.DOTALL)
    if json_match:
        try:
            print("        🎯 Found JSON in markdown code block")
            result = json.loads(json_match.group(1))
            print(f"        ✅ Successfully parsed JSON from markdown: {type(result)}")
            return result
        except json.JSONDecodeError as e:
            print(f"        ⚠️ Failed to parse JSON from markdown: {e}")
            pass
    
    # Try to find JSON without markdown
    json_match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
    if json_match:
        try:
            print("        🎯 Found JSON without markdown")
            result = json.loads(json_match.group(1))
            print(f"        ✅ Successfully parsed JSON without markdown: {type(result)}")
            return result
        except json.JSONDecodeError as e:
            print(f"        ⚠️ Failed to parse JSON without markdown: {e}")
            pass
    
    # Try parsing the entire response as JSON
    try:
        print("        🎯 Attempting to parse entire response as JSON")
        result = json.loads(text)
        print(f"        ✅ Successfully parsed entire response as JSON: {type(result)}")
        return result
    except json.JSONDecodeError as e:
        print(f"        ❌ Failed to parse entire response as JSON: {e}")
        pass
    
    print("        ❌ No valid JSON found in response")
    return None

def safe_get_content(response):
    """Safely extract content from agent response."""
    print(f"        🔍 Extracting content from response type: {type(response)}")
    if hasattr(response, 'content'):
        print(f"        ✅ Found content attribute, length: {len(str(response.content))}")
        return response.content
    content = str(response)
    print(f"        ✅ Using string conversion, length: {len(content)}")
    return content

def process_single_topic(topic, max_articles=3):
    """
    Process a single topic to avoid token limits.
    
    Args:
        topic (str): Single topic to research
        max_articles (int): Maximum articles to process for this topic
    
    Returns:
        str: Topic summary section formatted for Telegram
    """
    print(f"  🔎 Processing topic: {topic}")
    
    try:
        # Step 1: Generate search queries for this topic
        print(f"    📋 Step 1: Planning search strategy for {topic}...")
        planning_prompt = f"Plan research strategy for this single topic: {topic}. Generate 2-3 specific search queries focusing on today's date {date.today().strftime('%Y-%m-%d')}."
        
        print(f"    🤖 Calling research coordinator agent...")
        planning_response = research_coordinator.run(planning_prompt)
        print(f"    ✅ Research coordinator response received")
        
        print(f"    🔍 Extracting JSON from planning response...")
        research_plan = extract_json_from_response(safe_get_content(planning_response))
        print(f"    📊 Research plan extracted: {research_plan}")
        
        if not research_plan or 'research_plan' not in research_plan:
            print(f"    ⚠️ Using fallback queries for {topic}")
            queries = [f"latest {topic} news today", f"{topic} breaking news {date.today().strftime('%Y-%m-%d')}"]
        else:
            queries = list(research_plan.get('research_plan', {}).values())[0] if research_plan.get('research_plan') else [f"latest {topic} news today"]
            print(f"    📝 Generated queries: {queries}")
        
        # Step 2: Search for articles
        print(f"    🔍 Step 2: Searching for articles...")
        articles = []
        for i, query in enumerate(queries[:2], 1):  # Limit to 2 queries per topic
            print(f"      🔎 Query {i}/{min(len(queries), 2)}: {query}")
            try:
                search_prompt = f"Search for recent news about: {query}"
                print(f"      🤖 Calling web researcher agent...")
                search_response = web_researcher.run(search_prompt)
                print(f"      ✅ Web researcher response received")
                
                print(f"      🔍 Extracting JSON from search response...")
                search_results = extract_json_from_response(safe_get_content(search_response))
                print(f"      📊 Search results extracted: {len(search_results) if search_results else 0} results")
                
                if search_results and isinstance(search_results, list):
                    for j, article in enumerate(search_results[:2], 1):  # Top 2 per query
                        article['topic'] = topic
                        articles.append(article)
                        print(f"        📄 Added article {j}: {article.get('title', 'No title')[:50]}...")
                else:
                    print(f"      ⚠️ No valid search results for query: {query}")
                        
            except Exception as e:
                print(f"      ❌ Error searching for {query}: {str(e)}")
                import traceback
                print(f"      📍 Traceback: {traceback.format_exc()}")
                continue
        
        print(f"    📊 Total articles found: {len(articles)}")
        if not articles:
            print(f"    ❌ No articles found for {topic}")
            return f"_{topic}: No recent news available._\n"
        
        # Step 3: Scrape content for top articles
        print(f"    📄 Step 3: Scraping content for top articles...")
        scraped_articles = []
        if articles:
            top_articles = articles[:max_articles]
            urls_to_scrape = [article['url'] for article in top_articles]
            print(f"    📋 URLs to scrape: {len(urls_to_scrape)}")
            for i, url in enumerate(urls_to_scrape, 1):
                print(f"      🔗 URL {i}: {url[:50]}...")
            
            try:
                scraping_prompt = f"Scrape content from these URLs: {json.dumps(urls_to_scrape[:3])}"  # Limit to 3 URLs
                print(f"    🤖 Calling content scraper agent...")
                scraping_response = content_scraper.run(scraping_prompt)
                print(f"    ✅ Content scraper response received")
                
                print(f"    🔍 Extracting JSON from scraping response...")
                scraped_content = extract_json_from_response(safe_get_content(scraping_response))
                print(f"    📊 Scraped content extracted: {len(scraped_content) if scraped_content else 0} items")
                
                if scraped_content and isinstance(scraped_content, list):
                    # Merge data
                    print(f"    🔄 Merging scraped content with original articles...")
                    for original in top_articles:
                        for scraped in scraped_content:
                            if scraped.get('url') == original.get('url'):
                                merged = {**original, **scraped}
                                scraped_articles.append(merged)
                                print(f"      ✅ Merged article: {original.get('title', 'No title')[:30]}...")
                                break
                    
                if not scraped_articles:
                    print(f"    ⚠️ No scraped content merged, using original articles")
                    scraped_articles = top_articles[:3]
                    
            except Exception as e:
                print(f"    ❌ Error scraping for {topic}: {str(e)}")
                import traceback
                print(f"    📍 Traceback: {traceback.format_exc()}")
                scraped_articles = articles[:3]
        
        print(f"    📊 Final scraped articles: {len(scraped_articles)}")
        
        # Step 4: Generate topic summary
        print(f"    ✍️ Step 4: Generating topic summary...")
        if scraped_articles:
            # Limit the amount of data sent to avoid token limits
            limited_articles = []
            for article in scraped_articles:
                limited_article = {
                    'title': article.get('title', ''),
                    'url': article.get('url', ''),
                    'snippet': article.get('snippet', ''),
                    'source': article.get('source', ''),
                    'content': article.get('content', '')[:500] if article.get('content') else ''  # Limit content
                }
                limited_articles.append(limited_article)
            
            print(f"    📝 Preparing summary with {len(limited_articles)} articles...")
            summary_prompt = f"Create a Telegram-formatted summary section for {topic} using these articles: {json.dumps(limited_articles)}"
            print(f"    🤖 Calling topic summary writer agent...")
            summary_response = topic_summary_writer.run(summary_prompt)
            print(f"    ✅ Topic summary writer response received")
            
            topic_summary = safe_get_content(summary_response)
            print(f"    📄 Generated summary length: {len(topic_summary)} characters")
            print(f"    ✅ Generated summary for {topic}")
            return topic_summary
        else:
            print(f"    ⚠️ No articles available for summary generation")
            return f"_{topic}: No detailed information available._\n"
            
    except Exception as e:
        print(f"    ❌ Critical error processing {topic}: {str(e)}")
        import traceback
        print(f"    📍 Full traceback: {traceback.format_exc()}")
        return f"_{topic}: Processing error occurred._\n"

def run_daily_news_research(topics=None, max_articles_per_topic=3):
    """
    Run the complete daily news research process with sequential topic processing.
    
    Args:
        topics (list): List of topics to research. If None, uses DEFAULT_TOPICS.
        max_articles_per_topic (int): Maximum articles to research per topic.
    
    Returns:
        str: Final news summary
    """
    if topics is None:
        topics = DEFAULT_TOPICS
    
    current_date = date.today().strftime('%Y-%m-%d')
    print(f"🚀 Starting Enhanced Daily News Research")
    print(f"📋 Topics: {', '.join(topics)}")
    print(f"📅 Date: {current_date}")
    print(f"📄 Max articles per topic: {max_articles_per_topic}")
    print("=" * 60)
    
    try:
        # Process each topic individually to avoid token limits
        print("\n🔍 Processing topics individually...")
        topic_summaries = []
        
        for i, topic in enumerate(topics, 1):
            print(f"\n📍 Processing topic {i}/{len(topics)}: {topic}")
            start_time = datetime.now()
            
            try:
                topic_summary = process_single_topic(topic, max_articles_per_topic)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                print(f"  ⏱️ Topic processing completed in {duration:.1f} seconds")
                
                if topic_summary and topic_summary.strip():
                    topic_summaries.append(topic_summary)
                    print(f"  ✅ Topic {i} completed successfully")
                else:
                    print(f"  ⚠️ Topic {i} returned empty summary")
                    
            except Exception as e:
                print(f"  ❌ Error processing topic {i} ({topic}): {str(e)}")
                import traceback
                print(f"  📍 Traceback: {traceback.format_exc()}")
                continue
        
        print(f"\n📊 Final Results:")
        print(f"  📝 Processed {len(topics)} topics")
        print(f"  ✅ Generated {len(topic_summaries)} successful summaries")
        
        # Get financial market data
        print("\n💰 Getting financial market data...")
        try:
            print("  🤖 Calling financial data agent...")
            financial_response = financial_data_agent.run("Get current market prices for BTC, GOLD, and EUR/CHF")
            print("  ✅ Financial data agent response received")
            financial_data = extract_json_from_response(safe_get_content(financial_response))
            
            if not financial_data:
                financial_data = {
                    "btc_price": "N/A",
                    "gold_price": "N/A", 
                    "eur_chf": "N/A"
                }
                print("  ⚠️ Using fallback financial data")
            else:
                print(f"  📊 Market data retrieved successfully")
                
        except Exception as e:
            print(f"  ❌ Error getting financial data: {str(e)}")
            financial_data = {
                "btc_price": "N/A",
                "gold_price": "N/A",
                "eur_chf": "N/A"
            }
        
        # Generate TLDR
        print("\n📝 Generating TLDR summary...")
        if topic_summaries:
            try:
                combined_for_tldr = "\n".join(topic_summaries)
                print("  🤖 Calling TLDR generator agent...")
                tldr_response = tldr_generator.run(f"Create a TLDR from these topic summaries: {combined_for_tldr}")
                print("  ✅ TLDR generator response received")
                tldr_summary = safe_get_content(tldr_response).strip()
                print(f"  📄 TLDR generated: {len(tldr_summary)} characters")
            except Exception as e:
                print(f"  ❌ Error generating TLDR: {str(e)}")
                tldr_summary = "Key developments across crypto, AI, politics, and finance markets today."
        else:
            tldr_summary = "No major news developments today."
        
        # Assemble final summary
        print("\n✍️ Assembling final news summary...")
        if topic_summaries:
            print(f"  📄 Combining {len(topic_summaries)} topic summaries...")
            combined_summaries = "\n\n".join(topic_summaries)
            
            assembly_data = {
                "market_data": financial_data,
                "tldr": tldr_summary,
                "topic_sections": combined_summaries
            }
            
            assembly_prompt = f"""Assemble the final news summary using this data:
Market Data: {financial_data}
TLDR: {tldr_summary}
Topic Sections:
{combined_summaries}"""
            
            print(f"  🤖 Calling final assembly agent...")
            
            try:
                assembly_response = final_assembly_agent.run(assembly_prompt)
                print(f"  ✅ Final assembly agent response received")
                news_summary = safe_get_content(assembly_response)
                print(f"  📄 Final summary length: {len(news_summary)} characters")
            except Exception as e:
                print(f"  ❌ Error in final assembly: {str(e)}")
                # Fallback manual assembly
                news_summary = f"""*News Agent - {date.today().strftime('%B %d, %Y')}*

*BTC price:* {financial_data.get('btc_price', 'N/A')}
*GOLD price:* {financial_data.get('gold_price', 'N/A')}
*EUR/CHF:* {financial_data.get('eur_chf', 'N/A')}

*TLDR:* {tldr_summary}

{combined_summaries}"""
        else:
            print(f"  ⚠️ No topic summaries available, creating fallback summary")
            news_summary = f"""*News Agent - {date.today().strftime('%B %d, %Y')}*

*BTC price:* {financial_data.get('btc_price', 'N/A')}
*GOLD price:* {financial_data.get('gold_price', 'N/A')}
*EUR/CHF:* {financial_data.get('eur_chf', 'N/A')}

*TLDR:* No relevant news found for today's topics.

No news updates available today."""
        
        # Step 6: Delivery
        print("\n📱 Delivering news summary...")
        if TELEGRAM_CHAT_ID and TELEGRAM_BOT_TOKEN:
            try:
                print("  📤 Sending message via Telegram Bot SDK...")
                success = send_telegram_message_sync(news_summary, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
                if success:
                    print("  ✅ News summary delivered via Telegram with markdown formatting")
                else:
                    print("  ❌ Failed to deliver news summary via Telegram")
            except Exception as e:
                print(f"  ⚠️ Error delivering to Telegram: {str(e)}")
        else:
            print("  ⚠️ Telegram credentials not configured. Skipping delivery.")
        
        # Note: File saving is handled by the CLI script to avoid duplicates
        print("\n📝 News summary generation completed")
        
        # Display final summary
        print("\n" + "="*60)
        print("📰 ENHANCED DAILY NEWS SUMMARY")
        print("="*60)
        print(news_summary)
        print("="*60)
        
        return news_summary
        
    except Exception as e:
        error_msg = f"❌ Critical error in news research process: {str(e)}"
        print(error_msg)
        import traceback
        print(f"📍 Full system traceback: {traceback.format_exc()}")
        return error_msg

# --- Main Execution ---
if __name__ == "__main__":
    # Example usage with custom topics
    custom_topics = [
        "Bitcoin cryptocurrency blockchain",
        "Artificial Intelligence machine learning",
        "US Politics elections 2024",
        "Stock market financial markets"
    ]
    
    print("🌟 Enhanced Daily News Agent System")
    print("Using GPT-4o-mini with DuckDuckGo and Firecrawl")
    print(f"📅 Current Date: {date.today().strftime('%B %d, %Y')}")
    print("-" * 50)
    
    # Run the daily news research
    summary = run_daily_news_research(topics=custom_topics)
    
    print("\n🎉 Enhanced daily news research completed!") 