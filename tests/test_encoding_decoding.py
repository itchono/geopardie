from geopardie.extensions.geopardie_game import PollButtonSession


def test_button_session():
    example_user_id = 1066130535073730631

    # Take only the bottom 16 bits of the user id
    truncated_user_id = example_user_id & 0xFFFF

    session = PollButtonSession(0, [truncated_user_id])
    session2 = PollButtonSession.deserialize(session.serialize)

    assert session.voted_ids == session2.voted_ids
