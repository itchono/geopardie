import os
from pathlib import Path

from geopardie.core.bot_client import CustomClient


def load_extensions(bot: CustomClient):
    """Automatically load all extension in the ./extensions folder"""

    bot.logger.info("Loading Extensions...")

    # go through all folders in the directory and load the extensions from all files
    # Note: files must end in .py
    bot.load_extension("geopardie.extensions.geopardie_game")
    # bot.load_extension("geopardie.extensions.user_analyzer")

    bot.logger.info(
        f"< {len(bot.interactions.get(0, []))} > Global Interactions Loaded")
