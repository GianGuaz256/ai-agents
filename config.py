from dotenv import load_dotenv
import os
from pathlib import Path

# Ottieni il percorso della directory root del progetto
ROOT_DIR = Path(__file__).resolve().parent

# Carica le variabili d'ambiente dal file .env
load_dotenv(ROOT_DIR / '.env')

# Configurazione delle variabili d'ambiente
class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    
    # Google Calendar Configuration
    GOOGLE_CALENDAR_CREDENTIALS = os.getenv('GOOGLE_CALENDAR_CREDENTIALS')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

    # Firecrawl Configuration
    FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY')
    APIFY_API_TOKEN = os.getenv('APIFY_API_TOKEN')
    
    # Environment Configuration
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Model Configuration
    MODEL_NAME = os.getenv('MODEL_NAME', 'gpt-4')
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '2000'))

    @classmethod
    def validate(cls):
        """Valida che tutte le variabili d'ambiente necessarie siano presenti"""
        required_vars = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_CALENDAR_CREDENTIALS', 'FIRECRAWL_API_KEY', 'APIFY_API_TOKEN', 'GOOGLE_API_KEY']
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Crea un'istanza globale della configurazione
config = Config()

# Valida la configurazione all'avvio
config.validate() 