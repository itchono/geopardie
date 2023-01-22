from naff import (Button, ButtonStyles, Extension, InteractionContext,
                  ModalContext, OptionTypes, listen, slash_command,
                  slash_option, spread_to_rows)
from naff.api.events.internal import ButtonPressed
from naff.models.naff.application_commands import modal_callback

from geopardie.core.bot_client import CustomClient
from geopardie.framework.embed_prefabs import geopardie_start_embed
from geopardie.framework.geopardie_constructs import PollButtonSession
from geopardie.framework.geopardie_handlers import GeopardieHandlersMixin
from geopardie.framework.modal_prefabs import geopardie_modal


class GeopardieGameExtension(Extension, GeopardieHandlersMixin):
    bot: CustomClient

    '''
    Command - Anonymous Poll

    Format - /geopardie <number of answers (up to 10)>

    Returns: a modal
        - Text box for prompt (long text)
        - N text boxes for answers (short text)
    '''
    @slash_command(name="geopardie", description="Create an anonymous poll")
    @slash_option(name="number_of_answers",
                  description="Number of answers (up to 10)",
                  opt_type=OptionTypes.INTEGER,
                  required=True,
                  min_value=1,
                  max_value=10)
    async def geopardie_start(self, ctx: InteractionContext,
                              number_of_answers: int):
        await ctx.send_modal(modal=geopardie_modal(number_of_answers))

    @modal_callback("geopardie_modal")
    async def geopardie_prompt(self, ctx: ModalContext):

        embed = geopardie_start_embed(ctx)

        buttons = [Button(style=ButtonStyles.PRIMARY,
                          label=f"{i+1}",
                          custom_id=PollButtonSession(i).serialize)
                   for i in range(len(ctx.responses) - 1)]

        close_button = Button(style=ButtonStyles.DANGER,
                              label="Close Voting",
                              custom_id=f"gp_close_{ctx.author.id}",
                              emoji="🗳️")

        components = spread_to_rows(*(buttons + [close_button]))

        await ctx.send(embed=embed, components=components)


    @listen(ButtonPressed)
    async def button_listener(self, event: ButtonPressed):
        # Decode the button and make sure it's a valid button
        if event.ctx.custom_id.startswith("gp_vote"):
            await self.handle_gp_vote(event.ctx)
        elif event.ctx.custom_id.startswith("gp_close"):
            await self.handle_gp_close(event.ctx)
        elif event.ctx.custom_id.startswith("gp_next"):
            await self.handle_gp_next(event.ctx)


def setup(bot: CustomClient):
    """Let naff load the extension"""

    GeopardieGameExtension(bot)
