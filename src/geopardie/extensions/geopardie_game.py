from geopardie.core.bot_client import CustomClient
from naff import (Extension, InteractionContext, OptionTypes,
                  slash_command, slash_option, ModalContext,
                  Button, ButtonStyles, spread_to_rows, component_callback,
                  listen)
from naff.models.naff.application_commands import modal_callback
from geopardie.prefabs.modal_prefabs import geopardie_modal
from geopardie.prefabs.embed_prefabs import geopardie_embed
from naff.api.events.internal import ButtonPressed


from dataclasses import dataclass, field
import struct
import base64

'''
Button Session Dataclass

This is used to store information about a given poll session, which is stored
into the custom_id of the buttons that are sent with the embed as a base85 encoded string

The entire custom_id must be less than 100 characters, so we need to keep the
storage of the data as small as possible.

Things to Store
----------------
voted_ids: list[int]
    the bottom 16 bits of the user id of the user who voted
    we do this because we are cheap on space and we don't need to store the entire user id

'''


@dataclass
class PollButtonSession:
    '''
    Max string bandwidth (100 char - 7 char prefix) = 93 char
    b85 overhead = 1.25 --> 93 / 1.25 = 74.4 bytes
    Each member of the list is 2 bytes, so we can store 37 members
    '''
    position_id: int
    voted_ids: list[int] = field(default_factory=list)

    @property
    def serialize(self) -> str:
        effective_arr = [self.position_id] + self.voted_ids
        data_bytes = struct.pack(f">{len(effective_arr)}H", *effective_arr)
        return "gp_vote" + base64.b85encode(data_bytes).decode("utf-8")

    @classmethod
    def deserialize(cls, string: str):
        data_bytes = base64.b85decode(string[7:].encode("utf-8"))
        effective_arr = list(
            struct.unpack(
                f">{len(data_bytes)//2}H",
                data_bytes))
        voted_ids = effective_arr[1:]
        return cls(effective_arr[0], voted_ids)

    def add_vote(self, user_id: int):
        # Take only the bottom 16 bits of the user id
        truncated_user_id = user_id & 0xFFFF

        if truncated_user_id not in self.voted_ids:
            self.voted_ids.append(truncated_user_id)
            
    def remove_vote(self, user_id: int):
        # Take only the bottom 16 bits of the user id
        truncated_user_id = user_id & 0xFFFF
        
        self.voted_ids.remove(truncated_user_id)

    def check_vote(self, user_id: int) -> bool:
        # Take only the bottom 16 bits of the user id
        truncated_user_id = user_id & 0xFFFF

        return truncated_user_id in self.voted_ids


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
    async def geopardie_start(self, ctx: InteractionContext,
                              number_of_answers: int):
        await ctx.send_modal(modal=geopardie_modal(number_of_answers))

    '''
    Listener - Modal Response
    '''
    @modal_callback("geopardie_modal")
    async def geopardie_prompt(self, ctx: ModalContext):

        embed = geopardie_embed(ctx)

        buttons = [Button(style=ButtonStyles.PRIMARY,
                          label=f"{i+1}",
                          custom_id=PollButtonSession(i).serialize)
                   for i in range(len(ctx.responses) - 1)]

        components = spread_to_rows(*(buttons
                                      + [Button(style=ButtonStyles.DANGER,
                                                label="Close Voting",
                                                custom_id="geopardie_close",
                                                emoji="🗳️")]))

        await ctx.send(embed=embed, components=components)

    '''
    Listener - Button Response

    This is designed to listen for the buttons that are sent with the embed

    The buttons themselves are encoded with a serialized state
    '''
    @listen(ButtonPressed)
    async def button_listener(self, event: ButtonPressed):
        ctx = event.ctx
        # Decode the button and make sure it's a valid button
        if not ctx.custom_id.startswith("gp_vote"):
            return
        
        button_session = PollButtonSession.deserialize(ctx.custom_id)
        
        # Check if user has already voted
        if button_session.check_vote(ctx.author.id):
            send_msg = "You have already voted, removing vote."
            button_session.remove_vote(ctx.author.id)
        else:
            send_msg = "Your vote has been recorded!"
            button_session.add_vote(ctx.author.id)

        # Edit original message - update components
        msg_components = ctx.message.components

        # Match position of button in components
        for row in msg_components:
            button: Button
            for button in row.components:
                if button.custom_id == ctx.custom_id:
                    # Update button
                    button.custom_id = button_session.serialize
                    
        # Edit message (without responding to interaction)
        await ctx.message.edit(embed=ctx.message.embeds[0],
                               components=msg_components)

        await ctx.send(send_msg, ephemeral=True)

    @component_callback("geopardie_close")
    async def geopardie_close(self, ctx: InteractionContext):
        referenced_msg = ctx.channel.get_message(ctx.message.message_reference.message_id)
        
        # Check that clicker is author
        if ctx.author.id != referenced_msg.author.id:
            return await ctx.send("You are not the author of this poll!",
                                  ephemeral=True)
        
        # Tally votes
        components = ctx.message.components

        # find all option buttons
        option_buttons: list[Button] = []

        for row in components:
            button: Button
            for button in row.components:
                if button.custom_id != "geopardie_close":
                    option_buttons.append(button)

        # Count votes
        sessions = [PollButtonSession.deserialize(
            button.custom_id) for button in option_buttons]
        counts = [len(session.voted_ids) for session in sessions]
        
        # Disable all buttons
        for row in components:
            button: Button
            for button in row.components:
                button.disabled = True
                
        # Edit message (without responding to interaction)
        await ctx.message.edit(embed=ctx.message.embeds[0],
                               components=components)

        await ctx.send("Voting has been closed!"
                       f" The results are: {counts} (in order of the buttons)")


def setup(bot: CustomClient):
    """Let naff load the extension"""

    GeopardieGameExtension(bot)
