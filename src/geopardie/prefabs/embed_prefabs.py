from naff import ModalContext, Embed, EmbedFooter, EmbedAuthor, EmbedField


def geopardie_embed(modal_ctx: ModalContext):

    prompt = modal_ctx.responses["modal_prompt"]
    answers = [modal_ctx.responses[f"modal_answer_{i+1}"]
               for i in range(len(modal_ctx.responses) - 1)]

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
            text="Use the buttons to vote/unvote"))

    return embed
