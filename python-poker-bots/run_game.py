from pypokerengine.api.game import setup_config, start_poker

# Import your bots
from math_bot import MathBot
from drunk_uncle import DrunkUncle
from angry_uncle import AngryUncle
from sad_uncle import SadUncle
from lookup_bot import LookupBot
from fifteen_bluff_lookup_bot import FifteenBluffLookupBot


def main():
    config = setup_config(
        max_round=50,
        initial_stack=1000,
        small_blind_amount=10
    )

    config.register_player(name="fifteenblufflookupbot", algorithm=FifteenBluffLookupBot())
    config.register_player(name="LookupBot", algorithm=(LookupBot()))


    game_result = start_poker(config, verbose=1)
    print(game_result)


if __name__ == "__main__":
    main()
