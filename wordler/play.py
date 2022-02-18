from copy import copy
from random import shuffle
from string import ascii_lowercase
from read_words import words_into_list
from narrow import allowed_true, allowed_guesses, clear_console


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
    allowed_words = set(words_into_list())
    allowed_guesses = allowed_guesses
    qwerty_order = [['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
                    ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
                    ['z', 'x', 'c', 'v', 'b', 'n', 'm']]
    abc_order = [['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'],
                 ['n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']]

    def __init__(self, qwerty_console=True):
        self.qwerty_console = qwerty_console
        self.available_words = list(self.allowed_words)
        shuffle(self.available_words)

        self.remaining_guesses = None
        self.number_of_guesses = None
        self.share_text = None
        self.display_history = None
        self.unknown = None
        self.known_in_right_place = None
        self.known_in_wrong_place = None
        self.known_wrong = None

    def reset(self):
        self.number_of_guesses = 0
        self.share_text = ''
        self.display_history = ''
        self.remaining_guesses = copy(self.allowed_guesses)
        self.unknown = copy(self.allowed_letters)
        self.known_in_right_place = set()
        self.known_in_wrong_place = set()
        self.known_wrong = set()

    def get_word(self, word=None):
        if word is None:
            word = self.available_words.pop()
        elif word in self.available_words:
            self.available_words.remove(word)
        else:
            raise KeyError(f'The word {word} is not an allowed word.')
        return word

    def ask_for_word(self):
        guess_word = None
        self.number_of_guesses += 1
        while guess_word is None:
            raw_word = input(f"\nEnter guess number: {self.number_of_guesses}\n ")
            test_word = raw_word.strip().lower()
            if len(test_word) == 5 and test_word in self.remaining_guesses:
                guess_word = test_word
        self.remaining_guesses.remove(guess_word)
        return guess_word

    def remove_unknown(self, letter):
        if letter in self.unknown:
            self.unknown.remove(letter)

    def is_correct_place_letter(self, letter):
        self.remove_unknown(letter=letter)
        if letter in self.known_in_wrong_place:
            self.known_in_wrong_place.remove(letter)
        self.known_in_right_place.add(letter)
        self.share_text += is_correct_place_letter_text(letter=' ')
        return is_correct_place_letter_text(letter=letter)

    def is_used_but_place_is_wrong(self, letter):
        self.remove_unknown(letter=letter)
        self.known_in_wrong_place.add(letter)
        self.share_text += is_used_but_place_is_wrong_text(letter=' ')
        return is_used_but_place_is_wrong_text(letter=letter)

    def is_not_used_letter(self, letter):
        self.remove_unknown(letter=letter)
        self.known_wrong.add(letter)
        self.share_text += is_not_used_letter_text(letter=' ')
        return is_not_used_letter_text(letter=letter)

    def make_letter_text(self, word, guess_letter, guess_index):
        if guess_letter in word:
            if guess_letter == word[guess_index]:
                return self.is_correct_place_letter(letter=guess_letter)
            else:
                return self.is_used_but_place_is_wrong(letter=guess_letter)
        else:
            return self.is_not_used_letter(letter=guess_letter)

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

    def print_display(self, word, guess_word):
        text_str = ''
        for guess_index, guess_letter in list(enumerate(guess_word)):
            text_str += self.make_letter_text(word=word, guess_letter=guess_letter, guess_index=guess_index)
        console_str = self.get_console_text()
        self.display_history += text_str + '\n'
        self.share_text += '\n'
        # the display statements
        clear_console()
        print(console_str)
        print(self.display_history)

    def play(self, word=None):
        self.reset()
        word = self.get_word(word=word)
        guess_word = None
        while guess_word != word:
            guess_word = self.ask_for_word()
            self.print_display(word=word, guess_word=guess_word)

        punctuation = get_punctuation(number_of_guesses=self.number_of_guesses)
        print(f'\n\nCompleted in {self.number_of_guesses} guesses{punctuation}\n')
        print(self.share_text)


def play(qwerty_console=True):
    clear_console()
    w = Wordle(qwerty_console=qwerty_console)
    play_again = True
    while play_again:
        w.play()
        raw_play_again = input('\nDo you want to play again with a new word? [y,n]:\n ')
        if raw_play_again.strip().lower() in allowed_true:
            play_again = True
        else:
            play_again = False


if __name__ == '__main__':
    import argparse
    # set up the parser for this Script
    parser = argparse.ArgumentParser(description='Parser for play.py, a Wordle Emulator.')
    parser.add_argument('--abc', dest='abc', action='store_true',
                        help="Turns on an 'ABCDEF...' letter console for keeping track of used letters. " +
                             "The default is --no-abc which displays a qwerty letter console.")
    parser.add_argument('--no-abc', dest='abc', action='store_false', default=True,
                        help="Turns off an 'ABCDEF...' letter console for and uses the default qwerty console " +
                             "for keeping track of used letters. ")
    args = parser.parse_args()
    # run the game script
    play(qwerty_console=not args.abc)
