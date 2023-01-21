import logging
import os

from naff import Client, listen, logger_name


class CustomClient(Client):
    """Subclass of naff.Client with our own logger and on_startup event"""

    # you can use that logger in all your extensions
    logger = logging.getLogger(logger_name)

    # Default server ID for the bot, for slash commands
    default_scope = os.getenv("DEFAULT_GUILD_ID")

    @listen()
    async def on_startup(self):
        """Gets triggered on startup"""

        # Set default scope for slash commands
        self.debug_scope = self.default_scope

        self.logger.info(f"Geopardie is online. Logged in as {self.user}")
        self.logger.info(
            "Note: Discord needs up to an hour to load your global commands / context menus. They may not appear immediately\n"
        )
