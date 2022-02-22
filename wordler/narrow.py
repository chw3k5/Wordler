import os
from copy import deepcopy
from operator import itemgetter
from string import ascii_lowercase
from read_words import build_by_letter_dict, all_guesses, all_word_list


allowed_letters = set(ascii_lowercase)
allowed_true = {"true", 'y', 'yes', 'yeah', 't', 'yep', '1'}
allowed_false = {"false", 'n', 'no', 'nope', 'f', '0'}
allow_result_answers = {'0', '1', '2'}


def clear_console():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)


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


def narrow_by_usage(available_answers, known_wrong_positions, letter, min_letter_occurrences):
    for test_word in available_answers:
        # the letter must be in the word the correct number of times
        if test_word.count(letter) >= min_letter_occurrences:
            # This letters must not be in known incorrect positions.
            for test_index, test_letter in list(enumerate(test_word)):
                if test_letter == letter and letter in known_wrong_positions.keys() \
                        and test_index in known_wrong_positions[letter]:
                    break
            else:
                yield test_word


def narrow_by_usage_wrapper(available_answers, known_wrong_positions, letter, letter_index, min_letter_occurrences):
    # track the data about this letter's usage
    if letter not in known_wrong_positions.keys():
        known_wrong_positions[letter] = set()
    known_wrong_positions[letter].add(letter_index)
    remaining = list(narrow_by_usage(available_answers=available_answers, known_wrong_positions=known_wrong_positions,
                                     letter=letter, min_letter_occurrences=min_letter_occurrences))
    return known_wrong_positions, remaining


def narrow_by_omission(available_answers, letter):
    return [test_word for test_word in available_answers if letter not in test_word]


def narrow_by_max_usage(available_answers, letter, max_letter_occurrences):
    return [test_word for test_word in available_answers if test_word.count(letter) <= max_letter_occurrences]


def calc_remaining_words(known_wrong_positions, known_positions, available_answers, guess_word, guess_results):
    unassigned_indexes = list(range(len(guess_word)))
    required_letter_count_this_guess = {}
    known_positions_this_guess = {}
    known_not_used = set()
    # layer 1 the letter is in the correct place
    for unassigned_index in list(unassigned_indexes):
        if guess_results[unassigned_index] == '2':
            correct_guess_letter = guess_word[unassigned_index]
            if correct_guess_letter not in required_letter_count_this_guess.keys():
                required_letter_count_this_guess[correct_guess_letter] = 0
            required_letter_count_this_guess[correct_guess_letter] += 1
            if unassigned_index not in known_positions.keys():
                available_answers = narrow_by_correct_place(available_answers=available_answers,
                                                            letter=correct_guess_letter, letter_index=unassigned_index)
                known_positions_this_guess[unassigned_index] = correct_guess_letter
            unassigned_indexes.remove(unassigned_index)

    # layer 2, for the remaining letters check if they are in the reaming part of the word
    for unassigned_index in list(unassigned_indexes):
        if guess_results[unassigned_index] == '1':
            is_used_guess_letter = guess_word[unassigned_index]
            if is_used_guess_letter not in required_letter_count_this_guess.keys():
                required_letter_count_this_guess[is_used_guess_letter] = 0
            # deal with repeated letter guesses test case aahed 10100 word macho should be removed
            if guess_word.count(guess_word[unassigned_index])>1:# #handle repeated letter guesses
                repeated = [] 
                for letter in guess_word:
                    if letter == guess_word[unassigned_index]:
                        repeated.append(1)
                    else:
                        repeated.append(0)
                for index in range(0,len(guess_word)):
                    #        if repeated     and      is not the 1 we are examining and = 0

                    if (repeated[index] == 1 and index != unassigned_index and guess_results[index] == '0' ): #other 1s or 2s allowed
                        if guess_word[unassigned_index] not in known_wrong_positions.keys():
                            known_wrong_positions[guess_word[unassigned_index]] = set()
                        known_wrong_positions[guess_word[unassigned_index]].add(index)

            required_letter_count_this_guess[is_used_guess_letter] += 1
            known_wrong_positions, available_answers = \
                narrow_by_usage_wrapper(available_answers=available_answers,
                                        known_wrong_positions=known_wrong_positions,
                                        letter=is_used_guess_letter, letter_index=unassigned_index,
                                        min_letter_occurrences=required_letter_count_this_guess[is_used_guess_letter])
            unassigned_indexes.remove(unassigned_index)

    # these letters are not used or are not used in this number
    for unassigned_index in list(unassigned_indexes):
        if guess_results[unassigned_index] == '0':
            not_needed_guess_letter = guess_word[unassigned_index]
            if not_needed_guess_letter in required_letter_count_this_guess.keys():
                # this letter is used, but not the number of times it occurs in the guess word
                available_answers = \
                    narrow_by_max_usage(available_answers=available_answers, letter=not_needed_guess_letter,
                                        max_letter_occurrences=required_letter_count_this_guess[not_needed_guess_letter])
                if not_needed_guess_letter not in known_wrong_positions.keys():
                    known_wrong_positions[not_needed_guess_letter] = set()
                known_wrong_positions[not_needed_guess_letter].add(unassigned_index)
            else:
                # this letter is not in the word at all
                available_answers = narrow_by_omission(available_answers=available_answers,
                                                       letter=not_needed_guess_letter)
                known_not_used.add(not_needed_guess_letter)

        else:
            raise KeyError(f'Guess result: {guess_results[unassigned_index]} is not an allowed value.')
    return known_wrong_positions, known_positions_this_guess, required_letter_count_this_guess, available_answers,\
        known_not_used


class AvailableWords:
    all_word_list = deepcopy(all_word_list)
    all_guesses = deepcopy(all_guesses)
    index_terms = ['first', 'second', 'third', 'forth', 'fifth']

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        # data structures that get initialized with self.reset()
        self.guess_number = None
        self.remaining_words = None
        self.remaining_guesses = None
        self.possible_words_dict = None
        self.letter_counter = None
        self.known_rules = None
        self.required_letter_count = None
        self.known_positions = None
        self.known_wrong_positions = None
        self.known_not_used = None
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
        return_str += f'\n\nKnown Letters ({len(self.required_letter_count)}):\n '
        for letter in sorted(self.required_letter_count.keys()):
            value = self.required_letter_count[letter]
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
            for counter, guess_word in list(enumerate(self.guess_using_remaining)):
                if guess_word in self.remaining_words:
                    warning_str = '*'
                else:
                    warning_str = ''
                return_str += f'{guess_word}{warning_str}  '
                if counter > 38:
                    break
        # finishing up
        return_str += '\n\n'
        return return_str

    def __len__(self):
        return len(self.remaining_words)

    def reset(self):
        self.guess_number = 0
        self.known_rules = set()
        self.required_letter_count = {}
        self.known_positions = {}
        self.known_wrong_positions = {}
        self.known_not_used = set()
        self.wrong_guesses = set()
        self.set_data(word_list=deepcopy(self.all_word_list), guesses=deepcopy(self.all_guesses))

    def count_letters(self):
        # count the letters that remain.
        self.letter_counter = {}
        for word in list(self):
            letter_set = {letter for letter in word}
            for letter in letter_set:
                if letter not in self.letter_counter.keys():
                    self.letter_counter[letter] = 0
                self.letter_counter[letter] += 1
        self.remaining_letters = set(self.letter_counter.keys()) - set(self.required_letter_count.keys())
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

    def set_data(self, word_list, guesses):
        self.remaining_words = word_list
        self.remaining_guesses = guesses
        self.possible_words_dict = build_by_letter_dict(word_list=self.remaining_words)
        self.count_letters()
        self.rank_words()

    def add_guess(self, guess_word, guess_results):
        self.known_wrong_positions, known_positions_this_guess, required_letter_count_this_guess, available_answers,\
            known_not_used = \
            calc_remaining_words(known_wrong_positions=self.known_wrong_positions,
                                 available_answers=list(self), guess_word=guess_word,
                                 guess_results=guess_results, known_positions=self.known_positions)
        self.known_positions.update(known_positions_this_guess)
        for letter in required_letter_count_this_guess.keys():
            if letter not in self.required_letter_count.keys() or \
                    required_letter_count_this_guess[letter] > self.required_letter_count[letter]:
                self.required_letter_count[letter] = required_letter_count_this_guess[letter]

        _known_wrong_positions, _known_positions_this_guess, _required_letter_count_this_guess, available_guesses,\
            _known_not_used = \
            calc_remaining_words(known_wrong_positions=self.known_wrong_positions,
                                 available_answers=self.remaining_guesses, guess_word=guess_word,
                                 guess_results=guess_results, known_positions=self.known_positions)
        self.set_data(word_list=available_answers, guesses=available_guesses)
        # display the results
        if self.verbose:
            clear_console()
            print(f'{len(self.remaining_words)} words are possible')
            print(f'  {self}')

    def is_known_wrong_letter(self, letter, letter_index) -> bool:
        return (letter, letter_index) in self.wrong_guesses

    def is_known_letter_position(self, letter, letter_index) -> bool:
        return letter_index in self.known_positions.keys() and letter == self.known_positions[letter_index]

    def is_known_this_position(self, letter, letter_index) -> bool:
        return letter_index in self.known_positions.keys() and letter != self.known_positions[letter_index]

    def is_known_wrong_position(self, letter, letter_index) -> bool:
        return letter in self.known_wrong_positions.keys() and letter_index in self.known_wrong_positions[letter]

    def ask_guess(self, guess_word=None, results=None):
        self.guess_number += 1
        if guess_word is None:
            guess_word = ask_guess_word(guess_number=self.guess_number)
        if results is None:
            results = ask_guess_results(guess_word=guess_word, guess_number=self.guess_number)
        if self.verbose:
            print('\n')
        self.add_guess(guess_word=guess_word, guess_results=results)


def helper():
    clear_console()
    av = AvailableWords()
    print(av)
    while len(av) > 1:
        av.ask_guess()


if __name__ == '__main__':
    helper()
