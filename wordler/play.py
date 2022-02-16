from copy import copy
from random import shuffle
from read_words import words_into_list
from narrow import allowed_true


class Wordle:
    allowed_words = set(words_into_list())
    allowed_guesses = set(words_into_list(path='allowed_guesses.csv')) | allowed_words

    def __init__(self):
        self.available_words = list(self.allowed_words)
        shuffle(self.available_words)

        self.remaining_guesses = None
        self.number_of_guesses = None
        self.share_text = None

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
            raw_word = input(f"Enter guess number: {self.number_of_guesses}")
            test_word = raw_word.strip().lower()
            if len(test_word) == 5 and test_word in self.remaining_guesses:
                guess_word = test_word
        self.remaining_guesses.remove(guess_word)
        return guess_word

    def make_letter_text(self, word, guess_letter, guess_index):
        if guess_letter in word:
            if guess_letter == word[guess_index]:
                self.share_text += f'\033[1;30;42m   \033[0;0m'
                return f'\033[1;30;42m {guess_letter} \033[0;0m'
            else:
                self.share_text += f'\033[1;30;43m   \033[0;0m'
                return f'\033[1;30;43m {guess_letter} \033[0;0m'
        else:
            self.share_text += f'\033[1;37;40m   \033[0;0m'
            return f'\033[1;37;40m {guess_letter} \033[0;0m'

    def print_word_text(self, word, guess_word):
        text_str = ''
        for guess_index, guess_letter in list(enumerate(guess_word)):
            text_str += self.make_letter_text(word=word, guess_letter=guess_letter, guess_index=guess_index)
        print(text_str)
        self.share_text += '\n'

    def play(self, word=None):
        self.number_of_guesses = 0
        self.share_text = ''
        self.remaining_guesses = copy(self.allowed_guesses)
        word = self.get_word(word=word)
        guess_word = None
        while guess_word != word:
            guess_word = self.ask_for_word()
            self.print_word_text(word=word, guess_word=guess_word)

        print(f'\nCompleted in {self.number_of_guesses} Guesses')
        print(self.share_text)
        play_again = input('\nDo you want to play again with a new word? [y,n]:')
        if play_again.strip().lower() in allowed_true:
            self.play()


if __name__ == '__main__':
    w = Wordle()
    w.play()
