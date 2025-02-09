"""Configuration for the TaigaBot"""
import os
from typing import Final
#from dotenv import load_dotenv

#load_dotenv()

# Discord configuration
DISCORD_TOKEN: Final[str] = os.environ['DISCORD_TOKEN']
CHANNEL_ID: Final[int] = int(os.environ['CHANNEL_ID'])
FORUM_ID: Final[int] = int(os.environ['FORUM_ID'])

# Taiga configuration
TAIGA_BASE_URL: Final[str] = os.getenv('TAIGA_BASE_URL', 'https://api.taiga.io')
TAIGA_AUTH_TOKEN: Final[str] = os.environ['TAIGA_AUTH_TOKEN']

# Webhook configuration
SECRET_KEY: Final[str] = os.environ['SECRET_KEY']
WEBHOOK_ROUTE: Final[str] = os.getenv('WEBHOOK_ROUTE', '/webhook')

# Validate required environment variables
def validate_config():
    """validate_config"""
    if not TAIGA_AUTH_TOKEN:
        raise ValueError("TAIGA_AUTH_TOKEN must be set in .env file")
    if not DISCORD_TOKEN:
        raise ValueError("DISCORD_TOKEN must be set in .env file")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in .env file")
    if not CHANNEL_ID:
        raise ValueError("CHANNEL_ID must be set in .env file")
    if not FORUM_ID:
        raise ValueError("FORUM_ID must be set in .env file")

# Validate on import
validate_config()
