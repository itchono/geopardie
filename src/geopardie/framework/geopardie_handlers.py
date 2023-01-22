from naff import Button, InteractionContext, ButtonStyles
from geopardie.framework.geopardie_constructs import (PollButtonSession,
                                                      GeopardieSessionResult)
from geopardie.framework.embed_prefabs import geopardie_showcase_start_embed


class GeopardieHandlersMixin:
    
    result_sessions: dict = {}
    
    
    async def handle_gp_vote(self, ctx: InteractionContext):
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
        
        
    async def handle_gp_close(self, ctx: InteractionContext):
        # Check that clicker is author
        if ctx.author.id != int(ctx.custom_id[9:]):
            return await ctx.send("You are not the author of this poll!",
                                  ephemeral=True)

        # Tally votes
        components = ctx.message.components

        # find all option buttons
        option_buttons: list[Button] = []

        for row in components:
            button: Button
            for button in row.components:
                if button.custom_id.startswith("gp_vote"):
                    option_buttons.append(button)

        # Count votes
        sessions = [PollButtonSession.deserialize(
            button.custom_id) for button in option_buttons]
        
        # Construct result session
        result = GeopardieSessionResult(ctx.message.embeds[0].title,
                                        [field.value for field in ctx.message.embeds[0].fields],
                                        [len(session.voted_ids) for session in sessions],
                                        ctx.author)
        
        self.result_sessions[ctx.author.id] = result

        # Disable all buttons
        for row in components:
            button: Button
            for button in row.components:
                button.disabled = True

        # Edit message (without responding to interaction)
        await ctx.message.edit(embed=ctx.message.embeds[0],
                               components=components)
        
        
        # Construct Response
        
        response_embed = geopardie_showcase_start_embed(ctx, result)
        response_buttons = [Button(style=ButtonStyles.PRIMARY,
                                   label="Show Next Answer",
                                   emoji = "⬇️",
                                   custom_id=f"gp_next_{ctx.author.id}")]

        await ctx.send(embed=response_embed, components=response_buttons)


    async def handle_gp_next(self, ctx: InteractionContext):
        # Check that clicker is author
        if ctx.author.id != int(ctx.custom_id[8:]):
            return await ctx.send("You are not the author of this poll!",
                                  ephemeral=True)
            
        await ctx.send(str(self.result_sessions[ctx.author.id]))
        
        
