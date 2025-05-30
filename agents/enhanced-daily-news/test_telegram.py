#!/usr/bin/env python3
"""
Telegram Bot SDK Integration Test

This script tests the new Telegram Bot SDK integration with MarkdownV2 formatting.
Use this to verify your Telegram credentials and message formatting before running
the full news agent system.

Prerequisites:
- Set TELEGRAM_BOT_TOKEN environment variable  
- Set TELEGRAM_CHAT_ID environment variable
- Ensure python-telegram-bot>=21.0.0 is installed

Usage:
    python test_telegram.py
"""

import os
import asyncio
from datetime import date
import dotenv
from agent import send_telegram_message_sync

# Load environment variables
dotenv.load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def test_telegram_delivery():
    """Test the Telegram delivery with markdown formatting."""
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Telegram credentials not configured.")
        print("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables.")
        print()
        print("Setup instructions:")
        print("1. Create a bot: Message @BotFather on Telegram")
        print("2. Send /newbot and follow instructions")
        print("3. Get your chat ID: Start chat with bot, then visit:")
        print("   https://api.telegram.org/bot<TOKEN>/getUpdates")
        print("4. Set environment variables:")
        print("   export TELEGRAM_BOT_TOKEN='your-bot-token'")
        print("   export TELEGRAM_CHAT_ID='your-chat-id'")
        return False
    
    # Create a comprehensive test message with markdown formatting
    test_message = f"""*News Agent - {date.today().strftime('%B %d, %Y')} - Test* ✅

*BTC price:* $45,000
*GOLD price:* $2,100
*EUR/CHF:* 0.9456

*TLDR:* This is a test message to verify the new Telegram Bot SDK integration with MarkdownV2 formatting.

*₿ Bitcoin Update* 🟠
• *Bitcoin* continues to show strength above $45k resistance
• Market sentiment remains *bullish* with institutional adoption
• Technical analysis: [CoinDesk](https://coindesk.com)

*AI Update* 🤖  
• Major *AI breakthrough* announced by leading tech companies
• New models showing improved capabilities in reasoning
• Industry experts predict significant market impact

*Politics Update* ⏳
• Recent policy developments affecting tech sector
• Regulatory discussions on cryptocurrency oversight
• Expert analysis on market implications

*Finance Update* 💰
• Stock markets showing mixed signals
• Federal Reserve policy updates
• Global economic indicators

*Test completed successfully* 🎉

_This is a test message from the Enhanced Daily News Agent system._"""

    print("🧪 Testing Telegram Bot SDK Integration")
    print("=" * 50)
    print(f"📝 Message length: {len(test_message)} characters")
    print(f"🤖 Bot token: {TELEGRAM_BOT_TOKEN[:10]}..." if TELEGRAM_BOT_TOKEN else "❌ Not set")
    print(f"💬 Chat ID: {TELEGRAM_CHAT_ID}")
    print()
    print("📤 Sending test message...")
    
    try:
        success = send_telegram_message_sync(test_message, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        if success:
            print("✅ Test message sent successfully!")
            print("📱 Check your Telegram chat to verify:")
            print("   • Bold formatting appears correctly")
            print("   • Emojis display properly")
            print("   • Links are clickable")
            print("   • Special characters are escaped correctly")
            return True
        else:
            print("❌ Test message failed to send.")
            print("Check your bot token and chat ID.")
            return False
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        print("Common issues:")
        print("• Invalid bot token or chat ID")
        print("• Bot not started (send /start to your bot)")
        print("• Network connectivity issues")
        return False

def test_message_splitting():
    """Test message splitting for long messages."""
    print("\n🧪 Testing Message Splitting")
    print("=" * 50)
    
    # Create a very long message to test splitting
    long_sections = []
    for i in range(10):
        section = f"""*Section {i+1}* 📄
        
This is section number {i+1} with some content to make the message long enough to trigger splitting.
• Point 1 with some detailed information about various topics
• Point 2 with additional content and links [Example](https://example.com)
• Point 3 with more text to increase the overall message length

Additional paragraph with more information to ensure we exceed the 4000 character limit for Telegram messages and test the automatic splitting functionality."""
        long_sections.append(section)
    
    long_message = "\n\n".join(long_sections)
    
    print(f"📝 Long message length: {len(long_message)} characters")
    print("📤 Sending long message to test splitting...")
    
    try:
        success = send_telegram_message_sync(long_message, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        if success:
            print("✅ Long message sent successfully!")
            print("📱 Check that the message was split properly into multiple parts")
            return True
        else:
            print("❌ Long message test failed")
            return False
    except Exception as e:
        print(f"❌ Error during long message test: {str(e)}")
        return False

if __name__ == "__main__":
    print("🌟 Telegram Bot SDK Integration Test")
    print("Enhanced Daily News Agent System")
    print("=" * 50)
    
    # Run basic test
    basic_test_result = test_telegram_delivery()
    
    if basic_test_result and input("\n🔄 Test message splitting? (y/N): ").lower().startswith('y'):
        split_test_result = test_message_splitting()
        
        if basic_test_result and split_test_result:
            print("\n🎉 All tests completed successfully!")
            print("Your Telegram Bot SDK integration is working perfectly.")
            print("You can now run the full news agent with Telegram delivery.")
        else:
            print("\n⚠️ Some tests failed.")
            print("Please check your configuration and try again.")
    elif basic_test_result:
        print("\n🎉 Basic test completed successfully!")
        print("Your Telegram Bot SDK integration is working.")
        print("You can now run the full news agent with Telegram delivery.")
    else:
        print("\n⚠️ Test failed.")
        print("Please check your Telegram bot configuration.")
        print("Refer to the README.md for setup instructions.") 