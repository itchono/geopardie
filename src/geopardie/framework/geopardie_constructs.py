import base64
import struct
from dataclasses import dataclass, field
from naff import User

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

@dataclass
class GeopardieSessionResult:
    prompt: str
    answers: list[str]
    num_votes: list[int]
    author: User
    position: int = 0
    
    def __len__(self):
        return len(self.answers)

