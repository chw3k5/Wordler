from copy import deepcopy
from operator import itemgetter
from string import ascii_lowercase
from typing import NamedTuple, Optional
from read_words import words_into_list, build_by_letter_dict


all_word_list = words_into_list()


allowed_letters = set(ascii_lowercase)
allowed_true = {"true", 'y', 'yes', 'yeah', 't', 'yep', '1'}
allowed_false = {"false", 'n', 'no', 'nope', 'f', '0'}
allow_result_answers = {'0', '1', '2'}


def process_bool_user_input(is_raw):
    is_test = is_raw.strip().lower()
    if is_test in allowed_true:
        return True
    elif is_test in allowed_false:
        return False
    else:
        return None


def ask_letter_position(position, letter) -> bool:
    is_correct_place = None
    while is_correct_place is None:
        is_correct_place_raw = input(f'Was the {position} letter "{letter}" in the correct position?')
        is_correct_place = process_bool_user_input(is_raw=is_correct_place_raw)
    return is_correct_place


def ask_letter_used(position, letter) -> bool:
    is_used = None
    while is_used is None:
        is_used_raw = input(f'Was the {position} letter "{letter}" used in the word?')
        is_used = process_bool_user_input(is_raw=is_used_raw)
    return is_used


def ask_guess_word() -> str:
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
    return guess_word


def are_results_correctly_formatted(results_list) -> bool:
    correctly_formatted = False
    if len(results_list) == 5:
        for result in results_list:
            if result not in allow_result_answers:
                break
        else:
            correctly_formatted = True
    return correctly_formatted


def ask_guess_results(guess_word=''):
    finished = False
    test_results = None
    while not finished:
        print('Enter Your Results')
        print(' \033[1;37;40m 0 \033[0;0m for a letter that was not in the word.' )
        print(' \033[1;30;43m 1 \033[0;0m for a letter that is in the word, but is not the correct position.')
        print(' \033[1;30;42m 2 \033[0;0m for a letter is in the correct position.')
        raw_results = input(f'   {guess_word}')
        test_results = raw_results.strip()
        finished = are_results_correctly_formatted(results_list=test_results)
    return test_results


class Rule(NamedTuple):
    letter: str
    letter_index: int
    is_used: bool
    is_correct_place: bool


class Guess(NamedTuple):
    letter0: Optional[Rule] = None
    letter1: Optional[Rule] = None
    letter2: Optional[Rule] = None
    letter3: Optional[Rule] = None
    letter4: Optional[Rule] = None


class AvailableWords:
    all_word_list = all_word_list
    index_terms = ['first', 'second', 'third', 'forth', 'fifth']

    def __init__(self):
        # data structures that get initialized with self.reset()
        self.remaining_words = None
        self.possible_words_dict = None
        self.letter_counter = None
        self.known_rules = None
        self.known_letters = None
        self.know_position = None
        self.known_wrong_positions = None
        self.wrong_guesses = None
        self.remaining_letters = None
        self.ranked_words = None
        # the method the set/restores the initial state
        self.reset()

    def __iter__(self):
        for letter0 in sorted(self.possible_words_dict.keys()):
            for letter1 in sorted(self.possible_words_dict[letter0].keys()):
                for letter2 in sorted(self.possible_words_dict[letter0][letter1].keys()):
                    for letter3 in sorted(self.possible_words_dict[letter0][letter1][letter2].keys()):
                        for letter4 in sorted(self.possible_words_dict[letter0][letter1][letter2][letter3].keys()):
                            yield letter0 + letter1 + letter2 + letter3 + letter4

    def __str__(self):
        # All remaining words
        first_letter_last_word = ''
        return_str = 'Possible Words:'
        for remaining_word in list(self):
            first_letter_this_word = remaining_word[0]
            if first_letter_last_word not in first_letter_this_word:
                return_str += '\n '
            return_str += f'{remaining_word} '
            first_letter_last_word = first_letter_this_word
        # Known Letters Recap
        return_str += f'\n\nKnown Letters ({len(self.known_letters)}):\n '
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
        # Remaining Letters
        return_str += f'\n\nRemaining Letters ({len(self.remaining_letters)}):\n '
        count_list = [(letter, self.letter_counter[letter])
                      for letter in self.remaining_letters]
        for letter, count in sorted(count_list, key=itemgetter(1), reverse=True):
            return_str += f'{letter}:{self.letter_counter[letter]}  '
        # Ranked Words
        return_str += f'\n\nSuggestions from Possible Words - Ranked by Sum of Remaining Letters:\n '
        for word, rank in self.ranked_words:
            return_str += f'{word}({rank}) '
        # finishing up
        return_str += '\n\n'
        return return_str

    def __len__(self):
        return len(self.remaining_words)

    def reset(self):
        self.known_rules = set()
        self.known_letters = {}
        self.know_position = {}
        self.known_wrong_positions = {}
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

    def get_rank_value(self, word):
        letter_set = {letter for letter in word}
        value = 0
        for letter in letter_set:
            if letter in self.remaining_letters:
                value += self.letter_counter[letter]
        return value

    def rank_words(self):
        self.ranked_words = sorted([(word, self.get_rank_value(word)) for word in list(self)],
                                   key=itemgetter(1), reverse=True)

    def set_data(self, word_list):
        self.remaining_words = word_list
        self.possible_words_dict = build_by_letter_dict(word_list=self.remaining_words)
        self.count_letters()
        self.rank_words()

    def narrow_by_correct_place(self, letter, letter_index):
        narrowed_word_list = []
        for test_word in list(self):
            if letter == test_word[letter_index]:
                narrowed_word_list.append(test_word)
        self.set_data(word_list=narrowed_word_list)
        self.known_letters[letter] = letter_index
        self.know_position[letter_index] = letter

    def narrow_by_usage(self, letter, letter_index):
        # track the data about this letter's usage
        self.known_letters[letter] = True
        if letter not in self.known_wrong_positions.keys():
            self.known_wrong_positions[letter] = set()
        self.known_wrong_positions[letter].add(letter_index)
        # narrow the list of possible words
        narrowed_word_list = []
        for test_word in list(self):
            # the letter must be in the word
            if letter in test_word:
                # but the letter must not be in the wrong position
                for test_index, test_letter in list(enumerate(test_word)):
                    if test_letter == letter and self.is_known_wrong_position(letter=letter, letter_index=test_index):
                        break
                else:
                    # happens only when there is no break statement
                    narrowed_word_list.append(test_word)
        self.set_data(word_list=narrowed_word_list)

    def narrow_by_omission(self, letter):
        narrowed_word_list = []
        for test_word in list(self):
            if letter not in test_word:
                narrowed_word_list.append(test_word)
        self.set_data(word_list=narrowed_word_list)
        self.known_letters[letter] = False

    def add_rule(self, rule: Rule):
        if rule.is_correct_place:
            self.narrow_by_correct_place(letter=rule.letter, letter_index=rule.letter_index)
        elif rule.is_used:
            self.narrow_by_usage(letter=rule.letter, letter_index=rule.letter_index)
        else:
            self.narrow_by_omission(letter=rule.letter)
            self.wrong_guesses.add((rule.letter, rule.letter_index))
        self.known_rules.add(rule)

    def add_guess(self, rules_list):
        for rule in list(rules_list):
            self.add_rule(rule=rule)
        print(f'{len(self.remaining_words)} words are possible')
        print(f'  {self}')

    def is_known_wrong_letter(self, letter, letter_index) -> bool:
        return (letter, letter_index) in self.wrong_guesses

    def is_known_letter_position(self, letter, letter_index) -> bool:
        return letter_index in self.know_position.keys() and letter == self.know_position[letter_index]

    def is_known_this_position(self, letter, letter_index) -> bool:
        return letter_index in self.know_position.keys() and letter != self.know_position[letter_index]
    
    def is_known_wrong_position(self, letter, letter_index) -> bool:
        return letter in self.known_wrong_positions.keys() and letter_index in self.known_wrong_positions[letter]

    def ask_guess_slow(self):
        rules_list = []
        guess_word = ask_guess_word()
        for letter_index, letter in list(enumerate(guess_word)):
            position = self.index_terms[letter_index]
            if not self.is_known_wrong_letter(letter=letter, letter_index=letter_index) \
                    and not self.is_known_letter_position(letter=letter, letter_index=letter_index):
                print("")
                if self.is_known_this_position(letter=letter, letter_index=letter_index):
                    is_correct_place = False
                else:
                    is_correct_place = ask_letter_position(position=position, letter=letter)
                if is_correct_place:
                    is_used = True
                else:
                    is_used = ask_letter_position(position=position, letter=letter)
                rule = Rule(letter=letter, letter_index=letter_index, is_correct_place=is_correct_place,
                            is_used=is_used)
                rules_list.append(rule)
        print('\n')
        self.add_guess(rules_list=rules_list)

    def ask_guess(self):
        rules_list = []
        guess_word = ask_guess_word()
        results = ask_guess_results(guess_word=guess_word)
        for letter_index, letter in list(enumerate(guess_word)):
            result = results[letter_index]
            if not self.is_known_wrong_letter(letter=letter, letter_index=letter_index) \
                    and not self.is_known_letter_position(letter=letter, letter_index=letter_index):
                if result == '2':
                    is_correct_place = True
                    is_used = True
                elif result == '1':
                    is_correct_place = False
                    is_used = True
                elif result == '0':
                    is_correct_place = False
                    is_used = False
                else:
                    raise ValueError(f"{result} is not one of the expect values: {allow_result_answers}.")
                rule = Rule(letter=letter, letter_index=letter_index, is_correct_place=is_correct_place,
                            is_used=is_used)
                rules_list.append(rule)
        print('\n')
        self.add_guess(rules_list=rules_list)


def helper():
    av = AvailableWords()
    guess_num = 0
    print(av)
    while len(av) > 1:
        guess_num += 1
        av.ask_guess()
        print(f'\n After Guess number {guess_num}\n')


if __name__ == '__main__':
    helper()
