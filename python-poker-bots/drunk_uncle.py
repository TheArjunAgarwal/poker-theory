import random
from pypokerengine.players import BasePokerPlayer


class DrunkUncle(BasePokerPlayer):

    def declare_action(self, valid_actions, hole_card, round_state):
        action = random.choice(valid_actions)

        if action["action"] == "raise":
            min_raise = action["amount"]["min"]
            max_raise = action["amount"]["max"]

            # If raising not allowed
            if min_raise == -1:
                return "call", valid_actions[1]["amount"]

            amount = random.randint(min_raise, max_raise)
            return "raise", amount

        return action["action"], action["amount"]

    # Required overrides
    def receive_game_start_message(self, game_info): pass
    def receive_round_start_message(self, round_count, hole_card, seats): pass
    def receive_street_start_message(self, street, round_state): pass
    def receive_game_update_message(self, action, round_state): pass
    def receive_round_result_message(self, winners, hand_info, round_state): pass
