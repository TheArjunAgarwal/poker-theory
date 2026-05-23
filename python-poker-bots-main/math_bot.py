import random
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
from pypokerengine.utils.card_utils import _pick_unused_card
from pypokerengine.engine.hand_evaluator import HandEvaluator


class MathBot(BasePokerPlayer):

    SIMULATIONS = 10000
    RAISE_THRESHOLD = 0.61

    def estimate_equity(self, hole_card, community_card, nb_players):
        """
        Monte Carlo equity estimation
        """
        win_rate = estimate_hole_card_win_rate(
            nb_simulation=self.SIMULATIONS,
            nb_player=nb_players,
            hole_card=gen_cards(hole_card),
            community_card=gen_cards(community_card)
        )
        return win_rate

    def calculate_pot_odds(self, call_amount, pot):
        if call_amount == 0:
            return 0
        return call_amount / float(pot + call_amount)

    def declare_action(self, valid_actions, hole_card, round_state):

        community_card = round_state['community_card']
        pot = round_state['pot']['main']['amount']
        nb_players = len(round_state['seats'])

        # Extract call info
        call_action = next(a for a in valid_actions if a['action'] == 'call')
        call_amount = call_action['amount']

        raise_action = next(a for a in valid_actions if a['action'] == 'raise')

        # Estimate equity
        equity = self.estimate_equity(hole_card, community_card, nb_players)

        # Compute pot odds
        pot_odds = self.calculate_pot_odds(call_amount, pot)

        # Decision logic
        if equity >= pot_odds:

            # Raise if strong enough
            if equity >= self.RAISE_THRESHOLD and raise_action['amount']['min'] != -1:
                min_raise = raise_action['amount']['min']
                max_raise = raise_action['amount']['max']

                # Simple proportional raise sizing
                raise_amount = int(pot * equity)

                # Clamp to legal range
                raise_amount = max(min_raise, min(raise_amount, max_raise))

                return "raise", raise_amount

            return "call", call_amount

        return "fold", 0


    # Required abstract methods
    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass
