import os
from getpass import getuser
from multiprocessing import Pool
import numpy as np
from copy import deepcopy
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
    all_guesses = all_guesses[:100]
    all_guesses[0] = 'raise'
elif current_user == "chw3k5":
    multiprocessing_threads = balanced_threads  # Caleb's other computers
elif current_user in "cwheeler":
    multiprocessing_threads = max_threads  # Mac Pro 8-core intel core i9 processor 16 threads
elif current_user in "jdw8":
    multiprocessing_threads = max_threads  # Mac Pro 8-core intel core i9 processor 16 threads
else:
    multiprocessing_threads = balanced_threads

first_guess = 'raise'
outcome = '0000'


def generate_all_results():
    for i in range(0, 3):
        for j in range(0, 3):
            for k in range(0, 3):
                for n in range(0, 3):
                    for m in range(0, 3):
                        yield str(i) + str(j) + str(k) + str(n) + str(m)


all_outcomes_list = list(generate_all_results())


def per_word_outcomes(guess_word, known_wrong_positions_initial=None,\
                          available_answers_initial=all_answers,known_positions_initial={}):
                          
    if known_wrong_positions_initial is None:
        known_wrong_positions_initial = {}
        
    for single_outcome in all_outcomes_list:
        # calc_remaining_words made to minipulate data so I need to reset to initial state after 
        # each call
        # I am using a deep copy to do that but that might be slow?
        # not a problem for available answers I guess becuase it is a set? not a dict
        known_wrong_positions = deepcopy(known_wrong_positions_initial)
        known_positions = deepcopy(known_positions_initial)
        
        known_wrong_positions, known_positions_this_guess, required_letter_count_this_guess,\
          available_answers,known_not_used = \
            calc_remaining_words(known_wrong_positions=known_wrong_positions,\
                                     available_answers=available_answers_initial,\
                                     guess_word=guess_word, guess_results=single_outcome,\
                                     known_positions=known_positions)
                                     
        yield len(available_answers)


def per_word_outcomes_wrapper(args):
    guess_index, guess_word, known_wrong_positions_initial, available_answers_initial,known_positions_initial = args
    print(f'{" %5d" % guess_index}, {guess_word}',end = '\r')
    this_word_outcomes = \
      list(per_word_outcomes(guess_word=guess_word,known_wrong_positions_initial=known_wrong_positions_initial,\
                                 available_answers_initial=available_answers_initial,\
                                 known_positions_initial = known_positions_initial))
    return this_word_outcomes


def generate_all_words_outcomes(known_wrong_positions_initial=None, available_answers_initial=all_answers\
                                    ,known_positions_initial = {}):
    if multiprocessing_threads is None:
        all_outcomes_list = []
        for guess_index, guess_word in list(enumerate(all_guesses)):
            this_word_outcomes =per_word_outcomes_wrapper(args=(guess_index, guess_word,known_wrong_positions_initial,\
                                                                    available_answers_initial,known_positions_initial))

            all_outcomes_list.append(this_word_outcomes)

    else:
        all_args = [(guess_index, guess_word, known_wrong_positions_initial, available_answers_initial,\
                         known_positions_initial) for guess_index, guess_word in list(enumerate(all_guesses))]
        with Pool(multiprocessing_threads) as p:
            all_outcomes_list = p.map(per_word_outcomes_wrapper, all_args)
    return all_outcomes_list


def calc(known_wrong_positions_initial=None, available_answers_initial=all_answers,known_positions_initial = {}):
    all_outcomes_list = generate_all_words_outcomes(known_wrong_positions_initial=known_wrong_positions_initial,\
                            available_answers_initial=available_answers_initial,\
                                known_positions_initial = known_positions_initial)
                                                        
    remaining_words_given_outcome = np.array(all_outcomes_list)
    np.save("result_with_guesses.npy", remaining_words_given_outcome)


def calc_after_guessing(guess_words, guess_results, number_of_results_to_display=20):
    known_wrong_positions_initial, known_positions_initial, required_letter_count_this_guess,\
      available_answers_initial,known_not_used =calc_remaining_words(known_wrong_positions={},\
        available_answers=all_answers,guess_word=guess_words[0], guess_results=guess_results[0],\
                                                                         known_positions={})
      
    for i in range(1, len(guess_words)):
        known_wrong_positions_initial, known_positions_this_guess, required_letter_count_this_guess,\
          available_answers_initial,known_not_used = \
            calc_remaining_words(known_wrong_positions=known_wrong_positions_initial,\
                                     available_answers=available_answers_initial,\
                                     guess_word=guess_words[i],\
                                     guess_results=guess_results[i],\
                                     known_positions=known_positions_initial)
                                     
        known_positions_initial.update(known_positions_this_guess)
        
    if len(available_answers_initial) > 2:
        calc_outcomes(rerun=True, known_wrong_positions_initial=known_wrong_positions_initial,
                      available_answers_initial=available_answers_initial,
                      number_of_results_to_display=number_of_results_to_display,
                          known_positions_initial=known_positions_initial)

        print("length of possible answers", len(available_answers_initial))
        print(available_answers_initial)
    elif len(available_answers_initial) == 2:
        print("Only two answers left pick one of :",available_answers_initial)
    else:
        print("Only answer remaining is  ", available_answers_initial)
        



def calc_outcomes(rerun=False, number_of_results_to_display=25, known_wrong_positions_initial=None,
                  available_answers_initial=all_answers,known_positions_initial = {}):
    print(f'There are {len(all_outcomes_list)} the are possible outcomes per word.')
    # there are a lot of cases where the outcome is impossible should I average or total or minimize
    # it seems given every possible outcome every word is possible.
    # sum is always 2315 so not useful
    # want sum of length*lixlyhood = sum(length(all_outcomes)*(len(all_outcomes)/total_possible_words)
    # should equal average list length
    if rerun:
        calc(known_wrong_positions_initial=known_wrong_positions_initial,
             available_answers_initial=available_answers_initial,
                 known_positions_initial = known_positions_initial)

    remaining_words_given_outcome = np.load("result_with_guesses.npy")

    average_remaining_list_length = np.sum(remaining_words_given_outcome * remaining_words_given_outcome
                                               / len(available_answers_initial),axis=1)
    
    a = np.argsort(average_remaining_list_length)
    if debug_mode:
        sorted_words = np.asarray(all_guesses[0:100])[a]
    else:
        sorted_words = np.asarray(all_guesses)[a]
    sorted_values = average_remaining_list_length[a]

    print(f'Top {number_of_results_to_display} Results: Possible answers in \033[1;30;42mgreen\033[0;0m')
    print(" word | (likely length of narrowed list)")
    answer_available = False
    for word_index, (sorted_word, sorted_value) in list(enumerate(zip(sorted_words, sorted_values))):
        if word_index == number_of_results_to_display:
            break
        if sorted_word in available_answers_initial:
            print(f'\033[1;30;42m{sorted_word} | ({sorted_value}) \033[0;0m')
            answer_available = True
        else:
            print(f'{sorted_word} | ({sorted_value})')


    if not (answer_available):
        print("...")
        for word_index, (sorted_word, sorted_value) in list(enumerate(zip(sorted_words, sorted_values))):
            if sorted_word in available_answers_initial:
                print(f'\033[1;30;42m{sorted_word} | ({sorted_value}) \033[0;0m')
                answer_available = True
                break


if __name__ == '__main__':
    # calc_outcomes(rerun=False, number_of_results_to_display=20)
    # don't typo
    #calc_after_guessing(['raise'],['10000'])
    #calc_after_guessing(['raise', 'count'], ['10000', '01000'])
    calc_after_guessing(['raise', 'count','bludy'], ['10000', '01000','00011'])
