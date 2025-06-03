from agno.agent import Agent
from agno.tools.github import GithubTools
from agno.models.openai import OpenAIChat
from textwrap import dedent
import dotenv
import os
import json
import re
from datetime import datetime, date, timedelta
import asyncio
from telegram import Bot
from telegram.constants import ParseMode
import requests

dotenv.load_dotenv()

# Get GitHub token from environment
github_token = os.getenv("GITHUB_TOKEN")
if not github_token:
    raise ValueError("GITHUB_TOKEN environment variable is not set. Please set it in your .env file.")

# Set the token in the environment
os.environ["GITHUB_TOKEN"] = github_token

# --- Configuration ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Check if GitHub token is available
def get_github_tools():
    """Get GitHub tools if token is available, otherwise return None."""
    if github_token:
        try:
            # Set the GitHub token as environment variable for Agno
            os.environ['GITHUB_ACCESS_TOKEN'] = github_token
            return [GithubTools(access_token=github_token)]
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize GitHub tools: {e}")
            print(f"   Make sure your GitHub token has proper permissions")
            return []
    else:
        print("⚠️  Warning: GITHUB_TOKEN not set. GitHub API calls will be limited.")
        return []

def check_github_token():
    """Check if GitHub token is properly configured"""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        return False, "GITHUB_TOKEN environment variable not set"
    
    if len(token) != 40:
        return False, f"GitHub token has invalid length: {len(token)} (expected 40)"
    
    # Test the token with a simple API call
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github+json'
        }
        response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
        if response.status_code == 200:
            user = response.json()
            return True, f"Token valid for user: {user.get('login', 'unknown')}"
        else:
            return False, f"GitHub API returned {response.status_code}: {response.text}"
    except Exception as e:
        return False, f"Failed to validate token: {str(e)}"

# --- GitHub Search Coordinator Agent ---
github_search_coordinator = Agent(
    name="GitHub Search Coordinator",
    model=OpenAIChat("gpt-4.1"),
    description="You coordinate GitHub repository searches to find trending repositories.",
    instructions=[
        "You plan and coordinate searches for trending GitHub repositories.",
        "Focus on finding the most popular and trending repositories.",
        "Generate search queries to find the most starred and active repositories.",
        "Consider different programming languages and trending topics.",
        "Return search parameters in this JSON format:",
        "```json",
        "{",
        "  \"search_query\": \"stars:>1000\",",
        "  \"sort\": \"stars\",",
        "  \"order\": \"desc\",",
        "  \"per_page\": 10",
        "}",
        "```",
        "IMPORTANT: Return ONLY the JSON object, no other text."
    ],
    show_tool_calls=True,
    markdown=True,
)

# --- GitHub Repository Fetcher Agent ---
github_repo_fetcher = Agent(
    name="GitHub Repository Fetcher",
    model=OpenAIChat("gpt-4.1-mini"),
    description="You fetch trending GitHub repositories using GitHub tools.",
    instructions=[
        "Use GitHub tools to search for trending repositories.",
        "You will receive search parameters and use them to find repositories.",
        "Search for the most popular and trending repositories.",
        "Sort by stars in descending order to get the most popular ones.",
        "Get repository details including: name, description, stars, URL, language, owner.",
        "Focus on the top 10 most starred repositories.",
        "Use the search_repositories function with the provided parameters.",
        "If GitHub tools are not available, explain that GitHub API access is required.",
        "Return results in this JSON format:",
        "```json",
        "[",
        "  {",
        "    \"name\": \"repository-name\",",
        "    \"full_name\": \"owner/repository-name\",",
        "    \"description\": \"Repository description\",",
        "    \"stars\": 1234,",
        "    \"url\": \"https://github.com/owner/repository-name\",",
        "    \"language\": \"Python\",",
        "    \"owner\": \"owner-name\"",
        "  }",
        "]",
        "```",
        "IMPORTANT: Return ONLY the JSON array, no other text."
    ],
    tools=get_github_tools(),
    show_tool_calls=True,
    markdown=True,
)

# --- Repository Data Analyzer Agent ---
repo_data_analyzer = Agent(
    name="Repository Data Analyzer",
    model=OpenAIChat("gpt-4.1-mini"),
    description="You analyze and rank GitHub repository data to create a clean summary.",
    instructions=[
        "You will receive raw GitHub repository data and clean it up.",
        "Analyze the repositories and ensure they are properly ranked by stars.",
        "Clean up descriptions to be concise and readable.",
        "Ensure all data is properly formatted.",
        "Remove any repositories that might be spam or low quality.",
        "Verify that URLs are properly formatted.",
        "Return the top 10 repositories in this JSON format:",
        "```json",
        "[",
        "  {",
        "    \"rank\": 1,",
        "    \"name\": \"repository-name\",",
        "    \"full_name\": \"owner/repository-name\",",
        "    \"description\": \"Clean, concise description\",",
        "    \"stars\": 1234,",
        "    \"url\": \"https://github.com/owner/repository-name\",",
        "    \"language\": \"Python\",",
        "    \"owner\": \"owner-name\"",
        "  }",
        "]",
        "```",
        "IMPORTANT: Return ONLY the JSON array, no other text."
    ],
    show_tool_calls=True,
    markdown=True,
)

# --- Telegram Message Formatter Agent ---
telegram_formatter = Agent(
    name="Telegram Message Formatter",
    model=OpenAIChat("gpt-4.1-mini"),
    description="You create Telegram-optimized messages for GitHub trending repositories.",
    instructions=[
        "You will receive analyzed GitHub repository data and format it for Telegram.",
        "Create a message optimized for Telegram with MarkdownV2 formatting.",
        "Use this exact structure:",
        "- Header: '*🔥 Top 10 GitHub Trending Repos*'",
        "- Subheader: '*Most Popular Repositories*'",
        "- List each repository with bullet points using •",
        "- Format: '• **[Repository Name](url)** ⭐ X,XXX'",
        "- Include description on next line indented with 2 spaces",
        "- Add footer with generation timestamp",
        "Follow this structure exactly:",
        "*🔥 Top 10 GitHub Trending Repos*",
        "*Most Popular Repositories*",
        "",
        "• **[freeCodeCamp](https://github.com/freeCodeCamp/freeCodeCamp)** ⭐ 419,830",
        "  Open-source codebase and curriculum for learning programming",
        "",
        "• **[awesome](https://github.com/sindresorhus/awesome)** ⭐ 363,497",
        "  Curated lists of awesome projects",
        "",
        "[Continue for all repositories]",
        "",
        "_Generated on [timestamp]_",
        "",
        "Format guidelines:",
        "- Use *bold* for headers (single asterisks)",
        "- Use **bold** for repository names inside links",
        "- Use • for bullet points",
        "- Format links as: [text](url)",
        "- Add comma separators for thousands in star counts",
        "- Keep descriptions under 80 characters",
        "- Use 2 spaces for indentation of descriptions",
        "- Do NOT escape any characters - the system will handle escaping",
        "IMPORTANT: Return ONLY the formatted message text, no code blocks or extra formatting."
    ],
    show_tool_calls=True,
    markdown=True,
)

# --- Final Assembly Agent ---
final_assembly_agent = Agent(
    name="Final Assembly Agent",
    model=OpenAIChat("gpt-4.1-mini"),
    description="You combine all components into the final GitHub trending report.",
    instructions=[
        "You will receive the formatted Telegram message and finalize it.",
        "Ensure the message is properly formatted and ready to send.",
        "Verify all links are working and properly formatted.",
        "Make sure the star counts are properly formatted with commas.",
        "Ensure the date range is accurate.",
        "Add any final touches to make the message engaging.",
        "Return the final message exactly as it should be sent to Telegram.",
        "IMPORTANT: Return ONLY the final message text, no other formatting or explanation."
    ],
    show_tool_calls=True,
    markdown=True,
)

# --- Utility Functions (from enhanced-daily-news pattern) ---

def escape_markdown_v2(text: str) -> str:
    """Escape special characters for Telegram MarkdownV2."""
    # Characters that need to be escaped in MarkdownV2
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    
    return text

def format_for_markdown_v2(text: str, preserve_markdown: bool = True) -> str:
    """Format text for Telegram MarkdownV2, preserving intentional markdown."""
    if not text:
        return ""
    
    # For Telegram MarkdownV2, we need to be more careful with escaping
    # Characters that need escaping in MarkdownV2 (excluding markdown syntax we want to keep)
    chars_to_escape = ['_', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!', '(', ')']
    
    result = text
    
    # Handle links first - extract and protect them
    import re
    links = []
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    
    def replace_link(match):
        text_part = match.group(1)
        url_part = match.group(2)
        # Escape special chars in link text only, not in URL
        escaped_text = text_part
        for char in ['_', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']:  # Don't escape () in link text
            if char in escaped_text:
                escaped_text = escaped_text.replace(char, f'\\{char}')
        placeholder = f"LINKPLACEHOLDER{len(links)}LINKEND"  # Use a safe placeholder
        links.append(f'[{escaped_text}]({url_part})')
        return placeholder
    
    result = re.sub(link_pattern, replace_link, result)
    
    # Handle bold text (**text** -> *text* for MarkdownV2)
    bold_pattern = r'\*\*([^*]+)\*\*'
    def replace_bold(match):
        content = match.group(1)
        # Don't escape content that's inside bold - let it stay as is for better readability
        return f'*{content}*'
    
    result = re.sub(bold_pattern, replace_bold, result)
    
    # Escape remaining special characters in regular text (but not in our placeholders or markdown)
    for char in chars_to_escape:
        # Skip if this char is part of our placeholder or already escaped
        if char in result:
            # Use a more careful replacement that avoids placeholders and existing escapes
            temp_result = ""
            i = 0
            while i < len(result):
                if result[i:i+len(f'\\{char}')] == f'\\{char}':
                    # Already escaped, keep as is
                    temp_result += f'\\{char}'
                    i += len(f'\\{char}')
                elif result[i:].startswith('LINKPLACEHOLDER'):
                    # This is a link placeholder, find the end and keep as is
                    end_pos = result.find('LINKEND', i)
                    if end_pos != -1:
                        temp_result += result[i:end_pos + len('LINKEND')]
                        i = end_pos + len('LINKEND')
                    else:
                        temp_result += result[i]
                        i += 1
                elif result[i] == char:
                    # Need to escape this character
                    temp_result += f'\\{char}'
                    i += 1
                else:
                    temp_result += result[i]
                    i += 1
            result = temp_result
    
    # Restore links
    for i, link in enumerate(links):
        result = result.replace(f"LINKPLACEHOLDER{i}LINKEND", link)
    
    return result

async def send_telegram_message(message: str, bot_token: str, chat_id: str):
    """Send message to Telegram using async bot."""
    try:
        bot = Bot(token=bot_token)
        
        # Format message for MarkdownV2
        formatted_message = format_for_markdown_v2(message)
        
        # Split message if too long (Telegram limit is 4096 characters)
        max_length = 4000  # Leave some buffer
        
        if len(formatted_message) <= max_length:
            await bot.send_message(
                chat_id=chat_id,
                text=formatted_message,
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=False
            )
            print("✅ Telegram message sent successfully")
        else:
            # Split into multiple messages
            parts = []
            current_part = ""
            
            for line in formatted_message.split('\n'):
                if len(current_part + line + '\n') > max_length:
                    if current_part:
                        parts.append(current_part.strip())
                        current_part = line + '\n'
                    else:
                        # Single line is too long, force split
                        parts.append(line[:max_length])
                        current_part = line[max_length:] + '\n'
                else:
                    current_part += line + '\n'
            
            if current_part:
                parts.append(current_part.strip())
            
            # Send each part
            for i, part in enumerate(parts):
                if i > 0:
                    part = f"*📝 Continued...*\n\n{part}"
                
                await bot.send_message(
                    chat_id=chat_id,
                    text=part,
                    parse_mode=ParseMode.MARKDOWN_V2,
                    disable_web_page_preview=False
                )
                
                # Small delay between messages
                await asyncio.sleep(1)
            
            print(f"✅ Telegram message sent successfully in {len(parts)} parts")
        
        await bot.close()
        
    except Exception as e:
        print(f"❌ Error sending Telegram message: {str(e)}")
        print(f"   Message preview: {message[:100]}...")
        raise e

def send_telegram_message_sync(message: str, bot_token: str, chat_id: str):
    """Synchronous wrapper for Telegram message sending."""
    try:
        asyncio.run(send_telegram_message(message, bot_token, chat_id))
    except Exception as e:
        print(f"❌ Error in sync Telegram send: {str(e)}")
        raise e

def extract_json_from_response(response_text):
    """Extract JSON from agent response text."""
    if not response_text:
        return None
        
    try:
        # Try to parse the entire response as JSON first
        return json.loads(response_text.strip())
    except:
        pass
    
    # Look for JSON block in markdown
    json_pattern = r'```json\s*(.*?)\s*```'
    matches = re.findall(json_pattern, response_text, re.DOTALL)
    
    if matches:
        try:
            return json.loads(matches[0])
        except:
            pass
    
    # Look for JSON object without markdown
    json_pattern = r'\{.*\}'
    matches = re.findall(json_pattern, response_text, re.DOTALL)
    
    if matches:
        try:
            return json.loads(matches[0])
        except:
            pass
    
    # Look for JSON array without markdown
    json_pattern = r'\[.*\]'
    matches = re.findall(json_pattern, response_text, re.DOTALL)
    
    if matches:
        try:
            return json.loads(matches[0])
        except:
            pass
    
    return None

def safe_get_content(response):
    """Safely extract content from agent response."""
    if hasattr(response, 'content') and response.content:
        return response.content
    elif isinstance(response, str):
        return response
    else:
        return str(response)

def fallback_github_search(search_query, max_repos=10):
    """
    Fallback GitHub API search when Agno tools are not available.
    Uses direct GitHub API calls.
    """
    try:
        print("🔄 Using fallback GitHub API search...")
        
        url = "https://api.github.com/search/repositories"
        headers = {
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        
        # Add authentication if token is available
        if github_token:
            headers['Authorization'] = f'Bearer {github_token}'
        
        params = {
            'q': search_query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': max_repos
        }
        
        print(f"   API URL: {url}")
        print(f"   Query: {search_query}")
        print(f"   Headers: {list(headers.keys())}")
        
        response = requests.get(url, headers=headers, params=params)
        
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            
            print(f"   Found {len(items)} repositories")
            
            # Convert to our expected format
            repos = []
            for item in items:
                # Fix the None description bug
                description = item.get('description') or 'No description available'
                if len(description) > 100:
                    description = description[:100]
                
                repo = {
                    "name": item.get('name', ''),
                    "full_name": item.get('full_name', ''),
                    "description": description,
                    "stars": item.get('stargazers_count', 0),
                    "url": item.get('html_url', ''),
                    "language": item.get('language') or 'Unknown',
                    "owner": item.get('owner', {}).get('login', ''),
                    "created_at": item.get('created_at', '')
                }
                repos.append(repo)
            
            return repos
        else:
            print(f"   API Error: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        print(f"   Fallback API error: {e}")
        return []

def run_github_trending_agent(days_back=7, max_repos=10, send_telegram=True):
    """
    Main function to run the GitHub trending repositories agent.
    
    Args:
        days_back (int): Unused - kept for compatibility
        max_repos (int): Maximum number of repositories to return
        send_telegram (bool): Whether to send the result to Telegram
    
    Returns:
        str: The final formatted message or error message
    """
    
    try:
        print("🐙 Starting GitHub Trending Repositories Agent")
        print("=" * 50)
        
        # Check prerequisites
        print("🔧 Checking prerequisites...")
        
        # Check OpenAI API key
        if not os.environ.get("OPENAI_API_KEY"):
            error_msg = "❌ OPENAI_API_KEY is required but not set."
            print(error_msg)
            print("   Please set your OpenAI API key:")
            print("   export OPENAI_API_KEY='your-openai-key-here'")
            return error_msg
        
        # Check GitHub token
        if not github_token:
            print("⚠️  GITHUB_TOKEN not set. You'll have limited API access (60 requests/hour).")
            print("   For better performance, set your GitHub token:")
            print("   1. Go to https://github.com/settings/tokens")
            print("   2. Generate a new token with 'public_repo' scope")
            print("   3. export GITHUB_TOKEN='your-github-token-here'")
            print("   4. Without a token, the agent may fail due to rate limits.")
            print("")
            
            # Ask user if they want to continue
            if not send_telegram:  # Only for manual runs, not scheduled
                response = input("   Continue anyway? (y/n): ").lower().strip()
                if response != 'y':
                    return "Setup cancelled by user. Please configure GitHub token and try again."
        else:
            print("✅ GitHub token configured")
        
        # Check Telegram setup (optional)
        if send_telegram:
            if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
                print("✅ Telegram delivery configured")
            else:
                print("⚠️  Telegram delivery disabled - missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
                send_telegram = False
        
        print("")
        
        # Step 1: Plan the search strategy
        print("📋 Step 1: Planning GitHub search strategy...")
        
        coordinator_prompt = f"""
        Plan a GitHub search to find the top {max_repos} trending repositories.
        Focus on the most popular and highly-starred repositories.
        """
        
        coordinator_response = github_search_coordinator.run(coordinator_prompt)
        coordinator_content = safe_get_content(coordinator_response)
        
        print(f"📋 Coordinator response: {coordinator_content[:200]}...")
        
        search_params = extract_json_from_response(coordinator_content)
        if not search_params:
            print("❌ Failed to get search parameters from coordinator")
            return "Error: Could not plan GitHub search strategy"
        
        print(f"✅ Search parameters: {search_params}")
        
        # Step 2: Fetch repositories using GitHub tools
        print("🔍 Step 2: Fetching trending repositories...")
        
        search_query = search_params.get('search_query', 'stars:>1000')
        print(f"   Search query: {search_query}")
        
        fetcher_prompt = f"""
        Search for GitHub repositories using these parameters:
        - Query: {search_query}
        - Sort by: stars (descending)
        - Maximum results: {max_repos}
        
        Use the GitHub search tools to find the most popular repositories.
        If you don't have access to GitHub tools, return a helpful error message explaining that GITHUB_TOKEN is required.
        """
        
        fetcher_response = github_repo_fetcher.run(fetcher_prompt)
        fetcher_content = safe_get_content(fetcher_response)
        
        print(f"🔍 Fetcher response: {fetcher_content[:300]}...")
        
        # Check if the response indicates missing GitHub access
        if "GitHub API access is required" in fetcher_content or "GITHUB_TOKEN" in fetcher_content:
            error_msg = "Error: GitHub API access is required but not properly configured."
            print(f"❌ {error_msg}")
            print("   Please set up your GitHub token and try again.")
            return error_msg
        
        repo_data = extract_json_from_response(fetcher_content)
        
        # If Agno tools failed or returned empty, try fallback
        if not repo_data or len(repo_data) == 0:
            print("⚠️  Agno GitHub tools returned no data, trying fallback API...")
            repo_data = fallback_github_search(search_query, max_repos)
        
        if not repo_data or len(repo_data) == 0:
            print("❌ Failed to get repository data from any source")
            return "Error: Could not fetch GitHub repositories. This might be due to rate limiting or missing GitHub token."
        
        print(f"✅ Found {len(repo_data)} repositories")
        
        # Step 3: Analyze and clean the data
        print("📊 Step 3: Analyzing repository data...")
        
        analyzer_prompt = f"""
        Analyze and clean this GitHub repository data:
        {json.dumps(repo_data, indent=2)}
        
        Ensure repositories are ranked by stars, clean up descriptions, and return the top {max_repos}.
        """
        
        analyzer_response = repo_data_analyzer.run(analyzer_prompt)
        analyzer_content = safe_get_content(analyzer_response)
        
        print(f"📊 Analyzer response: {analyzer_content[:200]}...")
        
        analyzed_data = extract_json_from_response(analyzer_content)
        if not analyzed_data:
            print("❌ Failed to get analyzed data")
            return "Error: Could not analyze repository data"
        
        print(f"✅ Analyzed {len(analyzed_data)} repositories")
        
        # Step 4: Format for Telegram
        print("📱 Step 4: Formatting message for Telegram...")
        
        date_range = f"Trending Repositories"
        
        formatter_prompt = f"""
        Format this GitHub repository data for Telegram:
        {json.dumps(analyzed_data, indent=2)}
        
        Date range: {date_range}
        Current timestamp: {datetime.now().strftime('%B %d, %Y at %H:%M CET')}
        
        Create an engaging Telegram message with the specified format.
        """
        
        formatter_response = telegram_formatter.run(formatter_prompt)
        formatter_content = safe_get_content(formatter_response)
        
        print(f"📱 Formatter response: {formatter_content[:200]}...")
        
        # Step 5: Final assembly
        print("🔧 Step 5: Final assembly...")
        
        assembly_prompt = f"""
        Finalize this Telegram message for GitHub trending repositories:
        
        {formatter_content}
        
        Ensure it's properly formatted and ready to send.
        """
        
        assembly_response = final_assembly_agent.run(assembly_prompt)
        final_message = safe_get_content(assembly_response)
        
        print("✅ Final message generated successfully")
        print("📄 Message preview:")
        print("-" * 30)
        print(final_message[:500] + "..." if len(final_message) > 500 else final_message)
        print("-" * 30)
        
        # Step 6: Send to Telegram (if enabled)
        if send_telegram and TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            print("📤 Step 6: Sending to Telegram...")
            try:
                send_telegram_message_sync(final_message, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
                print("✅ Successfully sent to Telegram!")
            except Exception as e:
                print(f"❌ Failed to send to Telegram: {str(e)}")
                print("📝 Message content was generated successfully though.")
        elif send_telegram:
            print("⚠️  Telegram sending skipped - missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
        else:
            print("ℹ️  Telegram sending disabled")
        
        print("🎉 GitHub Trending Agent completed successfully!")
        return final_message
        
    except Exception as e:
        error_msg = f"Critical error in GitHub Trending Agent: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        return error_msg

# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing GitHub Trending Agent")
    print(check_github_token())
    result = run_github_trending_agent(
        days_back=7,
        max_repos=10,
        send_telegram=True  # Enable Telegram sending
    )
    print("\n" + "="*50)
    print("FINAL RESULT:")
    print("="*50)
    print(result) 