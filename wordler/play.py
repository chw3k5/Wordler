import random
from copy import deepcopy
from getpass import getuser
from random import shuffle
from string import ascii_lowercase

from read_words import all_word_list, all_answers, allowed_guesses, all_guesses
from play_engine import determine_test_types
from narrow import allowed_true, allowed_false, allowed_stats, clear_console, AvailableWords
from hint import GetHint
from stats import UserStats


def get_punctuation(number_of_guesses):
    punctuation = ''
    if number_of_guesses == 1:
        punctuation += '?!'
    elif number_of_guesses == 2:
        punctuation += '!!!'
    elif number_of_guesses == 3:
        punctuation += '!!'
    elif number_of_guesses < 7:
        punctuation += '!'
    else:
        punctuation += '.'
    return punctuation


def is_correct_place_letter_text(letter):
    return f"\033[1;30;42m {letter.upper()} \033[0;0m"


def is_used_but_place_is_wrong_text(letter):
    return f"\033[1;30;43m {letter.upper()} \033[0;0m"


def is_not_used_letter_text(letter):
    return f"\033[1;37;40m {letter.upper()} \033[0;0m"


def is_unknown_test(letter):
    return f'\033[1;30;47m {letter.upper()} \033[0;0m'


class Wordle:
    allowed_letters = set(ascii_lowercase)
    allowed_words = deepcopy(all_answers)
    allowed_guesses = deepcopy(allowed_guesses)

    qwerty_order = [['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
                    ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
                    ['z', 'x', 'c', 'v', 'b', 'n', 'm']]
    abc_order = [['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'],
                 ['n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']]
    vowel_order = [['a', 'e', 'i', 'o', 'u', 'y'],
                   ['b', 'c', 'd', 'f', 'g', 'h', 'j'],
                   ['k', 'l', 'm', 'n', 'p', 'q'],
                   ['r', 's', 't', 'v', 'w', 'x', 'z']]

    def __init__(self, console_type='qwerty', first_word=None, hard_mode=False, allow_hint=True, hint_type=None,
                 auto_play=False, bot_mode=False, companions=None):
        # settings
        self.console_type = console_type
        self.first_word = first_word
        self.hard_mode = hard_mode
        self.auto_play = auto_play
        if self.auto_play:
            self.allow_hint = True
        else:
            self.allow_hint = allow_hint
        if hint_type is None:
            self.hint_type = None
        else:
            self.hint_type = hint_type.strip().lower()
        self.bot_mode = bot_mode
        if self.bot_mode:
            if hint_type is None:
                raise ValueError(f'hint_type cannot be None when bot_mode==True.')
            self.username = self.hint_type[0].upper() + self.hint_type[1:]
        else:
            self.username = getuser()
        if companions is None:
            self.companions = None
        else:
            self.companions = []
            for companion_name in companions:
                self.companions.append(Wordle(console_type=self.console_type, first_word=self.first_word,
                                              hard_mode=self.hard_mode, hint_type=companion_name, bot_mode=True))
        # Data that is re-initialized between games
        self.remaining_guesses = None
        self.number_of_guesses = None
        self.share_text = None
        self.display_history = None
        self.unknown = None
        self.known_in_right_place = None
        self.known_in_wrong_place = None
        self.known_wrong = None
        self.letter_counter = None
        self.guessed_words = None
        self.guessed_results = None
        self.word = None
        self.console_str = None
        self.av = None
        self.gh = GetHint(hint_type=self.hint_type, hard_mode=self.hard_mode, bot_mode=bot_mode)
        # stats data, initialized only once
        self.user_stats = UserStats(username=self.username, hard_mode=self.hard_mode)
        self.prior_guesses = self.user_stats.get_prior_guesses()
        # data initialization
        self.games_number = 0
        allowed_words_not_played = self.allowed_words - self.prior_guesses
        if allowed_words_not_played:
            self.available_words = list(allowed_words_not_played)
        else:
            self.available_words = deepcopy(all_word_list)
        shuffle(self.available_words)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.user_stats.write_stats()

    def reset(self):
        self.number_of_guesses = 0
        self.guessed_words = []
        self.guessed_results = []
        self.share_text = ''
        self.display_history = ''

        self.av = AvailableWords(verbose=False)
        self.gh.reset()
        if self.hard_mode:
            self.remaining_guesses = set(self.av.remaining_guesses)
        else:
            self.remaining_guesses = deepcopy(all_guesses)

        self.unknown = deepcopy(self.allowed_letters)
        self.known_in_right_place = set()
        self.known_in_wrong_place = set()
        self.known_wrong = set()
        self.letter_counter = {}

        self.games_number += 1

    def get_word(self, word=None):
        remove_word = True
        if self.games_number == 1 and self.first_word is not None:
            self.word = self.first_word
        elif word is None:
            self.word = self.available_words.pop()
            remove_word = False
        else:
            self.word = word
        self.word = self.word.strip()
        if len(self.word) != 5:
            raise ValueError(f'The user input word must have a length equal to 5, revived {self.word}')
        if remove_word:
            try:
                self.available_words.remove(self.word)
            except ValueError:
                if self.word not in all_answers:
                    # we need to disable hints when a word not from the all_answers set is used.
                    self.allow_hint = False
                    if self.bot_mode:
                        raise ValueError(f'Words like "{self.word}" that are not in the all_answers list cannot be ' +
                                         f'used when bot_mode=True')
        for letter in self.word:
            if letter not in self.letter_counter.keys():
                self.letter_counter[letter] = 0
            self.letter_counter[letter] += 1

    def ask_for_word(self):
        self.number_of_guesses += 1
        guess_word = None
        if self.hard_mode:
            mode_str = '\n(Hard-mode, guess must be possible answer)'
        else:
            mode_str = ''
        while guess_word is None:
            if self.allow_hint:
                if self.hint_type is None:
                    hint_type = random.choice(GetHint.hint_types)
                else:
                    hint_type = self.hint_type
                bot_name = hint_type[0].upper() + hint_type[1:]
                hint_str = f' (type "hint" to get a hint word from {bot_name})'
            else:
                bot_name = 'NoName'
                hint_str = ''
                hint_type = None
            raw_word = input(f"{mode_str}\nEnter guess number: {self.number_of_guesses}{hint_str}\n ")
            test_word = raw_word.strip().lower()
            if self.allow_hint and test_word == 'hint':
                test_word = self.gh.get_hint(av=self.av, guess_words=self.guessed_words,
                                             guess_results=self.guessed_results, hint_type=hint_type)
                if self.auto_play and len(test_word) == 5 and test_word in self.remaining_guesses:
                    guess_word = test_word
                else:
                    print(f"\nThe {bot_name} bot suggests using the word: '{test_word}'")
            elif self.allow_hint and test_word == 'narrow':
                print(self.av)
            elif len(test_word) == 5 and test_word in self.remaining_guesses:
                guess_word = test_word
        return guess_word

    def remove_unknown(self, letter):
        if letter in self.unknown:
            self.unknown.remove(letter)

    def is_correct_place_letter(self, letter):
        self.share_text += is_correct_place_letter_text(letter=' ')
        return is_correct_place_letter_text(letter=letter)

    def is_used_but_place_is_wrong(self, letter):
        self.share_text += is_used_but_place_is_wrong_text(letter=' ')
        return is_used_but_place_is_wrong_text(letter=letter)

    def is_not_used_letter(self, letter):
        self.share_text += is_not_used_letter_text(letter=' ')
        return is_not_used_letter_text(letter=letter)

    def make_letter_text(self, guess_letter, display_type):
        if display_type == '2':
            return self.is_correct_place_letter(letter=guess_letter)
        elif display_type == '1':
            return self.is_used_but_place_is_wrong(letter=guess_letter)
        elif display_type == '0':
            return self.is_not_used_letter(letter=guess_letter)
        else:
            raise KeyError

    def get_console_text(self):
        if self.console_type == 'abc':
            letter_order = self.abc_order
        elif self.console_type == 'vowel':
            letter_order = self.vowel_order
        else:
            letter_order = self.qwerty_order
        console_str = '\n'
        for row_index, letter_row in list(enumerate(letter_order)):
            console_str += ' ' * row_index
            for letter in letter_row:
                if letter in self.known_in_right_place:
                    console_str += is_correct_place_letter_text(letter=letter)
                elif letter in self.known_in_wrong_place:
                    console_str += is_used_but_place_is_wrong_text(letter=letter)
                elif letter in self.known_wrong:
                    console_str += is_not_used_letter_text(letter=letter)
                elif letter in self.unknown:
                    console_str += is_unknown_test(letter)
                else:
                    raise KeyError(f'letter: {letter}, not available.')
            console_str += '\n'
        self.console_str = console_str
        return console_str

    def determine_test_types(self, guess_word):
        index_to_guess_letter_and_display_type, correct_guess_letters, wrong_place_letters, \
        used_too_many_times_letters = \
            determine_test_types(guess_word=guess_word, solution_word=self.word)
        # correct letter data
        for correct_guess_letter in correct_guess_letters:
            self.remove_unknown(letter=correct_guess_letter)
            if correct_guess_letter in self.known_in_wrong_place:
                self.known_in_wrong_place.remove(correct_guess_letter)
            self.known_in_right_place.add(correct_guess_letter)
        # wrong_place letters
        for wrong_place_letter in wrong_place_letters:
            self.remove_unknown(letter=wrong_place_letter)
            if wrong_place_letter not in self.known_in_right_place:
                # this is not a double letter that is unused, but a letter that is in the word in different place
                self.known_in_wrong_place.add(wrong_place_letter)
        # letters use too mny times.
        for used_too_many_times_letter in used_too_many_times_letters:
            self.remove_unknown(letter=used_too_many_times_letter)
            if used_too_many_times_letter not in self.known_in_right_place and \
                    used_too_many_times_letter not in self.known_in_wrong_place:
                # this is not a double letter that is unused, but a letter the is not used at all
                self.known_wrong.add(used_too_many_times_letter)
        return index_to_guess_letter_and_display_type

    def print_display(self, guess_word):
        text_str = ''
        index_to_guess_letter_and_display_type = self.determine_test_types(guess_word)
        guess_results = ''
        for guess_index in sorted(index_to_guess_letter_and_display_type.keys()):
            guess_letter, display_type = index_to_guess_letter_and_display_type[guess_index]
            text_str += self.make_letter_text(guess_letter=guess_letter, display_type=display_type)
            guess_results += display_type
        # record the results 
        self.guessed_words.append(guess_word)
        self.guessed_results.append(guess_results)
        # update the allowed guesses
        self.av.add_guess(guess_word=guess_word, guess_results=guess_results)
        if not self.hard_mode:
            self.remaining_guesses.remove(guess_word)
        else:
            self.remaining_guesses = set(self.av.remaining_guesses)

        self.get_console_text()
        self.display_history += text_str + '\n'
        self.share_text += '\n'
        # the display statements
        if not self.bot_mode:
            clear_console()
            print(self.console_str)
            print(self.display_history)

    def play(self, word=None):
        self.reset()
        self.get_word(word=word)
        guess_word = None
        while guess_word != self.word:
            if self.bot_mode:
                guess_word = self.bot_turn()
            else:
                guess_word = self.ask_for_word()
            self.print_display(guess_word=guess_word)

        punctuation = get_punctuation(number_of_guesses=self.number_of_guesses)
        if self.bot_mode:
            print(self.console_str)
            print(self.display_history)
            name_str = f'The bot, {self.username},'
        else:
            name_str = f'{self.username}'
        self.user_stats.add_game(solution_word=self.word, guesses=self.guessed_words,
                                 guess_results=self.guessed_results)
        print(f'\n\n{name_str} solved the puzzle in {self.number_of_guesses} guesses{punctuation}\n')
        print(self.share_text)

    def bot_turn(self):
        return self.gh.__getattribute__(self.hint_type)()


def play(console_type='qwerty', first_word=None, hard_mode=False, allow_hint=True, hint_type=None, auto_play=False,
         bot_mode=False):
    clear_console()
    if bot_mode and hint_type is None:
        hint_type = random.choice(GetHint.hint_types)
    with Wordle(console_type=console_type, first_word=first_word, hard_mode=hard_mode, allow_hint=allow_hint,
                hint_type=hint_type, auto_play=auto_play, bot_mode=bot_mode) as w:
        play_again = True
        while play_again:
            w.play()
            ess = 's'
            if w.games_number < 2:
                ess = ''
            play_again = None
            while play_again is None:
                print(f'\n  Statistics on {len(w.user_stats)} games')
                print(f'  {w.games_number} game{ess} played this session')
                print(f'  {len(w.available_words)} words remain')
                print('\nDo you want to play again with a new word? [y,n]')
                raw_play_again = input('            or see your statistics so far? [s]:\n ')
                user_response = raw_play_again.strip().lower()
                if user_response in allowed_true:
                    play_again = True
                elif user_response in allowed_false:
                    play_again = False
                elif user_response in allowed_stats:
                    w.user_stats.get_histogram_str(verbose=True)


if __name__ == '__main__':
    hint_types_str = ''
    for hint_type_index, hint_type in list(enumerate(GetHint.hint_types)):
        if hint_type_index == len(GetHint.hint_types) - 1:
            concat_str = ''
        elif hint_type_index == len(GetHint.hint_types) - 2:
            concat_str = ', and '
        else:
            concat_str = ', '
        hint_types_str += f'{hint_type[0].upper() + hint_type[1:]}{concat_str}'
    import argparse

    # set up the parser for this Script
    parser = argparse.ArgumentParser(description='Parser for play.py, a Wordle Emulator.')
    parser.add_argument('word', type=str, default=None, nargs='?',
                        help="An specify the first word that is used as the game's solution. Good to demonstrates " +
                             "an specific word or to debug and test.")
    parser.add_argument('--abc', dest='abc', action='store_true',
                        help="Turns on an 'ABCDEF...' letter console for keeping track of used letters. " +
                             "The default is --no-abc which displays a qwerty letter console.")
    parser.add_argument('--no-abc', dest='abc', action='store_false', default=True,
                        help="Turns off an 'ABCDEF...' letter console for and uses the default qwerty console " +
                             "for keeping track of used letters. ")
    parser.add_argument('--vowel', dest='vowel', action='store_true',
                        help="Turns on an 'AEIOUYBCDF...' letter console for keeping track of used letters. " +
                             "The default is --no-vowel which displays a qwerty letter console.")
    parser.add_argument('--no-vowel', dest='vowel', action='store_false', default=True,
                        help="Turns off an 'AEIOUYBCDF...' letter console for and uses the default qwerty console " +
                             "for keeping track of used letters. ")
    parser.add_argument('--hard', dest='hard', action='store_true',
                        help="Turns on Wordle Hard-mode. Hard mode restricts the allowed guessed to solve the puzzle." +
                             "Guesses in Hard mode must be possible solutions to the puzzle. The default is " +
                             "--no-hard with all allowed guesses can be used to narrow the field of remaining letters.")
    parser.add_argument('--no-hard', dest='hard', action='store_false', default=False,
                        help="Turns off Wordle Hard-mode. Hard mode restricts the allowed guessed to solve the " +
                             "puzzle. This setting is the default in witch all allowed guesses can be used to narrow " +
                             "the field of remaining letters.")
    parser.add_argument('--hint', dest='hint', action='store_true',
                        help="Allows a hint to be available during game play. Type the word 'hint' instead of a five " +
                             "letter guess activate this feature, this lets the game choose a possible answer or " +
                             "allowed guess as a suggestion. By default, no hints are allowed.")
    parser.add_argument('--no-hint', dest='hint', action='store_false', default=False,
                        help="Disables a hint to be available during game play. Typing the word 'hint' has no effect " +
                             "when the --no-hint augment is given. By default, no hints are allowed.")
    parser.add_argument('--bot', dest='bot_mode', action='store_true',
                        help="Replace the human player with a bot that plays the game. The bot is " +
                             "selected at random or can be chosen with by specifying a 'Name' using the setting " +
                             "--hint-type Name argument. The default is --no-bot were a humand player enter guesses " +
                             "and solves the puzzle.")
    parser.add_argument('--no-bot', dest='bot_mode', action='store_false', default=False,
                        help="This is the default, a user enter guesses to solve the puzzle. The human play can " +
                             "can still receive hints from the bot if --hint is set.")
    parser.add_argument('--auto-play', dest='auto_play', action='store_true',
                        help="When using 'hint' during a game, auto-plays the suggestion from a bot. The default is " +
                             "--no-autoplay. This is good for watching bot behavior.")
    parser.add_argument('--no-auto-play', dest='bot_mode', action='store_false', default=False,
                        help="This is the default, using the 'hint' during a game returns a suggestion from the bot " +
                             "that is printed to the screen. This suggestions can be used or not.")
    parser.add_argument('--hint-type', dest='hint_type', metavar='Name', nargs=1, default=None, type=str,
                        help=f'Specify a Hint personally. {len(GetHint.hint_types)} hint types are available: ' +
                             f'{hint_types_str}.\n' +
                             f'Caleb wants to guess the right answer in the next turn. Tries to eliminate unused ' +
                             f'letters but will not sacrifice a possible right answer in the next guess. Plays the ' +
                             f'the same way on regular or hard-mode. Goes big and risks it all to win. ' +
                             f'Natalie narrows the field of letters by seeking out the remaining vowels, the ' +
                             f'heart of the word. Natalie uses words that are allowed guesses, a bigger set of words ' +
                             f'then the just the allowed solutions that Caleb uses. Once all the vowels are accounted ' +
                             f'for, Natalie uses Jada\'s strategy ' +
                             f'Jada delivers hints that eliminate the unknown letters of that are the most common to ' +
                             f'remaining allowed guesses, trying to narrow the possible remaining answer words as ' +
                             f'quickly as possible, until only one or two possible solutions remain and then those ' +
                             f'are the hints returned. Jada and Natalie both know how ' +
                             f'to follow the rules in the more restrictive hard mode.')
    args = parser.parse_args()
    if args.hint_type is None:
        hint_name = None
    else:
        hint_name = args.hint_type[0]
    if args.abc:
        console_type = 'abc'
    elif args.vowel:
        console_type = 'vowel'
    else:
        console_type = 'qwerty'
    # run the game script
    play(console_type=console_type, first_word=args.word, hard_mode=args.hard, allow_hint=args.hint,
         hint_type=hint_name, auto_play=args.auto_play, bot_mode=args.bot_mode)
