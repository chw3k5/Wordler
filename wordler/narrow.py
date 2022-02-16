from copy import deepcopy
from string import ascii_lowercase
from typing import NamedTuple
from operator import itemgetter
from read_words import words_into_list, build_by_letter_dict


all_word_list = words_into_list()


allowed_letters = set(ascii_lowercase)
allowed_true = {"true", 'y', 'yes', 'yeah', 't', 'yep', '1'}
allowed_false = {"false", 'n', 'no', 'nope', 'f', '0'}


def process_bool_user_input(is_raw):
    is_test = is_raw.strip().lower()
    if is_test in allowed_true:
        return True
    elif is_test in allowed_false:
        return False
    else:
        return None


class Rule(NamedTuple):
    letter: str
    letter_number: int
    is_used: bool
    is_correct_place: bool


class Guess(NamedTuple):
    letter0: Rule
    letter1: Rule
    letter2: Rule
    letter3: Rule
    letter4: Rule


class AvailableWords:
    all_word_list = all_word_list
    index_terms = ['first', 'second', 'third', 'forth', 'fifth']

    def __init__(self):
        self.remaining_words = None
        self.possible_words_dict = None
        self.letter_counter = None
        self.known_rules = None
        self.known_letters = None
        self.know_position = None
        self.wrong_guesses = None
        self.remaining_letters = None

        self.reset()


    def __iter__(self):
        for letter0 in sorted(self.possible_words_dict.keys()):
            for letter1 in sorted(self.possible_words_dict[letter0].keys()):
                for letter2 in sorted(self.possible_words_dict[letter0][letter1].keys()):
                    for letter3 in sorted(self.possible_words_dict[letter0][letter1][letter2].keys()):
                        for letter4 in sorted(self.possible_words_dict[letter0][letter1][letter2][letter3].keys()):
                            yield letter0 + letter1 + letter2 + letter3 + letter4

    def __str__(self):
        first_letter_last_word = ''
        return_str = ''
        for remaining_word in list(self):
            first_letter_this_word = remaining_word[0]
            if first_letter_last_word not in first_letter_this_word:
                return_str += '\n'
            return_str += f'{remaining_word} '
            first_letter_last_word = first_letter_this_word
        return_str += f'\n\nKnown letters ({len(self.known_letters)}):\n'
        for letter in sorted(self.known_letters.keys()):
            value = self.known_letters[letter]
            return_str += f'{letter}:'
            if isinstance(value, bool):
                if value:
                    return_str += 'in word  '
                else:
                    return_str += 'not used  '
            else:
                return_str += f'is {self.index_terms[value]} letter  '
        return_str += f'\n\nRemaining letters ({len(self.remaining_letters)}):\n'
        count_list = [(letter, self.letter_counter[letter])
                      for letter in self.remaining_letters]
        for letter, count in sorted(count_list, key=itemgetter(1), reverse=True):
            return_str += f'{letter}:{self.letter_counter[letter]}  '
        return return_str

    def __len__(self):
        return len(self.remaining_words)

    def reset(self):
        self.known_rules = set()
        self.known_letters = {}
        self.know_position = {}
        self.wrong_guesses = set()
        self.set_data(word_list=deepcopy(self.all_word_list))


    def count_letters(self):
        self.letter_counter = {}
        for word in list(self):
            for letter in word:
                if letter not in self.letter_counter.keys():
                    self.letter_counter[letter] = 0
                self.letter_counter[letter] += 1
        self.remaining_letters = set(self.letter_counter.keys()) - set(self.known_letters.keys())

    def set_data(self, word_list):
        self.remaining_words = word_list
        self.possible_words_dict = build_by_letter_dict(word_list=self.remaining_words)
        self.count_letters()



    def narrow_by_correct_place(self, letter, letter_number):
        narrowed_word_list = []
        for test_word in list(self):
            if letter == test_word[letter_number]:
                narrowed_word_list.append(test_word)
        self.set_data(word_list=narrowed_word_list)
        self.known_letters[letter] = letter_number
        self.know_position[letter_number] = letter


    def narrow_by_usage(self, letter):
        narrowed_word_list = []
        for test_word in list(self):
            if letter in test_word:
                narrowed_word_list.append(test_word)
        self.set_data(word_list=narrowed_word_list)
        self.known_letters[letter] = True

    def narrow_by_omission(self, letter):
        narrowed_word_list = []
        for test_word in list(self):
            if letter not in test_word:
                narrowed_word_list.append(test_word)
        self.set_data(word_list=narrowed_word_list)
        self.known_letters[letter] = False

    def add_rule(self, rule: Rule):
        if rule.is_correct_place:
            self.narrow_by_correct_place(letter=rule.letter, letter_number=rule.letter_number)
        elif rule.is_used:
            self.narrow_by_usage(letter=rule.letter)
        else:
            self.narrow_by_omission(letter=rule.letter)
            self.wrong_guesses.add((rule.letter, rule.letter_number))
        self.known_rules.add(rule)

    def add_guess(self, rules_list):
        for rule in list(rules_list):
            self.add_rule(rule=rule)
        print(f'{len(self.remaining_words)} words are possible')
        print(f'  {self}')

    def ask_guess(self):
        rules_list = []

        guess_word = None
        while guess_word is None:
            raw_word = input(f'Enter your guess word: ')
            test_word = raw_word.strip().lower()
            if len(test_word) == 5:
                for letter in test_word:
                    if letter not in allowed_letters:
                        break
                else:
                    guess_word = test_word

        for letter_index, letter in list(enumerate(guess_word)):
            position = self.index_terms[letter_index]
            is_correct_place = None
            is_used = None
            if (letter, letter_index) not in self.wrong_guesses and \
                    not (letter_index in self.know_position.keys() and letter == self.know_position[letter_index]):
                print("")
                if letter_index in self.know_position.keys() and letter != self.know_position[letter_index]:
                        is_correct_place = False
                else:
                    while is_correct_place is None:
                        is_correct_place_raw = input(f'Was the {position} letter "{letter}" in the correct position?')
                        is_correct_place = process_bool_user_input(is_raw=is_correct_place_raw)
                if is_correct_place:
                    is_used = True
                else:
                    while is_used is None:
                        is_used_raw = input(f'Was the {position} letter "{letter}" used in the word?')
                        is_used = process_bool_user_input(is_raw=is_used_raw)
                rule = Rule(letter=letter, letter_number=letter_index, is_correct_place=is_correct_place,
                            is_used=is_used)
                rules_list.append(rule)
        print('\n')
        self.add_guess(rules_list=rules_list)


def helper():
    av = AvailableWords()
    guess_num = 0
    while len(av) > 1:
        guess_num += 1
        av.ask_guess()
        print(f'\n After Guess number {guess_num}\n')


if __name__ == '__main__':
    helper()
