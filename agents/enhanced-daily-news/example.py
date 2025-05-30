#!/usr/bin/env python3
"""
Example script demonstrating the Enhanced Daily News Agent System

This script shows how to use the news research system programmatically
with different configurations and topics.
"""

import os
import sys
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import run_daily_news_research
from config import get_topics_by_preset, validate_config

def example_basic_usage():
    """Example 1: Basic usage with default topics"""
    print("=" * 60)
    print("📰 EXAMPLE 1: Basic Usage with Default Topics")
    print("=" * 60)
    
    # Use default topics
    summary = run_daily_news_research()
    return summary

def example_preset_usage():
    """Example 2: Using a preset topic collection"""
    print("\n" + "=" * 60)
    print("📰 EXAMPLE 2: Using Crypto/Finance Preset")
    print("=" * 60)
    
    # Get topics from preset
    topics = get_topics_by_preset("crypto_finance")
    summary = run_daily_news_research(topics=topics, max_articles_per_topic=3)
    return summary

def example_custom_topics():
    """Example 3: Using custom topics"""
    print("\n" + "=" * 60)
    print("📰 EXAMPLE 3: Custom Topics")
    print("=" * 60)
    
    # Define custom topics
    custom_topics = [
        "Tesla stock price",
        "OpenAI GPT developments",
        "Federal Reserve interest rates",
        "Bitcoin ETF approval"
    ]
    
    summary = run_daily_news_research(topics=custom_topics, max_articles_per_topic=4)
    return summary

def example_focused_research():
    """Example 4: Focused research on specific topic"""
    print("\n" + "=" * 60)
    print("📰 EXAMPLE 4: Focused AI Research")
    print("=" * 60)
    
    # Focus on AI developments
    ai_topics = [
        "ChatGPT OpenAI updates",
        "Google Bard AI developments",
        "AI regulation policy",
        "Machine learning breakthroughs"
    ]
    
    summary = run_daily_news_research(topics=ai_topics, max_articles_per_topic=5)
    return summary

def save_summary_to_file(summary, filename_prefix):
    """Save summary to a timestamped file"""
    if summary and "Critical error" not in summary:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{filename_prefix}_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Daily News Summary - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                f.write(summary)
            
            print(f"📁 Summary saved to: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Error saving file: {e}")
    
    return None

def main():
    """Main function demonstrating different usage patterns"""
    print("🌟 Enhanced Daily News Agent System - Examples")
    print("🤖 Using GPT-4o-mini with DuckDuckGo and Firecrawl")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Validate configuration
    print("\n🔧 Validating configuration...")
    if not validate_config():
        print("❌ Configuration validation failed.")
        print("Please ensure OPENAI_API_KEY is set in your environment.")
        return
    
    print("✅ Configuration validated successfully")
    
    # Ask user which example to run
    print("\n📋 Available Examples:")
    print("1. Basic usage with default topics")
    print("2. Crypto/Finance preset")
    print("3. Custom topics")
    print("4. Focused AI research")
    print("5. Run all examples")
    
    try:
        choice = input("\n🔢 Choose an example (1-5): ").strip()
        
        if choice == "1":
            summary = example_basic_usage()
            save_summary_to_file(summary, "basic_example")
            
        elif choice == "2":
            summary = example_preset_usage()
            save_summary_to_file(summary, "crypto_example")
            
        elif choice == "3":
            summary = example_custom_topics()
            save_summary_to_file(summary, "custom_example")
            
        elif choice == "4":
            summary = example_focused_research()
            save_summary_to_file(summary, "ai_example")
            
        elif choice == "5":
            print("\n🚀 Running all examples...")
            
            # Run all examples
            summaries = []
            summaries.append(("basic", example_basic_usage()))
            summaries.append(("crypto", example_preset_usage()))
            summaries.append(("custom", example_custom_topics()))
            summaries.append(("ai", example_focused_research()))
            
            # Save all summaries
            for name, summary in summaries:
                save_summary_to_file(summary, f"{name}_example")
            
            print(f"\n✅ All examples completed! Generated {len(summaries)} summaries.")
            
        else:
            print("❌ Invalid choice. Please run the script again.")
            
    except KeyboardInterrupt:
        print("\n\n👋 Examples cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")

if __name__ == "__main__":
    main() 