import os
from copy import deepcopy
from getpass import getuser
from multiprocessing import Pool
from narrow import calc_remaining_words, AvailableWords
from read_words import write_calculated_results, all_answers, all_guesses, all_outcomes_list, read_calculated_results


# dev options
do_calculated_first_guesses_rerun = False
first_guess_number_of_results_to_display = 25
write_csv_outcomes = False
read_from_csv_outcomes = False

# Debug mode
debug_mode = False
# multiprocessing
# the 'assumption' of max threads is that we are cpu limited in processing,
# so we use should not use more than a computer's available threads
max_threads = int(os.cpu_count())
# Try to strike a balance between best performance and computer usability during processing
balanced_threads = max(max_threads - 2, 2)
# Use onl half of the available threads for processing
half_threads = int(round(os.cpu_count() * 0.5))

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


def calculate_average_remaining_list_length(remaining_words_given_outcome, length_remaining_words):
    average_remaining_list_length = []
    for outcomes_this_guess in remaining_words_given_outcome:
        squared_values = [outcome_this_guess * outcome_this_guess for outcome_this_guess in outcomes_this_guess]
        sum_values = float(sum(squared_values))
        average_remaining_list_length.append(sum_values / length_remaining_words)
    return average_remaining_list_length


def per_word_outcomes(guess_word, known_wrong_positions_initial=None,
                      available_answers_initial=all_answers, known_positions_initial=None):
    if known_wrong_positions_initial is None:
        known_wrong_positions_initial = {}
    if known_positions_initial is None:
        known_positions_initial = {}
    for single_outcome in all_outcomes_list:
        known_wrong_positions, known_positions_this_guess, required_letter_count_this_guess,\
          available_answers,known_not_used = \
            calc_remaining_words(known_wrong_positions=deepcopy(known_wrong_positions_initial),
                                 available_answers=available_answers_initial,
                                 guess_word=guess_word, guess_results=single_outcome,
                                 known_positions=deepcopy(known_positions_initial))
        yield len(available_answers)


def per_word_outcomes_wrapper(args):
    guess_index, guess_word, known_wrong_positions_initial, available_answers_initial,known_positions_initial = args
    this_word_outcomes = \
      list(per_word_outcomes(guess_word=guess_word, known_wrong_positions_initial=known_wrong_positions_initial,
                             available_answers_initial=available_answers_initial,
                             known_positions_initial=known_positions_initial))
    print(f'{" %5d" % guess_index}, {guess_word}, outcomes max length:{max(this_word_outcomes)}', end='\r')
    return this_word_outcomes


def generate_all_words_outcomes(known_wrong_positions_initial=None, available_answers_initial=all_answers,
                                known_positions_initial=None):
    if multiprocessing_threads is None:
        all_outcomes_list = []
        for guess_index, guess_word in list(enumerate(all_guesses)):
            this_word_outcomes =per_word_outcomes_wrapper(args=(guess_index, guess_word,known_wrong_positions_initial,
                                                                    available_answers_initial,known_positions_initial))

            all_outcomes_list.append(this_word_outcomes)

    else:
        all_args = [(guess_index, guess_word, known_wrong_positions_initial, available_answers_initial,\
                         known_positions_initial) for guess_index, guess_word in list(enumerate(all_guesses))]
        with Pool(multiprocessing_threads) as p:
            all_outcomes_list = p.map(per_word_outcomes_wrapper, all_args)
    return all_outcomes_list


def calc(known_wrong_positions_initial=None, available_answers_initial=all_answers, known_positions_initial=None):
    print("Calculating optimal words...")
    remaining_words_given_outcome = generate_all_words_outcomes(
                        known_wrong_positions_initial=known_wrong_positions_initial,
                            available_answers_initial=available_answers_initial,
                                known_positions_initial=known_positions_initial)
    return remaining_words_given_outcome


def calc_outcomes(guess_words=None, guess_results=None, rerun=False, number_of_results_to_display=25,
                  known_wrong_positions_initial=None, available_answers_initial=all_answers,
                  known_positions_initial=None):
    """
        There are 3**5 possible outcomes
    it seems given every possible outcome every word is possible
    want sum of length_of_list*liklyhood_of_getting_list =
           sum(length_of_list(all_outcomes)*(length_of_list(all_outcomes)/total_possible_words_available_for guess)
    should equal average list length
    """
    if guess_words == None: 
        if len(available_answers_initial) != len(all_answers): # detect if supplying rules instead of guesses and results
            if len(available_answers_initial) > 2:
                remaining_words_given_outcome = calc(known_wrong_positions_initial=known_wrong_positions_initial,
                                                     available_answers_initial=available_answers_initial,
                                                     known_positions_initial=known_positions_initial)
        else:
            if rerun: #first guesses are a bit slow and only change if word banks are updated
                remaining_words_given_outcome = calc(known_wrong_positions_initial=known_wrong_positions_initial,
                                                     available_answers_initial=available_answers_initial,
                                                     known_positions_initial = known_positions_initial)
                write_calculated_results(remaining_words_given_outcome=remaining_words_given_outcome,
                                         as_csv=write_csv_outcomes)

            else:
                remaining_words_given_outcome = read_calculated_results(from_csv=read_from_csv_outcomes)
    else:
        known_wrong_positions_initial, known_positions_initial, required_letter_count_this_guess, \
          available_answers_initial, known_not_used = \
            calc_remaining_words(known_wrong_positions={}, available_answers=all_answers,guess_word=guess_words[0],
                                 guess_results=guess_results[0], known_positions={})

        for i in range(1, len(guess_words)):
            known_wrong_positions_initial, known_positions_this_guess, required_letter_count_this_guess,\
              available_answers_initial,known_not_used = \
                calc_remaining_words(known_wrong_positions=known_wrong_positions_initial,
                                         available_answers=available_answers_initial,
                                         guess_word=guess_words[i],
                                         guess_results=guess_results[i],
                                         known_positions=known_positions_initial)

            known_positions_initial.update(known_positions_this_guess)

        if len(available_answers_initial) > 2:
            remaining_words_given_outcome = calc(known_wrong_positions_initial=known_wrong_positions_initial,
                                                     available_answers_initial=available_answers_initial,
                                                     known_positions_initial=known_positions_initial)

    if len(available_answers_initial) == 2:
        print("Only two answers left pick one of :",available_answers_initial)
    elif len(available_answers_initial) == 1:
        print("Only answer remaining is  ", available_answers_initial)
    else:

        print("length of possible answers", len(available_answers_initial))
        print(available_answers_initial)
        average_remaining_list_length = \
            calculate_average_remaining_list_length(remaining_words_given_outcome, len(available_answers_initial))

        if debug_mode:
            sorted_lists = sorted(zip(average_remaining_list_length, all_guesses[0:100]))
            tuples = zip(*sorted_lists)
            sorted_values, sorted_words = [ list(tuple) for tuple in  tuples]
        else:
            sorted_lists = sorted(zip(average_remaining_list_length, all_guesses))
            tuples = zip(*sorted_lists)
            sorted_values, sorted_words = [ list(tuple) for tuple in  tuples]

        print(f'Top {number_of_results_to_display} Results: Possible answers in \033[1;30;42mgreen\033[0;0m')
        print(" word | (likely length of narrowed list)")
        answer_available = False
        for word_index, (sorted_word, sorted_value) in list(enumerate(zip(sorted_words, sorted_values))):
            if word_index == number_of_results_to_display:
                break
            if sorted_word in available_answers_initial:
                print(f'\033[1;30;42m{sorted_word} | ({"%.3f" % sorted_value})\033[0;0m')
                answer_available = True
            else:
                print(f'{sorted_word} | ({"%.3f" % sorted_value})')


        if not (answer_available):
            print("...")
            for word_index, (sorted_word, sorted_value) in list(enumerate(zip(sorted_words, sorted_values))):
                if sorted_word in available_answers_initial: #{" %5d" % guess_index}
                    print(f'\033[1;30;42m{sorted_word} | ({"%.3f" % sorted_value})\033[0;0m')
                    answer_available = True
                    break

def helper():
    av = AvailableWords()
    print(len(av.remaining_words) == len(all_answers))
    while len(av) > 1:
        calc_outcomes(rerun=do_calculated_first_guesses_rerun,
                      number_of_results_to_display=first_guess_number_of_results_to_display,
                      known_wrong_positions_initial=av.known_wrong_positions,
                      available_answers_initial=av.remaining_words,
                      known_positions_initial=av.known_positions)
        av.ask_guess()



if __name__ == '__main__':
    helper()
    #calc_outcomes(rerun=False, number_of_results_to_display=20)
    #calc_outcomes(['roate'],['01100'])
    #calc_outcomes(['roate', 'salon'], ['01100', '02010'])
    #calc_outcomes(['roate', 'salon','macho'], ['01100', '02010','02202'])
    # logic is calc_outcomes->calc->generate_all_words_outcomes->per_word_outcomes_wrapper
    # ->per_word_outcomes->calc_remaining_words
