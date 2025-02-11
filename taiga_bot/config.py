"""Configuration for the TaigaBot"""
import os
from typing import Final
from dotenv import load_dotenv # pylint: disable=import-error # pyright: ignore[reportMissingImports]

load_dotenv()

# Discord configuration
DISCORD_TOKEN: Final[str] = os.environ['DISCORD_TOKEN']
CHANNEL_ID: Final[int] = int(os.environ['CHANNEL_ID'])
FORUM_ID: Final[int] = int(os.environ['FORUM_ID'])

# Taiga configuration
TAIGA_USERNAME: Final[str] = os.environ['TAIGA_USERNAME']
TAIGA_PASSWORD: Final[str] = os.environ['TAIGA_PASSWORD']
TAIGA_BASE_URL: Final[str] = os.environ['TAIGA_BASE_URL']


# Webhook configuration
SECRET_KEY: Final[str] = os.environ['SECRET_KEY']
WEBHOOK_ROUTE: Final[str] = os.getenv('WEBHOOK_ROUTE', '/webhook')

# Validate required environment variables
def validate_config():
    """validate_config"""
    if not TAIGA_USERNAME:
        raise ValueError("TAIGA_USERNAME must be set in environment")
    if not TAIGA_PASSWORD:
        raise ValueError("TAIGA_PASSWORD must be set in environment")
    if not TAIGA_BASE_URL:
        raise ValueError("TAIGA_BASE_URL must be set in environment")
    if not DISCORD_TOKEN:
        raise ValueError("DISCORD_TOKEN must be set in environment")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in environment")
    if not CHANNEL_ID:
        raise ValueError("CHANNEL_ID must be set in environment")
    if not FORUM_ID:
        raise ValueError("FORUM_ID must be set in environment")

# Validate on import
#validate_config()
