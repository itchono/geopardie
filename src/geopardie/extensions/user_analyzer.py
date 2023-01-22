# Sniffs all users on the server and scans their UUIDs for collisions in
# the bottom n bits

from naff import (Extension, InteractionContext, OptionTypes, slash_command,
                  slash_option)

from geopardie.core.bot_client import CustomClient


class UserAnalysisExtension(Extension):
    bot: CustomClient

    @slash_command(name="sniff", description="does the funny")
    @slash_option(name="bits", description="number of bits to check",
                  opt_type=OptionTypes.INTEGER)
    async def sniff(self, ctx: InteractionContext, bits: int):
        # Retrieve all members on the server

        guild_id = ctx.guild_id

        guild = self.bot.get_guild(guild_id)

        members = guild.members

        truncated_uuids = [bin(m.id)[-bits:] for m in members]

        # see if there are any duplicates

        duplicates = set(
            [x for x in truncated_uuids if truncated_uuids.count(x) > 1])

        if len(duplicates) == 0:
            await ctx.send("No duplicates found")
        else:
            await ctx.send(f"Found {len(duplicates)} duplicates: {', '.join(duplicates)}")
