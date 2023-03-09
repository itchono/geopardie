from naff import (Button, InteractionContext, ButtonStyles, Embed,
                  spread_to_rows, EmbedFooter)
from geopardie.framework.geopardie_constructs import (PollButtonSession,
                                                      GeopardieSessionResult)
from geopardie.framework.embed_prefabs import (geopardie_showcase_start_embed,
                                               geopardie_showcase_next_embed)
import struct


class GeopardieHandlersMixin:
    
    result_sessions: dict[tuple[int, int], GeopardieSessionResult] = {}
    
    async def send_geopardie_message(self, ctx: InteractionContext,
                                     number_of_answers: int,
                                     message_embed: Embed):
        buttons = [Button(style=ButtonStyles.PRIMARY,
                          label=f"{i+1}",
                          custom_id=PollButtonSession(i).serialize)
                   for i in range(number_of_answers)]

        close_button = Button(style=ButtonStyles.DANGER,
                              label="Close Voting",
                              custom_id=f"gp_close_{ctx.author.id}",
                              emoji="🗳️")
        bump_button = Button(style=ButtonStyles.SECONDARY,
                             label="Bump post further down",
                             custom_id=f"gp_bump_{ctx.author.id}",
                             emoji="⏬")

        components = spread_to_rows(*(buttons + [close_button, bump_button]))

        await ctx.send(embed=message_embed, components=components)
    
    
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

        total_votes = 0

        # Match position of button in components, and calculate total votes
        for row in msg_components:
            button: Button
            for button in row.components:
                if button.custom_id == ctx.custom_id:
                    # Update button
                    button.custom_id = button_session.serialize

                if button.custom_id.startswith("gp_vote"):
                    total_votes += PollButtonSession.deserialize(button.custom_id).vote_count
                    
        # Edit embed to reflect new vote count
        ctx.message.embeds[0].footer = EmbedFooter(
            text=f"Use the buttons to vote/unvote | Total Votes: {total_votes}")

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
        
    async def handle_gp_bump(self, ctx: InteractionContext):
        # Check that clicker is author
        if ctx.author.id != int(ctx.custom_id[8:]):
            return await ctx.send("You are not the author of this poll!",
                                  ephemeral=True)
            
        num_responses = len(ctx.message.embeds[0].fields)
            
        # Send new message and disable all buttons on the old one
        await self.send_geopardie_message(ctx, num_responses, ctx.message.embeds[0])
        
        
        # Disable all buttons on old message
        for row in ctx.message.components:
            button: Button
            for button in row.components:
                button.disabled = True
                
        await ctx.message.edit(embed=ctx.message.embeds[0],
                               components=ctx.message.components)
        