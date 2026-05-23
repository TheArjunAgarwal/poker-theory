from pypokerengine.players import BasePokerPlayer


class SadUncle(BasePokerPlayer):

    def declare_action(self, valid_actions, hole_card, round_state):

        call_action = next(a for a in valid_actions if a["action"] == "call")

        # If we can check (call amount == 0)
        if call_action["amount"] == 0:
            return "call", 0

        # Otherwise fold
        return "fold", 0

    def receive_game_start_message(self, game_info): pass
    def receive_round_start_message(self, round_count, hole_card, seats): pass
    def receive_street_start_message(self, street, round_state): pass
    def receive_game_update_message(self, action, round_state): pass
    def receive_round_result_message(self, winners, hand_info, round_state): pass
