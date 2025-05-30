#!/usr/bin/env python3
"""
Enhanced Daily News Research CLI Runner

This script provides a command-line interface to run the enhanced daily news research system.
It supports custom topics, presets, and various configuration options.

Usage Examples:
    python run_news.py
    python run_news.py --preset crypto_finance
    python run_news.py --topics "Bitcoin" "AI" "Politics"
    python run_news.py --preset tech_ai --articles 5 --quiet
"""

import argparse
import sys
import os
from datetime import datetime, date

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from agent import run_daily_news_research, DEFAULT_TOPICS
    from config import TOPIC_PRESETS, OPENAI_API_KEY
except ImportError as e:
    print(f"❌ Error importing required modules: {e}")
    print("Make sure you're running this script from the enhanced-daily-news directory")
    sys.exit(1)

def validate_environment():
    """Validate that required environment variables are set."""
    if not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY environment variable is not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return False
    return True

def get_topics_from_preset(preset_name):
    """Get topics from a preset configuration."""
    if preset_name not in TOPIC_PRESETS:
        print(f"❌ Unknown preset: {preset_name}")
        print(f"Available presets: {', '.join(TOPIC_PRESETS.keys())}")
        return None
    
    return TOPIC_PRESETS[preset_name]['topics']

def save_summary_to_file(summary, custom_filename=None):
    """Save the news summary to a markdown file."""
    if custom_filename:
        filename = custom_filename if custom_filename.endswith('.md') else f"{custom_filename}.md"
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"news_summary_{timestamp}.md"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Daily News Summary - {date.today().strftime('%B %d, %Y')}\n\n")
            f.write(summary)
        print(f"📁 Summary saved to: {filename}")
        return filename
    except Exception as e:
        print(f"⚠️ Error saving file: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(
        description="Enhanced Daily News Research System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Use default topics, ask before saving
  %(prog)s --preset crypto_finance            # Use crypto/finance preset
  %(prog)s --topics "Tesla" "Apple"           # Default topics + Tesla and Apple
  %(prog)s --preset tech_ai --articles 5     # Tech preset with 5 articles per topic
  %(prog)s --quiet --output my_news           # Quiet mode with auto-save to my_news.md
  %(prog)s --no-save                          # Generate summary but don't save file
  %(prog)s --quiet --no-save                  # Silent run without file creation

Available Presets:
  crypto_finance  - Bitcoin, DeFi, crypto markets, financial regulation
  tech_ai         - AI/ML, tech companies, software development, cybersecurity  
  politics_economy - US/Global politics, economics, policy, elections
  business_markets - Stock markets, business news, corporate earnings, economic indicators
  science_health  - Medical research, scientific discoveries, health policy, climate
  default         - Balanced mix of Bitcoin, AI, Politics, Markets
        """
    )
    
    # Topic selection options
    topic_group = parser.add_mutually_exclusive_group()
    topic_group.add_argument(
        '--preset', '-p',
        choices=list(TOPIC_PRESETS.keys()),
        help='Use a predefined topic preset'
    )
    topic_group.add_argument(
        '--topics', '-t',
        nargs='+',
        help='Additional topics to research (added to default: Bitcoin, AI, Politics, Finance)'
    )
    
    # Configuration options
    parser.add_argument(
        '--articles', '-a',
        type=int,
        default=3,
        help='Maximum articles per topic (default: 3)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Custom output filename (without .md extension)'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress detailed progress output'
    )
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save summary to file automatically'
    )
    parser.add_argument(
        '--list-presets',
        action='store_true',
        help='List all available topic presets and exit'
    )
    
    args = parser.parse_args()
    
    # Handle list presets option
    if args.list_presets:
        print("📋 Available Topic Presets:")
        print("=" * 50)
        for name, config in TOPIC_PRESETS.items():
            print(f"\n🔹 {name}")
            print(f"   Description: {config['description']}")
            print(f"   Topics: {', '.join(config['topics'])}")
        return
    
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    # Determine topics to use
    if args.preset:
        topics = get_topics_from_preset(args.preset)
        if topics is None:
            sys.exit(1)
        topic_source = f"preset '{args.preset}'"
    elif args.topics:
        # Add custom topics to default topics instead of replacing them
        topics = DEFAULT_TOPICS + args.topics
        topic_source = f"default topics + custom topics"
    else:
        topics = DEFAULT_TOPICS
        topic_source = "default topics"
    
    # Print configuration
    if not args.quiet:
        print("🌟 Enhanced Daily News Research System")
        print("=" * 50)
        print(f"📅 Date: {date.today().strftime('%B %d, %Y')}")
        print(f"📋 Using: {topic_source}")
        print(f"🔍 Topics: {', '.join(topics)}")
        print(f"📄 Max articles per topic: {args.articles}")
        print(f"💾 Output file: {args.output + '.md' if args.output else 'auto-generated'}")
        print("=" * 50)
    
    try:
        # Run the news research
        if args.quiet:
            # Suppress output during research
            import io
            import contextlib
            
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                summary = run_daily_news_research(
                    topics=topics,
                    max_articles_per_topic=args.articles
                )
        else:
            summary = run_daily_news_research(
                topics=topics,
                max_articles_per_topic=args.articles
            )
        
        # Save to file (unless --no-save is specified)
        filename = None
        if not args.no_save:
            if args.quiet:
                # In quiet mode, save automatically
                filename = save_summary_to_file(summary, args.output)
            else:
                # In interactive mode, ask for confirmation
                try:
                    save_choice = input("\n💾 Save summary to file? (Y/n): ").lower().strip()
                    if save_choice in ['', 'y', 'yes']:
                        filename = save_summary_to_file(summary, args.output)
                    else:
                        print("📝 Summary not saved to file")
                except KeyboardInterrupt:
                    print("\n📝 Summary not saved to file")
        
        # Final status messages
        if args.quiet and filename:
            print(f"✅ News summary completed and saved to: {filename}")
        elif args.quiet:
            print("✅ News summary completed")
        
        if not args.quiet:
            print("\n🎉 Enhanced daily news research completed!")
            print(f"📱 Summary ready for sharing!")
            if filename:
                print(f"📁 Saved to: {filename}")
        
    except KeyboardInterrupt:
        print("\n⚠️ Research interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during news research: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 