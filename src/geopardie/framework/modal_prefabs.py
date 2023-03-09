# Prefabs for Discord Modals (Popups)
from naff import Modal, ParagraphText, ShortText



'''
Modals for starting a geopardie game:
1. Prompt + 1-4 Text
2. Up to 5 Text

N prompts will be split into type 1 and type 2 modals
'''

def geopardie_modal_type_1(number_of_answers: int) -> Modal:
    '''
    Returns a Modal with the following fields:
    - Prompt input (long text)
    - Up to 4 answer inputs (short text)
    
    This is the FIRST modal returned in a series of modals (potentially)
    '''
    
    if number_of_answers > 4:
        raise ValueError("Number of answers must be <= 4")
    
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
                placeholder=f"Enter answer {i+1}") for i in range(number_of_answers)])
    
def geopardie_modal_type_2(number_of_answers: int, modal_number: int=2) -> Modal:
    '''
    This is a "followup" modal to the first modal.
    
    It returns a Modal with the following fields:
    - up to 5 answer inputs (short text)
    
    It accepts a "modal_number" parameter, which is used to
    identify the modal in the series of modals.
    '''
    if number_of_answers > 5:
        raise ValueError("Number of answers must be <= 5")
    
    offset = 4 + (modal_number - 2) * 5 # e.g. modal 2 -> 4, modal 3 -> 9, etc.
    
    return Modal(
        "Create an Anonymous Poll",
        components=[
            ShortText(
                label=f"Answer {i+1+offset}",
                custom_id=f"modal_answer_{i+1+offset}",
                placeholder=f"Enter answer {i+1+offset}") for i in range(number_of_answers)])
    

def get_geopardie_modals(total_number_of_answers: int) -> list[Modal]:
    '''
    Returns a sequence of modals depending on the number of answers needed.
    '''
    
    if total_number_of_answers < 5:
        return [geopardie_modal_type_1(total_number_of_answers)]
    else:
        modals = [geopardie_modal_type_1(4)]
        
        remaining_answers = total_number_of_answers - 4
        
        while remaining_answers > 0:
            if remaining_answers >= 5:
                modals.append(geopardie_modal_type_2(5, len(modals) + 1))
                remaining_answers -= 5
            else:
                modals.append(geopardie_modal_type_2(remaining_answers, len(modals) + 1))
                remaining_answers = 0
                
        return modals
