import os
from getpass import getuser
from multiprocessing import Pool
import numpy as np
from narrow import all_guesses, all_answers, calc_remaining_words

# Debug mode
debug_mode = False
# multiprocessing
# the 'assumption' of max threads is that we are cpu limited in processing,
# so we use should not use more than a computer's available threads
max_threads = int(os.cpu_count())
# Try to strike a balance between best performance and computer usability during processing
balanced_threads = max(max_threads - 2, 2)
# Use onl half of the available threads for processing
half_threads = int(np.round(os.cpu_count() * 0.5))

current_user = getuser()
if debug_mode:
    # this will do standard linear processing.
    multiprocessing_threads = None
elif current_user == "chw3k5":
    multiprocessing_threads = balanced_threads  # Caleb's other computers
elif current_user in "cwheeler":
    multiprocessing_threads = max_threads  # Mac Pro 8-core intel core i9 processor 16 threads
else:
    multiprocessing_threads = balanced_threads


def generate_all_results():
    for i in range(0, 3):
        for j in range(0, 3):
            for k in range(0, 3):
                for n in range(0, 3):
                    for m in range(0, 3):
                        yield str(i) + str(j) + str(k) + str(n) + str(m)


all_outcomes_list = list(generate_all_results())


def per_word_outcomes(guess_word):
    for single_outcome in all_outcomes_list:
        known_wrong_positions, available_answers = \
            calc_remaining_words(known_wrong_positions={}, available_answers=all_answers,
                                 guess_word=guess_word, guess_results=single_outcome)
        yield len(available_answers)


def per_word_outcomes_wrapper(args):
    guess_index, guess_word = args
    print(f'{"%5d" % guess_index}, {guess_word}')
    this_word_outcomes = list(per_word_outcomes(guess_word=guess_word))
    print(f'      Max outcomes value for {guess_word} {max(this_word_outcomes)}')
    return this_word_outcomes


def generate_all_words_outcomes():
    if multiprocessing_threads is None:
        all_outcomes_list = []
        for guess_index, guess_word in list(enumerate(all_guesses)):
            this_word_outcomes = per_word_outcomes_wrapper(args=(guess_index, guess_word))
            all_outcomes_list.append(this_word_outcomes)

    else:
        all_args = [(guess_index, guess_word) for guess_index, guess_word in list(enumerate(all_guesses))]
        with Pool(multiprocessing_threads) as p:
            all_outcomes_list = p.map(per_word_outcomes_wrapper, all_args)
    return all_outcomes_list


def calc():
    all_outcomes_list = generate_all_words_outcomes()
    remaining_words_given_outcome = np.array(all_outcomes_list)
    np.save("result.npy", remaining_words_given_outcome)


def calc_outcomes(rerun=False, number_of_results_to_display=25):
    print(f'There are {len(all_outcomes_list)} the are possible outcomes per word.')
    # there are a lot of cases where the outcome is impossible should I average or total or minimize
    # it seems given every possible outcome every word is possible.
    # sum is always 2315 so not useful
    # want sum of length*likelyhood = sum(length(all_outcomes)*(len(all_outcomes)/total_possible_words)
    # should equal average list length
    if rerun:
        calc()

    remaining_words_given_outcome = np.load("result.npy")

    average_remaining_list_length = np.sum(remaining_words_given_outcome * remaining_words_given_outcome / len(all_words),
                                           axis=0)
    a = np.argsort(average_remaining_list_length)
    sorted_words = np.asarray(all_answers)[a]
    sorted_values = average_remaining_list_length[a]

    print(f'Top {number_of_results_to_display} Results:')
    print(" word | (likely length of narrowed list)")
    for word_index, (sorted_word, sorted_value) in list(enumerate(zip(sorted_words, sorted_values))):
        if word_index == number_of_results_to_display:
            break
        print(f'{sorted_word} | ({sorted_value})')


if __name__ == '__main__':
    calc_outcomes(rerun=True, number_of_results_to_display=20)
