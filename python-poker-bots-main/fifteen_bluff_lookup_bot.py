import random
from lookup_bot import LookupBot

class FifteenBluffLookupBot(LookupBot):

    BLUFF_FREQUENCY = 0.15  # 15%

    def declare_action(self, valid_actions, hole_card, round_state):

        # Get original LookupBot decision
        action, amount = super().declare_action(
            valid_actions, hole_card, round_state
        )

        # If original action is NOT fold → keep it
        if action != "fold":
            return action, amount

        # If original action IS fold → 15% bluff-call
        if random.random() < self.BLUFF_FREQUENCY:

            call_action = next(
                a for a in valid_actions if a['action'] == 'call'
            )

            call_amount = call_action['amount']

            # If we can call, call instead of folding
            if call_amount is not None:
                return "call", call_amount

        # Otherwise keep fold
        return action, amount