from naff import (Embed, EmbedAuthor, EmbedField,
                  EmbedFooter, ModalContext, InteractionContext)
from geopardie.framework.geopardie_constructs import GeopardieSessionResult


def geopardie_start_embed(modal_ctx: ModalContext,
                          prompt: str, answers: list[str]):
    # Create an embed from a modal
    embed = Embed(
        title=f"**__POLL__:\n{prompt}**",
        description=("This is an anonymous poll which will be revealed by "
                     f"<@{modal_ctx.author.id}> after voting is complete."),
        author=EmbedAuthor(
            name=modal_ctx.author.display_name,
            icon_url=modal_ctx.author.avatar.url),
        fields=[
            EmbedField(
                name=f"Answer {i+1}",
                value=answer) for i,
            answer in enumerate(answers)],
        footer=EmbedFooter(
            text="Use the buttons to vote/unvote | Total Votes: 0"))

    return embed

def geopardie_showcase_start_embed(ctx: InteractionContext, results: GeopardieSessionResult):
    '''
    Embed to start showcasing a geopardie game
    
    The ctx contains a reference to the original message, including embed
    '''
    embed = Embed(title=results.prompt,
                  author=EmbedAuthor(name=results.author.display_name,
                                     icon_url=results.author.avatar.url),
                  description="Voting has closed, time to reveal the results!")
    
    return embed
    
def geopardie_showcase_next_embed(ctx: InteractionContext, results: GeopardieSessionResult):
    
    idx = results.position
    
    embed = Embed(title=f"{idx+1}) {results.answers[idx]}",
                  description=f"**{results.num_votes[idx]} votes**")
    
    return embed
    