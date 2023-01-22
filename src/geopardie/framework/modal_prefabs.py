# Prefabs for Discord Modals (Popups)
from naff import Modal, ParagraphText, ShortText


def geopardie_modal(number_of_answers: int):
    return Modal(
        "Create an Anonymous Poll",
        components=[
            ParagraphText(
                label="Prompt",
                custom_id="modal_prompt",
                placeholder="Enter the prompt for the poll")] + [
            ShortText(
                label=f"Answer {i+1}",
                custom_id=f"modal_answer_{i+1}",
                placeholder=f"Enter answer {i+1}") for i in range(number_of_answers)],
        custom_id="geopardie_modal")
