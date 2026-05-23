import random
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate

# ============================================================
# Canonical Hand Representation (169 classes)
# ============================================================

RANK_MAP = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7,
    "8": 8, "9": 9, "T": 10, "J": 11,
    "Q": 12, "K": 13, "A": 14
}


def canonical_key(hole_card):
    # PyPokerEngine format is "SA", "DT", etc.
    r1 = RANK_MAP[hole_card[0][1]]
    r2 = RANK_MAP[hole_card[1][1]]

    s1 = hole_card[0][0]
    s2 = hole_card[1][0]

    hi, lo = max(r1, r2), min(r1, r2)
    suited = (s1 == s2)

    if hi == lo:
        suited = False  # pairs ignore suit

    return (hi, lo, suited)


# ============================================================
# Preflop Ranges
# ============================================================

def build_utg_range():
    pairs = {(r, r, False) for r in [14,13,12,11,10,9,8,7]}
    suited = {
        (14,13,True),(14,12,True),(14,11,True),(14,10,True),
        (13,12,True),(13,11,True),(12,11,True),(11,10,True),(10,9,True)
    }
    offsuit = {
        (14,13,False),(14,12,False),(14,11,False)
    }
    return pairs | suited | offsuit


def build_co_range():
    R = build_utg_range()
    extra_pairs = {(6,6,False),(5,5,False)}
    extra_suited = {
        (9,8,True),(8,7,True),(7,6,True),
        (14,9,True),(14,8,True)
    }
    return R | extra_pairs | extra_suited


def build_btn_range():
    R = build_co_range()
    extra_pairs = {(4,4,False),(3,3,False),(2,2,False)}
    extra_suited = {
        (6,5,True),(5,4,True),(4,3,True),
        (13,9,True),(12,9,True)
    }
    extra_offsuit = {
        (14,10,False),(13,12,False)
    }
    return R | extra_pairs | extra_suited | extra_offsuit


def build_sb_range():
    return build_btn_range()


OPENING_RANGES = {
    "UTG": build_utg_range(),
    "CO": build_co_range(),
    "BTN": build_btn_range(),
    "SB": build_sb_range()
}

PREMIUM = {
    (14,14,False),
    (13,13,False),
    (12,12,False),
    (14,13,True)
}


# ============================================================
# LookupBot
# ============================================================

class LookupBot(BasePokerPlayer):

    SIMULATIONS = 8000
    RAISE_THRESHOLD = 0.60

    # --------------------------------------------------------
    # Position detection
    # --------------------------------------------------------

    def get_position(self, round_state):
        seats = round_state['seats']
        dealer_btn = round_state['dealer_btn']
        my_index = next(i for i, s in enumerate(seats)
                        if s['uuid'] == self.uuid)

        relative = (my_index - dealer_btn) % len(seats)

        if relative == 0:
            return "BTN"
        elif relative == 1:
            return "SB"
        elif relative == 2:
            return "BB"
        elif relative == 3:
            return "UTG"
        else:
            return "CO"

    # --------------------------------------------------------
    # Monte Carlo Postflop Equity
    # --------------------------------------------------------

    def estimate_equity(self, hole_card, community_card, nb_players):
        return estimate_hole_card_win_rate(
            nb_simulation=self.SIMULATIONS,
            nb_player=nb_players,
            hole_card=gen_cards(hole_card),
            community_card=gen_cards(community_card)
        )

    def calculate_pot_odds(self, call_amount, pot):
        if call_amount == 0:
            return 0
        return call_amount / float(pot + call_amount)

    # --------------------------------------------------------
    # Main Decision Engine
    # --------------------------------------------------------

    def declare_action(self, valid_actions, hole_card, round_state):

        street = round_state['street']
        pot = round_state['pot']['main']['amount']
        nb_players = len(round_state['seats'])

        call_action = next(a for a in valid_actions if a['action'] == 'call')
        call_amount = call_action['amount']

        raise_action = next(a for a in valid_actions if a['action'] == 'raise')

        # ====================================================
        # PREFLOP LOOKUP ENGINE
        # ====================================================

        if street == "preflop":

            position = self.get_position(round_state)
            key = canonical_key(hole_card)
            my_range = OPENING_RANGES.get(position, set())

            facing_raise = call_amount > 0

            # OPENING
            if not facing_raise:
                if key in my_range and raise_action['amount']['min'] != -1:
                    return "raise", raise_action['amount']['min']
                return "fold", 0

            # FACING RAISE
            else:
                if key in PREMIUM and raise_action['amount']['min'] != -1:
                    return "raise", raise_action['amount']['min'] * 3

                if key in my_range:
                    return "call", call_amount

                return "fold", 0

        # ====================================================
        # POSTFLOP MATH ENGINE
        # ====================================================

        community_card = round_state['community_card']

        equity = self.estimate_equity(hole_card, community_card, nb_players)
        pot_odds = self.calculate_pot_odds(call_amount, pot)

        if equity >= pot_odds:

            if equity >= self.RAISE_THRESHOLD and raise_action['amount']['min'] != -1:
                min_raise = raise_action['amount']['min']
                max_raise = raise_action['amount']['max']

                raise_amount = int(pot * equity)
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