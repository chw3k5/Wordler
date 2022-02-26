from play import Wordle
from hint import GetHint


def bot_run(bot_name, hard_mode=False):
    with Wordle(hard_mode=hard_mode, hint_type=bot_name, bot_mode=True) as w:
        while w.available_words:
            w.play()


def run_all_bots(hard_mode=False):
    for bot_name in list(GetHint.hint_types):
        bot_run(bot_name, hard_mode=hard_mode)


if __name__ == '__main__':
    run_all_bots(hard_mode=False)
    run_all_bots(hard_mode=True)
