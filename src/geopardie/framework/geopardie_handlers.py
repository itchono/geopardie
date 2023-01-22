from naff import Button, InteractionContext, ButtonStyles
from geopardie.framework.geopardie_constructs import (PollButtonSession,
                                                      GeopardieSessionResult)
from geopardie.framework.embed_prefabs import (geopardie_showcase_start_embed,
                                               geopardie_showcase_next_embed)


class GeopardieHandlersMixin:
    
    result_sessions: dict[tuple[int, int], GeopardieSessionResult] = {}
    
    
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
        
        self.result_sessions[(ctx.author.id, ctx.message.id)] = result

        # Disable all buttons
        for row in components:
            button: Button
            for button in row.components:
                button.disabled = True

        # Edit message (without responding to interaction)
        await ctx.message.edit(embed=ctx.message.embeds[0],
                               components=components)
        
        
        # Construct Response
        # Encode state using author id and message id
        hex_enc_author_id = hex(ctx.author.id)[2:]
        hex_enc_message_id = hex(ctx.message.id)[2:]
        
        response_embed = geopardie_showcase_start_embed(ctx, result)
        response_buttons = [Button(style=ButtonStyles.PRIMARY,
                                   label="Show Next Answer",
                                   emoji = "⬇️",
                                   custom_id=f"gp_next_{hex_enc_author_id}_{hex_enc_message_id}")]

        await ctx.send(embed=response_embed, components=response_buttons)


    async def handle_gp_next(self, ctx: InteractionContext):
        
        author_id_hex, message_id_hex = ctx.custom_id[8:].split("_")
        author_id = int(author_id_hex, 16)
        message_id = int(message_id_hex, 16)
        
        # Check that clicker is author
        if ctx.author.id != author_id:
            return await ctx.send("You are not the author of this poll!",
                                  ephemeral=True)
            
        # Disable button
        for row in ctx.message.components:
            button: Button
            for button in row.components:
                button.disabled = True
                
        # Edit message (without responding to interaction)
        await ctx.message.edit(embed=ctx.message.embeds[0],
                               components=ctx.message.components)
                
        # Handle stale buttons
        if (author_id, message_id) not in self.result_sessions:
            return await ctx.send("This poll has been closed for too long!",
                                  ephemeral=True)
            
        session = self.result_sessions[(author_id, message_id)]
        
        response_embed = geopardie_showcase_next_embed(ctx, session)
        
        if session.position < len(session.answers) - 1:
            # Construct Response
            
            response_buttons = [Button(style=ButtonStyles.PRIMARY,
                                       label="Show Next Answer",
                                       emoji = "⬇️",
                                       custom_id=f"gp_next_{author_id_hex}_{message_id_hex}")]
            await ctx.send(embed=response_embed, components=response_buttons)
        else:
            await ctx.send(embed=response_embed)
        
        # Advance session
        session.position += 1
