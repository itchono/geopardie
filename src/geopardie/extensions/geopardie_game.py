from naff import (Button, ButtonStyles, Extension, InteractionContext,
                  ModalContext, OptionTypes, listen, slash_command,
                  slash_option, spread_to_rows)
from naff.api.events.internal import ButtonPressed

from geopardie.core.bot_client import CustomClient
from geopardie.framework.embed_prefabs import geopardie_start_embed
from geopardie.framework.geopardie_constructs import PollButtonSession
from geopardie.framework.geopardie_handlers import GeopardieHandlersMixin
from geopardie.framework.modal_prefabs import get_geopardie_modals


class GeopardieGameExtension(Extension, GeopardieHandlersMixin):
    bot: CustomClient

    '''
    Command - Anonymous Poll

    Format - /geopardie 
                <number of answers (up to 23)>
                <unique answer responses (T/F)>  (later)
                <visibility of response count (T/F)> (later)

    Returns: M modals
        - Text box for prompt (long text)
        - N text boxes for answers (short text)
        - the N text boxes are split into modals such that
          each modal contains no more than 5 text boxes total
          
        e.g. if N = 10, then there will be 3 modals (4, 4, 2)
    '''
    @slash_command(name="geopardie", description="Create an anonymous poll")
    @slash_option(name="number_of_answers",
                  description="Number of answers (up to 23)",
                  opt_type=OptionTypes.INTEGER,
                  required=True,
                  min_value=1,
                  max_value=23)
    async def geopardie_start(self, ctx: InteractionContext,
                              number_of_answers: int):
        
        modals = get_geopardie_modals(number_of_answers)
        
        modal_ctx: ModalContext = None
        
        modal_responses = {}
        
        for idx, modal in enumerate(modals):
            
            await ctx.send_modal(modal)
            modal_ctx: ModalContext = await self.bot.wait_for_modal(modal)
            
            # Dict union with modal_responses (join the two dicts)
            modal_responses |= modal_ctx.responses

            if idx != len(modals) - 1:
                # Queue up a button for the user to click to continue
                # This is necessary because we can't respond to a modal
                # with another modal
                
                cont_button = Button(style=ButtonStyles.PRIMARY,
                                     label="Continue",
                                     emoji="⬇")
                
                btn_msg = await modal_ctx.send("You have more answers to fill out. "
                                     "Click the button below to continue...",
                                        components=spread_to_rows(cont_button))
                
                def author_check(interaction: ButtonPressed):
                    return interaction.ctx.author == modal_ctx.author
                
                ctx = (await self.bot.wait_for_component(components=cont_button,
                                                         check=author_check)).ctx
                
                # Disable button on btn_msg
                cont_button.disabled = True
                await btn_msg.edit(components=spread_to_rows(cont_button))
                
                # loop continues
                
        prompt = modal_responses["modal_prompt"]
            
        # amend the answers list with the answers from the modal
        answers = [modal_responses[f"modal_answer_{i+1}"]
                    for i in range(number_of_answers)]
            
        message_embed = geopardie_start_embed(modal_ctx, prompt, answers)
        
        await self.send_geopardie_message(modal_ctx, number_of_answers, message_embed)


    @listen(ButtonPressed)
    async def button_listener(self, event: ButtonPressed):
        # Decode the button and make sure it's a valid button
        if event.ctx.custom_id.startswith("gp_vote"):
            await self.handle_gp_vote(event.ctx)
        elif event.ctx.custom_id.startswith("gp_close"):
            await self.handle_gp_close(event.ctx)
        elif event.ctx.custom_id.startswith("gp_next"):
            await self.handle_gp_next(event.ctx)
        elif event.ctx.custom_id.startswith("gp_bump"):
            await self.handle_gp_bump(event.ctx)


def setup(bot: CustomClient):
    """Let naff load the extension"""

    GeopardieGameExtension(bot)
