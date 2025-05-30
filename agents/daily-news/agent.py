from agno.agent import Agent
from agno.team import Team
from agno.tools.hackernews import HackerNewsTools
from agno.tools.firecrawl import FirecrawlTools
from agno.models.anthropic import Claude
from agno.models.openai import OpenAIChat
from agno.tools.telegram import TelegramTools
import dotenv
import os
import json
import re

dotenv.load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# --- Configuration for Scraper ---
# Define target URLs here for scalability
TARGET_URLS_TO_SCRAPE = [
    "https://bitcoinmagazine.com/", # Add more URLs later if needed
    "https://www.ledgerinsights.com/",
]
ARTICLES_PER_URL = 5 # Changed from 3, now max crawl pages per URL
urls_string = ', '.join(TARGET_URLS_TO_SCRAPE) # Pre-format the URL string
# --------------------------------

scraper = Agent(
    name="Daily Scraper Agent",
    model=OpenAIChat("gpt-4o"), # Use a more capable model for the complex task
    description="You are a web crawler assistant who identifies, scrapes, and summarizes news articles from given base URLs.", # Updated description
    instructions=[
        f"Your goal is to find and summarize recent news articles from the following base website URLs: {urls_string}",
        f"Follow these steps precisely for EACH base URL:",
        f"1. **Crawl:** Use the crawl tool on the base URL, ensuring you pass the parameter `max_pages={ARTICLES_PER_URL}` in the tool call. This will return a list of found URLs.",
        f"2. **Filter:** Analyze the list of crawled URLs. Identify and keep ONLY the URLs that appear to be actual, distinct news articles (e.g., based on paths like '/news/', '/articles/', dates, common news URL patterns). Discard URLs pointing to homepages, category pages, 'about', 'contact', etc.",
        f"3. **Scrape Filtered:** For EACH of the filtered news article URLs, use the scrape tool to get its full content.",
        f"4. **Summarize & Structure:** For EACH scraped article, extract its title and generate a concise (1-2 sentence) summary based on the scraped content.",
        f"5. **Compile JSON:** Collect the title, original URL, and summary for ALL processed articles from ALL base URLs into a single JSON list.",
        f"6. Each object in the JSON list must have the format:",
        "```json",
        "{",
        "    \"title\": \"Extracted article title\",",
        "    \"url\": \"Direct URL to the article\",",
        "    \"summary\": \"Generated brief summary from scraped content\"",
        "}",
        "```",
        "IMPORTANT: Ensure the final result is ONLY the raw JSON list string itself, starting with '[' and ending with ']'. Do not include any other text, explanations, or markdown formatting like ```json before or after the list."
    ],
    tools=[FirecrawlTools(crawl=False, scrape=True)],
    show_tool_calls=True,
    markdown=True,
)

hackernews = Agent(
    name="Daily Hackernews Agent",
    model=OpenAIChat("gpt-4o"),
    description="You are a skilled web scraper who extracts articles from a website",
    instructions=[
        "Your task is to read the top 3 news in the hackernews website",
        "Then I want you to create a JSON list response where each object has the following format: ",
        "```json",
        "[",
        "  {",
        "    \"title\": \"Title of the article\",",
        "    \"url\": \"URL of the article\",",
        "    \"summary\": \"Summary of the article\"",
        "  }",
        "]",
        "```",
        "IMPORTANT: Your final response MUST be ONLY the raw JSON list string itself, starting with '[' and ending with ']'. Do NOT include any other text, explanations, or markdown formatting like ```json before or after the list."
    ],
    tools=[HackerNewsTools()],
    markdown=True,
)

writer = Agent(
    name="Daily Writer Agent",
    model=OpenAIChat("gpt-4o"),
    description="You are a skilled writer who formats news summaries for Telegram",
    instructions=[
        "You will receive a JSON string representing a list of news articles (from various sources). Each object has 'title', 'url', and 'summary' keys.",
        "Your task is to format a Telegram message presenting EACH news item clearly and informatively, resembling a news bulletin.",
        "Do NOT write a conversational summary. Instead, format the message as follows:",
        "1. Start the message with a suitable title like '📰 Daily News Update' or similar.",
        "2. For EACH article in the JSON list, create an entry:",
        "   - Start with a relevant emoji (e.g., 📰, 💡, 🔗, ₿, 🌐).",
        "   - Add the article title in ALL UPPERCASE letters.",
        "   - On the next line, write a concise (1-2 sentence) summary derived from the provided 'summary'.",
        "   - On the next line, include the full 'url'.",
        "   - Add a blank line between each news item entry.",
        "Example entry format:",
        "📰 EXAMPLE ARTICLE TITLE",
        "\n",
        "This is a brief summary of the article content.",
        "https://example.com/article",
        "\n",
        "Ensure the final output is a single string formatted strictly for Telegram. Do not use any bolding or other special formatting for the title besides making it uppercase."
    ],
    tools=[TelegramTools(chat_id=TELEGRAM_CHAT_ID, token=TELEGRAM_BOT_TOKEN)],
)

# Execute agents sequentially
print("Running Scraper Agent...")
scraper_result = scraper.run("Start your daily news scraping task.")
print("Scraper Result:", scraper_result)

print("\nRunning HackerNews Agent...")
hackernews_result = hackernews.run("Get the top Hacker News stories.")
print("HackerNews Result:", hackernews_result)

# Combine results - Assuming results are JSON strings representing lists
combined_results = []

def extract_json(text):
    # Try to find a JSON block ```json ... ```
    match = re.search(r"```json\n(.*?)\n```", str(text), re.DOTALL)
    if match:
        return match.group(1).strip()
    # If no markdown block, assume the whole string might be JSON
    # (or try other potential extraction methods)
    return str(text).strip()

try:
    if scraper_result and scraper_result.content:
        print(f"Raw Scraper Result Content:\n---\n{scraper_result.content}\n---")
        scraper_json_str = extract_json(scraper_result.content)
        print(f"Extracted Scraper JSON String:\n---\n{scraper_json_str}\n---")
        if scraper_json_str:
            combined_results.extend(json.loads(scraper_json_str))
        else:
            print("Could not extract JSON from scraper result content.")
    else:
        print("Scraper result or its content was empty.")
except json.JSONDecodeError as e:
    print(f"Error decoding extracted scraper JSON: {e}")
    # Handle error or add placeholder data if needed

try:
    if hackernews_result and hackernews_result.content:
        print(f"Raw HackerNews Result Content:\n---\n{hackernews_result.content}\n---")
        hackernews_json_str = extract_json(hackernews_result.content)
        print(f"Extracted HackerNews JSON String:\n---\n{hackernews_json_str}\n---")
        if hackernews_json_str:
            combined_results.extend(json.loads(hackernews_json_str))
        else:
            print("Could not extract JSON from hackernews result content.")
    else:
        print("HackerNews result or its content was empty.")
except json.JSONDecodeError as e:
    print(f"Error decoding extracted hackernews JSON: {e}")
    # Handle error or add placeholder data if needed

# Convert combined list back to JSON string for the writer agent
combined_json_string = json.dumps(combined_results, indent=2)

print(f"\nCombined Results (JSON):\n{combined_json_string}")

# Run the writer agent with the combined results
if combined_results:
    print("\nRunning Writer Agent...")
    writer_response = writer.run(combined_json_string)
    print("Writer Response:", writer_response)
else:
    print("\nSkipping Writer Agent as there are no combined results.")