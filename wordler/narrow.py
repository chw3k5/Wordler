import os
from copy import deepcopy
from operator import itemgetter
from string import ascii_lowercase
from typing import NamedTuple, Optional
from read_words import words_into_list, build_by_letter_dict


all_word_list = words_into_list()
all_answers = set(all_word_list)
dir_name = os.path.dirname(os.path.realpath(__file__))
allowed_guesses_path = os.path.join(dir_name, 'allowed_guesses.csv')
allowed_guesses = set(words_into_list(path=allowed_guesses_path)) | all_answers
all_guesses = sorted(allowed_guesses)


allowed_letters = set(ascii_lowercase)
allowed_true = {"true", 'y', 'yes', 'yeah', 't', 'yep', '1'}
allowed_false = {"false", 'n', 'no', 'nope', 'f', '0'}
allow_result_answers = {'0', '1', '2'}


def clear_console():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)


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
        is_correct_place_raw = input(f'Was the {position} letter "{letter}" in the correct position? [y/n]: ')
        is_correct_place = process_bool_user_input(is_raw=is_correct_place_raw)
    return is_correct_place


def ask_letter_used(position, letter) -> bool:
    is_used = None
    while is_used is None:
        is_used_raw = input(f'Was the {position} letter "{letter}" used in the word? [y/n]: ')
        is_used = process_bool_user_input(is_raw=is_used_raw)
    return is_used


def ask_guess_word(guess_number=None) -> str:
    if guess_number is None:
        question_string = 'Enter your guess word'
    else:
        question_string = f'Enter your guess for word number {guess_number}'
    guess_word = None
    while guess_word is None:
        raw_word = input(f'{question_string}:\n\n')
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


def ask_guess_results(guess_word='', guess_number=None):
    finished = False
    test_results = None
    if guess_number is None:
        guess_number_str = ''
    else:
        guess_number_str = ' for guess number {guess_number}'
    clear_console()
    while not finished:
        print(f'\nEnter Your Results{guess_number_str}:')
        print(' \033[1;37;40m 0 \033[0;0m for a letter that was not in the word.')
        print(' \033[1;30;43m 1 \033[0;0m for a letter that is in the word, but is not the correct position.')
        print(' \033[1;30;42m 2 \033[0;0m for a letter is in the correct position.')
        raw_results = input(f'  {guess_word}\n  ')
        test_results = raw_results.strip()
        finished = are_results_correctly_formatted(results_list=test_results)
    return test_results


def get_suggestions(letters):
    suggested_guesses = []
    for guess in all_guesses:
        for letter in letters:
            if letter not in guess:
                break
        else:
            suggested_guesses.append(guess)
    return suggested_guesses


def make_subsets(letters):
    letters_subsets = []
    for letter in reversed(letters):
        letters_subsets.append(letters.replace(letter, ''))
    return letters_subsets


def guess_using_letters(letters):
    # to exit recursion is all letters are removed
    if len(letters) == 0:
        return []
    # get a word that uses all the letters
    suggested_guesses = get_suggestions(letters=letters)
    if suggested_guesses:
        return suggested_guesses
    # get words that use a subset of the letters, using recursion.
    for letters_subset in make_subsets(letters=letters):
        suggested_guesses.extend(guess_using_letters(letters=letters_subset))
    return suggested_guesses


def narrow_by_correct_place(available_answers, letter, letter_index):
    return [test_word for test_word in available_answers if letter == test_word[letter_index]]


def narrow_by_usage(available_answers, known_wrong_positions, letter):
    for test_word in available_answers:
        # the letter must be in the word
        if letter in test_word:
            for test_index, test_letter in list(enumerate(test_word)):
                if test_letter == letter and letter in known_wrong_positions.keys() \
                        and test_index in known_wrong_positions[letter]:
                    break
            else:
                yield test_word


def narrow_by_usage_wrapper(available_answers, known_wrong_positions, letter, letter_index):
    # track the data about this letter's usage
    if letter not in known_wrong_positions.keys():
        known_wrong_positions[letter] = set()
    known_wrong_positions[letter].add(letter_index)
    remaining = list(narrow_by_usage(available_answers=available_answers, known_wrong_positions=known_wrong_positions,
                                     letter=letter))
    return known_wrong_positions, remaining


def narrow_by_omission(available_answers, letter):
    return [test_word for test_word in available_answers if letter not in test_word]


def calc_remaining_words(known_wrong_positions, available_answers, guess_word, guess_results):
    for letter_index, (letter, guess_result) in list(enumerate(zip(guess_word, guess_results))):
        guess_result = str(guess_result)
        if guess_result == '2':
            available_answers = narrow_by_correct_place(available_answers=available_answers,
                                                        letter=letter, letter_index=letter_index)
        elif guess_result == '1':
            known_wrong_positions, available_answers = \
                narrow_by_usage_wrapper(available_answers=available_answers,
                                        known_wrong_positions=known_wrong_positions,
                                        letter=letter, letter_index=letter_index)
        elif guess_result == '0':
            available_answers = narrow_by_omission(available_answers=available_answers, letter=letter)
        else:
            raise KeyError(f'Guess result: {guess_result} is not an allowed value.')

    return known_wrong_positions, available_answers


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

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        # data structures that get initialized with self.reset()
        self.guess_number = None
        self.remaining_words = None
        self.possible_words_dict = None
        self.letter_counter = None
        self.known_rules = None
        self.known_letters = None
        self.know_position = None
        self.known_wrong_positions = None
        self.wrong_guesses = None
        self.remaining_letters = None
        self.count_list = None
        self.guess_using_remaining = None
        self.ranked_words_by_rank = None
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
        for letter, count in self.count_list:
            return_str += f'{letter}:{self.letter_counter[letter]}  '
        # Ranked Words
        return_str += f'\n\nSuggestions of possible Answer Words - Ranked by Sum of Remaining Letters:\n '
        for word, rank in self.ranked_words_by_rank:
            return_str += f'{word}({rank}) '
        # allowed guess to use up remaining letters
        if len(self.ranked_words_by_rank) > 1:
            return_str += f'\n\nSuggestions of Guesses to use some of the top 5 remaining letters \n' +\
                          f' * indicates this is a possible answer:\n    '
            for guess_word in self.guess_using_remaining:
                if guess_word in self.remaining_words:
                    warning_str = '*'
                else:
                    warning_str = ''
                return_str += f'{guess_word}{warning_str}  '
        # finishing up
        return_str += '\n\n'
        return return_str

    def __len__(self):
        return len(self.remaining_words)

    def reset(self):
        self.guess_number = 0
        self.known_rules = set()
        self.known_letters = {}
        self.know_position = {}
        self.known_wrong_positions = {}
        self.wrong_guesses = set()
        self.set_data(word_list=deepcopy(self.all_word_list))

    def count_letters(self):
        # count the letters that remain.
        self.letter_counter = {}
        for word in list(self):
            letter_set = {letter for letter in word}
            for letter in letter_set:
                if letter not in self.letter_counter.keys():
                    self.letter_counter[letter] = 0
                self.letter_counter[letter] += 1
        self.remaining_letters = set(self.letter_counter.keys()) - set(self.known_letters.keys())
        self.count_list = sorted([(letter, self.letter_counter[letter]) for letter in self.remaining_letters],
                                 key=itemgetter(1), reverse=True)
        # get best guesses using the remaining letters
        top_5_remaining_letters = ''
        for letter, count in self.count_list:
            if len(top_5_remaining_letters) < 5:
                top_5_remaining_letters += letter
            else:
                break
        self.guess_using_remaining = guess_using_letters(letters=top_5_remaining_letters)

    def get_rank_value(self, word):
        letter_set = {letter for letter in word}
        value = 0
        for letter in letter_set:
            if letter in self.remaining_letters:
                value += self.letter_counter[letter]
        return value

    def rank_words(self):
        self.ranked_words_by_rank = sorted([(word, self.get_rank_value(word)) for word in list(self)],
                                           key=itemgetter(1), reverse=True)

    def set_data(self, word_list):
        self.remaining_words = word_list
        self.possible_words_dict = build_by_letter_dict(word_list=self.remaining_words)
        self.count_letters()
        self.rank_words()

    def narrow_by_correct_place(self, letter, letter_index):
        narrowed_word_list = narrow_by_correct_place(available_answers=list(self),
                                                     letter=letter, letter_index=letter_index)
        self.known_letters[letter] = letter_index
        self.know_position[letter_index] = letter
        self.set_data(word_list=narrowed_word_list)

    def narrow_by_usage(self, letter, letter_index):
        # track the data about this letter's usage
        self.known_letters[letter] = True
        if letter not in self.known_wrong_positions.keys():
            self.known_wrong_positions[letter] = set()
        self.known_wrong_positions[letter].add(letter_index)
        # narrow the list of possible words
        self.known_wrong_positions, narrowed_word_list = \
            narrow_by_usage_wrapper(available_answers=list(self), known_wrong_positions=self.known_wrong_positions,
                                    letter=letter, letter_index=letter_index)
        self.set_data(word_list=narrowed_word_list)

    def narrow_by_omission(self, letter):
        narrowed_word_list = narrow_by_omission(available_answers=list(self), letter=letter)
        self.known_letters[letter] = False
        self.set_data(word_list=narrowed_word_list)

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
        # only one rule is create per letter guess, that rule is made on the first letter recieved
        for rule in list(rules_list):
            self.add_rule(rule=rule)
        if self.verbose:
            clear_console()
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
        self.guess_number += 1
        rules_list = []
        guess_word = ask_guess_word(guess_num=self.guess_number)
        for letter_index, letter in list(enumerate(guess_word)):
            position = self.index_terms[letter_index]
            if not self.is_known_wrong_letter(letter=letter, letter_index=letter_index) \
                    and not self.is_known_letter_position(letter=letter, letter_index=letter_index):
                if self.verbose:
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
        if self.verbose:
            print('\n')
        self.add_guess(rules_list=rules_list)

    def ask_guess(self, guess_word=None, results=None):
        self.guess_number += 1
        rules_list = []
        if guess_word is None:
            guess_word = ask_guess_word(guess_number=self.guess_number)
        if results is None:
            results = ask_guess_results(guess_word=guess_word, guess_number=self.guess_number)
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
        if self.verbose:
            print('\n')
        self.add_guess(rules_list=rules_list)


def helper():
    clear_console()
    av = AvailableWords()
    print(av)
    while len(av) > 1:
        av.ask_guess()


if __name__ == '__main__':
    helper()
