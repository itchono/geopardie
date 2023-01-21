from geopardie.core.bot_client import CustomClient
from naff import (Extension, InteractionContext, OptionTypes,
                  slash_command, slash_option, ModalContext,
                  Button, ButtonStyles, spread_to_rows, component_callback)
from naff.models.naff.application_commands import modal_callback
from geopardie.prefabs.modal_prefabs import geopardie_modal
from geopardie.prefabs.embed_prefabs import geopardie_embed


class GeopardieGameExtension(Extension):
    bot: CustomClient

    # sessions: dict = {} TODO: Implement sessions
    # sessions are stored based on message id

    '''
    Command - Anonymous Poll

    Format - /geopardie <number of answers>

    Args:
        - Number of answers (up to 10)
        - Timeout (up to 120 minutes)

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
    @slash_option(name="timeout",
                  description="Timeout (up to 120 minutes)",
                  opt_type=OptionTypes.INTEGER,
                  required=False,
                  min_value=1,
                  max_value=120)
    async def geopardie_start(self, ctx: InteractionContext,
                              number_of_answers: int, timeout: int = 20):
        await ctx.send_modal(modal=geopardie_modal(number_of_answers))

    '''
    Listener - Modal Response
    '''
    @modal_callback("geopardie_modal")
    async def geopardie_prompt(self, ctx: ModalContext):

        embed = geopardie_embed(ctx)

        components = spread_to_rows(*([
            Button(
                style=ButtonStyles.PRIMARY,
                label=f"{i+1}",
                custom_id=f"geopardie_vote") for i in range(len(ctx.responses) - 1)]
            + [Button(style=ButtonStyles.DANGER, label=f"For {ctx.author.display_name}, close voting",
                      custom_id="geopardie_close", emoji="🗳️")]))

        await ctx.send(embed=embed, components=components)

    @component_callback("geopardie_vote")
    async def geopardie_vote(self, ctx: InteractionContext):
        await ctx.send("You voted! (This does nothing for now)")

    @component_callback("geopardie_close")
    async def geopardie_close(self, ctx: InteractionContext):
        await ctx.send("Voting has been closed! (This does nothing for now)")


def setup(bot: CustomClient):
    """Let naff load the extension"""

    GeopardieGameExtension(bot)
