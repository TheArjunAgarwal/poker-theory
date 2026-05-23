from pypokerengine.players import BasePokerPlayer


class AngryUncle(BasePokerPlayer):

    def declare_action(self, valid_actions, hole_card, round_state):

        raise_action = next(a for a in valid_actions if a["action"] == "raise")
        call_action = next(a for a in valid_actions if a["action"] == "call")

        # If raising is allowed
        if raise_action["amount"]["min"] != -1:
            return "raise", raise_action["amount"]["min"]

        # Otherwise always call
        return "call", call_action["amount"]

    def receive_game_start_message(self, game_info): pass
    def receive_round_start_message(self, round_count, hole_card, seats): pass
    def receive_street_start_message(self, street, round_state): pass
    def receive_game_update_message(self, action, round_state): pass
    def receive_round_result_message(self, winners, hand_info, round_state): pass
