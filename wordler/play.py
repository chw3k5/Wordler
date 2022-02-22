import random
from copy import copy
from random import shuffle
from string import ascii_lowercase

from read_words import all_word_list, all_answers, allowed_guesses, all_guesses
from narrow import allowed_true, clear_console, AvailableWords
from hint import GetHint


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
    return f'\033[1;30;42m {letter.upper()} \033[0;0m'


def is_used_but_place_is_wrong_text(letter):
    return f'\033[1;30;43m {letter.upper()} \033[0;0m'


def is_not_used_letter_text(letter):
    return f'\033[1;37;40m {letter.upper()} \033[0;0m'


def is_unknown_test(letter):
    return f'\033[1;30;47m {letter.upper()} \033[0;0m'


class Wordle:
    allowed_letters = set(ascii_lowercase)
    allowed_words = copy(all_answers)
    allowed_guesses = copy(allowed_guesses)

    qwerty_order = [['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
                    ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
                    ['z', 'x', 'c', 'v', 'b', 'n', 'm']]
    abc_order = [['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'],
                 ['n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']]

    def __init__(self, qwerty_console=True, first_word=None, hard_mode=False, allow_hint=True):
        # settings
        self.qwerty_console = qwerty_console
        self.first_word = first_word
        self.hard_mode = hard_mode
        self.allow_hint = allow_hint
        # data initialization
        self.available_words = all_word_list
        shuffle(self.available_words)
        self.games_number = 0
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
        self.av = None

    def reset(self):
        self.number_of_guesses = 0
        self.guessed_words = []
        self.guessed_results = []
        self.share_text = ''
        self.display_history = ''
        if self.hard_mode:
            self.av = AvailableWords(verbose=False)
        self.remaining_guesses = copy(self.allowed_guesses)

        self.unknown = copy(self.allowed_letters)
        self.known_in_right_place = set()
        self.known_in_wrong_place = set()
        self.known_wrong = set()
        self.letter_counter = {}

        self.games_number += 1

    def get_word(self, word=None):
        if self.games_number == 1 and self.first_word is not None:
            self.word = self.first_word
        elif word is None:
            self.word = self.available_words.pop()
        else:
            self.word = word
        try:
            self.available_words.remove(word)
        except ValueError:
            pass
        self.word = self.word.strip()
        if len(self.word) != 5:
            raise ValueError(f'The user input word must have a length equal to 5, revived {self.word}')
        for letter in self.word:
            if letter not in self.letter_counter.keys():
                self.letter_counter[letter] = 0
            self.letter_counter[letter] += 1

    def ask_for_word(self):
        guess_word = None
        self.number_of_guesses += 1
        if self.hard_mode:
            mode_str = '\n(Hard-mode, guess must be possible answer)'
        else:
            mode_str = ''
        while guess_word is None:
            if self.allow_hint:
                hint_type = random.choice(GetHint.hint_types)
                hint_str = f' (type "hint" to get a hint word from {hint_type[0].upper() + hint_type[1:]})'
            else:
                hint_str = ''
                hint_type=None
            raw_word = input(f"{mode_str}\nEnter guess number: {self.number_of_guesses}{hint_str}\n ")
            test_word = raw_word.strip().lower()
            if self.allow_hint and test_word == 'hint':
                get_hint = GetHint(hint_type=hint_type, hard_mode=self.hard_mode)
                test_word = get_hint.get_hint(guess_words=self.guessed_words, guess_results=self.guessed_results)
            if len(test_word) == 5 and test_word in self.remaining_guesses:
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
        if self.qwerty_console:
            letter_order = self.qwerty_order
        else:
            letter_order = self.abc_order
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
        return console_str

    def determine_test_types(self, guess_word):
        index_to_guess_letter_and_display_type = {}
        remaining_word_indexes = list(range(len(guess_word)))
        remaining_word_letters = list(self.word)
        for correct_index in list(remaining_word_indexes):
            guess_letter = guess_word[correct_index]
            word_letter = self.word[correct_index]
            if word_letter == guess_letter:
                index_to_guess_letter_and_display_type[correct_index] = (guess_letter, '2')
                self.remove_unknown(letter=guess_letter)
                if guess_letter in self.known_in_wrong_place:
                    self.known_in_wrong_place.remove(guess_letter)
                self.known_in_right_place.add(guess_letter)
                remaining_word_indexes.remove(correct_index)
                remaining_word_letters.remove(guess_letter)

        for is_used_index in list(remaining_word_indexes):
            guess_letter = guess_word[is_used_index]
            if guess_letter in remaining_word_letters:
                index_to_guess_letter_and_display_type[is_used_index] = (guess_letter, '1')
                self.remove_unknown(letter=guess_letter)
                if guess_letter not in self.known_in_right_place:
                    # this is not a double letter that is unused, but a letter that is in the word in different place
                    self.known_in_wrong_place.add(guess_letter)
                remaining_word_indexes.remove(is_used_index)
                remaining_word_letters.remove(guess_letter)

        for is_used_index in list(remaining_word_indexes):
            guess_letter = guess_word[is_used_index]
            index_to_guess_letter_and_display_type[is_used_index] = (guess_letter, '0')
            self.remove_unknown(letter=guess_letter)
            if guess_letter not in self.known_in_right_place and guess_letter not in self.known_in_wrong_place:
                # this is not a double letter that is unused, but a letter the is not used at all
                self.known_wrong.add(guess_letter)
            remaining_word_indexes.remove(is_used_index)
        if len(remaining_word_indexes) != 0:
            raise TypeError
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
        if self.hard_mode:
            self.av.add_guess(guess_word=guess_word, guess_results=guess_results)
            self.remaining_guesses = set(self.av.remaining_guesses)
        else:
            self.remaining_guesses.remove(guess_word)

        console_str = self.get_console_text()
        self.display_history += text_str + '\n'
        self.share_text += '\n'
        # the display statements
        clear_console()
        print(console_str)
        print(self.display_history)

    def play(self, word=None):
        self.reset()
        self.get_word(word=word)
        guess_word = None
        while guess_word != self.word:
            guess_word = self.ask_for_word()
            self.print_display(guess_word=guess_word)

        punctuation = get_punctuation(number_of_guesses=self.number_of_guesses)
        print(f'\n\nCompleted in {self.number_of_guesses} guesses{punctuation}\n')
        print(self.share_text)


def play(qwerty_console=True, first_word=None, hard_mode=False, allow_hint=True):
    clear_console()
    w = Wordle(qwerty_console=qwerty_console, first_word=first_word, hard_mode=hard_mode, allow_hint=allow_hint)
    play_again = True
    while play_again:
        w.play()
        ess = 's'
        if w.games_number < 2:
            ess = ''
        print(f'{w.games_number} game{ess} played, {len(w.available_words)} words remain.')
        raw_play_again = input('\nDo you want to play again with a new word? [y,n]:\n ')
        if raw_play_again.strip().lower() in allowed_true:
            play_again = True
        else:
            play_again = False


if __name__ == '__main__':
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
    parser.add_argument('--hard', dest='hard', action='store_true',
                        help="Turns on Wordle Hard-mode. Hard mode restricts the allowed guessed to solve the puzzle." +
                             "Guesses in Hard mode must be possible solutions to the puzzle. The default is " +
                             "--no-hard with all allowed guesses can be used to narrow the field of remaining letters.")
    parser.add_argument('--no-hard', dest='hard', action='store_false', default=False,
                        help="Turns off Wordle Hard-mode. Hard mode restricts the allowed guessed to solve the " +
                             "puzzle. This setting is the default in witch all allowed guesses can be used to narrow " +
                             "the field of remaining letters.")
    parser.add_argument('--hint', dest='hint', action='store_true', default=True,
                        help="Allows a hint to be available during game play. Type the word 'hint' instead of a five " +
                              "letter guess activate this feature, this lets the game choose a possible answer or " +
                              "allowed guess for you. The game can play itself by repeating using 'hint'. Default " +
                              "is that hints are allowed."
                        )
    parser.add_argument('--no-hint', dest='hint', action='store_false',
                        help="Disables a hint to be available during game play. Typing the word 'hint' has no effect " +
                              "when the --no-hint augmnet is given. By default, hints are allowed." +
                              "is that hints are allowed.")
    args = parser.parse_args()
    # run the game script
    play(qwerty_console=not args.abc, first_word=args.word, hard_mode=args.hard, allow_hint=args.hint)
