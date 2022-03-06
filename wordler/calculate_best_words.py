import os
from copy import deepcopy
from getpass import getuser
from multiprocessing import Pool
from narrow import calc_remaining_words, AvailableWords
from read_words import write_calculated_results, all_answers, all_guesses, all_outcomes_list, read_calculated_results
import math
import matplotlib.pyplot as plt
import numpy as np

# to do
# remove checksum in not rerun for first guess

# dev options
do_calculated_first_guesses_rerun = False
write_csv_outcomes = False
read_from_csv_outcomes = False
do_checksum = False
write_words = False # needed to parse failures of checksum but slow to read and right
                    # leave off until faliure turn on and repeat failure

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
    #all_guesses[0] = 'raise'
elif current_user == "chw3k5":
    multiprocessing_threads = balanced_threads  # Caleb's other computers
elif current_user in "cwheeler":
    multiprocessing_threads = max_threads  # Mac Pro 8-core intel core i9 processor 16 threads
elif current_user in "jdw8":
    multiprocessing_threads = max_threads  # Mac Pro 8-core intel core i9 processor 16 threads
else:
    multiprocessing_threads = balanced_threads


# need to clean up into sub functions
def trim_outcomes(word,known_positions_initial):
    possible_outcomes = deepcopy(all_outcomes_list)
    # look for repeated letters
    repeated_letters = []
    for letter in word:
        if word.count(letter)>1: #repeated
            if letter not in repeated_letters: #only need to do this once
                repeated_letters.append(letter)
                # cant have 22112 for two repeated letters or 21112 for three
                impossible_outcome = ''
                for i in range(0,len(word)):
                    if letter == word[i]:
                        impossible_outcome = impossible_outcome + '1'
                    else:
                        impossible_outcome = impossible_outcome + '2'
                possible_outcomes.remove(impossible_outcome)  
                
                indexes = []
                for i in range(0,len(word)):
                    if letter == word[i]:
                        indexes.append(i)

                impossible_outcome = '' #abccd 22102 #abbbc 21002  
                for i in range(0,len(word)):
                    if i == indexes[0]:
                        impossible_outcome = impossible_outcome + '1'
                    elif i in indexes:
                        impossible_outcome = impossible_outcome + '0'
                    else:
                        impossible_outcome = impossible_outcome + '2'

                possible_outcomes.remove(impossible_outcome)
                    
                #__01_ or _0_1_
                outcomes_to_remove = []
                for outcome in possible_outcomes: 
                    if (outcome[indexes[0]] == '0' and outcome[indexes[1]] == '1'): 
                        outcomes_to_remove.append(outcome)
                    if len(indexes)>2: #need to make compatible with more than just 3 repeated indexes
                        if (outcome[indexes[0]] == '0' and outcome[indexes[1]] == '0' and outcome[indexes[2]] == '1'): 
                            outcomes_to_remove.append(outcome)

                        if (outcome[indexes[0]] == '2' and outcome[indexes[1]] == '0' and outcome[indexes[2]] == '1'): 
                            outcomes_to_remove.append(outcome)

                        if (outcome[indexes[0]] == '1' and outcome[indexes[1]] == '0' and outcome[indexes[2]] == '1'): 
                            outcomes_to_remove.append(outcome)
                            
                        if (outcome[indexes[0]] == '0' and outcome[indexes[1]] == '2' and outcome[indexes[2]] == '1'):#weete #_02_1
                            outcomes_to_remove.append(outcome)
                for outcome in outcomes_to_remove:
                    possible_outcomes.remove(outcome)
           
                outcomes_to_remove = [] #if doubles are 1s cant have more than one 2
                for outcome in possible_outcomes:
                    if (outcome[indexes[0]] == '1' and outcome[indexes[1]] == '1'):
                        if outcome.count('2')>1:
                            outcomes_to_remove.append(outcome)

                for outcome in outcomes_to_remove:
                    possible_outcomes.remove(outcome)

    # rules
    if known_positions_initial != None:
        for index in known_positions_initial.keys():
            outcomes_to_remove = []
            if word[index] != known_positions_initial[index]: #if known 2 is not same letter
                for outcome in possible_outcomes:
                    if outcome[index] == '2':
                        outcomes_to_remove.append(outcome)
            for outcome in outcomes_to_remove:
                possible_outcomes.remove(outcome)

    # there might be more impossible outcomes and trimming them might save me time
    return possible_outcomes

def calculate_average_remaining_list_length(remaining_words_given_outcome, length_remaining_words):
    average_remaining_list_length = []
    for outcomes_this_guess in remaining_words_given_outcome:
        squared_values = [outcome_this_guess * outcome_this_guess for outcome_this_guess in outcomes_this_guess]
        sum_values = float(sum(squared_values))
        average_remaining_list_length.append(sum_values / length_remaining_words)
    return average_remaining_list_length

def calculate_variance(remaining_words_given_outcome, length_remaining_words):
    variance = []
    for outcomes_this_guess in remaining_words_given_outcome:
        values = []
        for outcome in outcomes_this_guess:
            if outcome !=0:
                values.append(1.)
        sum_outcomes = float(sum(values))
        squared_values = []
        for outcome in outcomes_this_guess:
            if outcome != 0:
                squared_values.append((outcome-length_remaining_words/sum_outcomes) * (outcome-length_remaining_words/sum_outcomes))
        sum_values = float(sum(squared_values))
        variance.append(sum_values / length_remaining_words)
    return variance

def calculate_max_remaining_list_length(remaining_words_given_outcome, length_remaining_words):
    average_remaining_list_length = []
    for outcomes_this_guess in remaining_words_given_outcome:
        average_remaining_list_length.append(max(outcomes_this_guess))
    return average_remaining_list_length

def calculate_best_chance_after_one_guess(remaining_words_given_outcome, length_remaining_words):
    '''
    probablity of right per outcome is 1/len_remaining_list)
    probabiliy of getting outcome is len_remaining_list/total_remaining_words
    chance after one guess is the sum of the product of those
    which is just the number of total possible outcomes/total_remaining_words
    which is not what I intuitively expected
    this mode assumes you will try to guess possible answers after this guess
    '''
    metric = []
    for outcomes_this_guess in remaining_words_given_outcome:
        values = []
        for outcome in outcomes_this_guess:
            if outcome !=0:
                values.append(1.)
        sum_values = float(sum(values))
        metric.append(sum_values / length_remaining_words)
    return metric

def power_law(x, a, b, c):
    return a*np.power(x, b)+c

def dict_of_guess_cost_per_list_len():
    cost = {}
    for i in range(0,len(all_answers)+1):
        if i == 0:
            cost[str(i)] = 0.0
        elif i == 1: # 1s
            cost[str(i)] = 1.0
        elif i == 2: # 2s
            cost[str(i)] = 1.5
        elif i == 3: # 3s
            cost[str(i)] = 1.7512027491408937
        elif i == 4: # 4s
            cost[str(i)] = 1.8580178173719377
        elif i == 5: # 4s
            cost[str(i)] = 1.9201465201465202
        else: # 6s and above
            #cost[str(i)] = 0.2322564106807115*math.log(i)+1.5894950183677843
            cost[str(i)] = power_law(i,-2.49828811,-0.16720445, 3.81375087)

    return cost

guess_cost_per_len = dict_of_guess_cost_per_list_len()

def calculate_expected_guess_cost(remaining_words_given_outcome,length_remaining_words):
    '''
    derived from data from good words 
    '''
    metric = []
    count = 0
    for outcomes_this_guess in remaining_words_given_outcome:
        count = count+1
        values = []
        for outcome in outcomes_this_guess:
            if outcome !=0:
                values.append(outcome*guess_cost_per_len[str(outcome)])
        values.append(length_remaining_words)
        sum_values = float(sum(values))
        metric.append(sum_values)
    return metric
            
def sum_all_lengths(remaining_words_given_outcome):
    sum_list_length = []
    for outcomes_this_guess in remaining_words_given_outcome:
        sum_values = sum(outcomes_this_guess)
        sum_list_length.append(sum_values)
    return sum_list_length

def check_sum(sum_list_length,available_answers,remaining_words_given_outcome,all_possible_outcomes,all_guesses):
    check_length = len(available_answers)
    available_answers_list =list(available_answers)
    for i in range(0,len(sum_list_length)):
        if sum_list_length[i]>check_length:
            print("non unique outcomes for i = ",i,all_guesses[i])
            if write_words: #can only check for repeated words if we are storing them
                for n in range(0,len(available_answers_list)):
                    occurances = []
                    for m in range(0,len(remaining_words_given_outcome[i])):
                        if available_answers_list[n] in remaining_words_given_outcome[i][m]:
                            occurances.append(1)
                        else:
                            occurances.append(0)
                    if sum(occurances)>1:
                        print(available_answers_list[n],"occurs more than once for outcomes")
                        for k in range(0,len(occurances)):
                            if occurances[k] == 1:
                                print(all_possible_outcomes[i][k])
                        break #just show first one
                            
        elif sum_list_length[i]<check_length:
            print("to restrictive rules/not all possilbe outcomes considered for i = ",i,all_guesses[i])

def generate_possible_outcomes_for_all_guesses(all_guesses,known_positions_initial = None):
    possible_outcomes_for_all_guesses = []
    for i in range(0,len(all_guesses)):
        possible_outcomes_for_all_guesses.append(trim_outcomes(all_guesses[i],known_positions_initial))      
    return possible_outcomes_for_all_guesses

def calculate_length_of_word_lists(remaining_words_given_outcome):
    list_of_list_of_lengths =[] 
    for i in range(0,len(remaining_words_given_outcome)):
        this_word_list = []
        for j in range(0,len(remaining_words_given_outcome[i])):
            this_word_list.append(len(remaining_words_given_outcome[i][j]))
        list_of_list_of_lengths.append(this_word_list)
    return list_of_list_of_lengths
       
def per_word_outcomes(guess_word, known_wrong_positions_initial=None,
                      available_answers_initial=deepcopy(all_answers),
                      known_positions_initial=None):
    if known_wrong_positions_initial is None:
        known_wrong_positions_initial = {}
    if known_positions_initial is None:
        known_positions_initial = {}

    possible_outcomes = trim_outcomes(guess_word,known_positions_initial)
    for single_outcome in possible_outcomes:
        known_wrong_positions, known_positions_this_guess, required_letter_count_this_guess,\
          available_answers,known_not_used = \
            calc_remaining_words(known_wrong_positions=deepcopy(known_wrong_positions_initial),
                                 available_answers=available_answers_initial,
                                 guess_word=guess_word, guess_results=single_outcome,
                                 known_positions=deepcopy(known_positions_initial))
        if write_words:
            yield available_answers
        else:
            yield len(available_answers)

def per_word_outcomes_wrapper(args):
    guess_index, guess_word, known_wrong_positions_initial, available_answers_initial, known_positions_initial,len_available_guesses_initial = args
    this_word_outcomes = \
      list(per_word_outcomes(guess_word=guess_word, known_wrong_positions_initial=known_wrong_positions_initial,
                             available_answers_initial=available_answers_initial,
                             known_positions_initial=known_positions_initial))
    print(f'{" %3d" % (100*guess_index/len_available_guesses_initial)}% complete'+\
              f'{" (%5d" % (guess_index)}/{"%5d" % (len_available_guesses_initial)})', end='\r')
    return this_word_outcomes

def generate_all_words_outcomes(known_wrong_positions_initial=None, available_answers_initial=None,
                                known_positions_initial=None,available_guesses_initial = None):
    if available_answers_initial is None:
        available_answers_initial = deepcopy(all_answers)
    if available_guesses_initial is None:
        available_guesses_initial = deepcopy(all_guesses)

    if multiprocessing_threads is None:
        all_outcomes_list = []
        for guess_index, guess_word in list(enumerate(available_guesses_initial)):
            this_word_outcomes = per_word_outcomes_wrapper(args=(guess_index, guess_word,known_wrong_positions_initial,
                                                                 available_answers_initial,known_positions_initial,
                                                                 len(available_guesses_initial)))

            all_outcomes_list.append(this_word_outcomes)

    else:
        all_args = [(guess_index, guess_word, known_wrong_positions_initial, available_answers_initial,
                     known_positions_initial,len(available_guesses_initial)) for guess_index, guess_word in list(enumerate(available_guesses_initial))]
        with Pool(multiprocessing_threads) as p:
            #all_outcomes_list = p.map(per_word_outcomes_wrapper, all_args)
            all_outcomes_list = list(p.imap(per_word_outcomes_wrapper, all_args))
    return all_outcomes_list


def calc(known_wrong_positions_initial=None, available_answers_initial=None,
             known_positions_initial=None,available_guesses_initial = None):
    if available_answers_initial is None:
        available_answers_initial = deepcopy(all_answers)
    if available_guesses_initial is None:
        available_guesses_initial = deepcopy(all_guesses)
    print("Calculating optimal words...")
    remaining_words_given_outcome = generate_all_words_outcomes(
                        known_wrong_positions_initial=known_wrong_positions_initial,
                            available_answers_initial=available_answers_initial,
                                known_positions_initial=known_positions_initial,
                                     available_guesses_initial = available_guesses_initial)
    return remaining_words_given_outcome


def calc_outcomes(guess_words=None, guess_results=None, rerun=False, number_of_results_to_display=25,
                  known_wrong_positions_initial=None, available_answers_initial=None,
                  known_positions_initial=None,available_guesses_initial = None,
                  verbose = True,mode = 'ave'):

    if not isinstance(mode, list):
        mode = [mode]
    if available_answers_initial is None:
        available_answers_initial = deepcopy(all_answers)
    if available_guesses_initial is None:
        available_guesses_initial = deepcopy(all_guesses)
    """
    There are 3**5 -5(GGGGY) - more for repeated letters possible outcomes
    Given every possible outcome every word is possible
    """
    if guess_words == None: 
        if len(available_answers_initial) != len(all_answers): # detect if supplying rules instead of guesses and results
            if len(available_answers_initial) > 2:
                remaining_words_given_outcome = calc(known_wrong_positions_initial=known_wrong_positions_initial,
                                                     available_answers_initial=available_answers_initial,
                                                     known_positions_initial=known_positions_initial,
                                                     available_guesses_initial = available_guesses_initial)
        else:
            if rerun: #first guesses are a bit slow and only change if word banks are updated
                remaining_words_given_outcome = calc(known_wrong_positions_initial=known_wrong_positions_initial,
                                                     available_answers_initial=available_answers_initial,
                                                     known_positions_initial = known_positions_initial,
                                                     available_guesses_initial = available_guesses_initial)
                
                write_calculated_results(remaining_words_given_outcome=remaining_words_given_outcome,
                                         as_csv=write_csv_outcomes,words = write_words)
            else:
                remaining_words_given_outcome = read_calculated_results(from_csv=read_from_csv_outcomes,words = write_words)
    else:
        # generate available answers base on first guess
        known_wrong_positions_initial, known_positions_initial, required_letter_count_this_guess, \
          available_answers_initial, known_not_used = \
            calc_remaining_words(known_wrong_positions={}, available_answers=deepcopy(all_answers),guess_word=guess_words[0],
                                 guess_results=guess_results[0], known_positions={},available_guesses_initial = deepcopy(all_guesses))

        for i in range(1, len(guess_words)):
            known_wrong_positions_initial, known_positions_this_guess, required_letter_count_this_guess,\
              available_answers_initial,known_not_used = \
                calc_remaining_words(known_wrong_positions=known_wrong_positions_initial,
                                         available_answers=available_answers_initial,
                                         guess_word=guess_words[i],
                                         guess_results=guess_results[i],
                                         known_positions=known_positions_initial,
                                         available_guesses_initial = available_guesses_initial)

            known_positions_initial.update(known_positions_this_guess)

        if len(available_answers_initial) > 2:
            remaining_words_given_outcome = calc(known_wrong_positions_initial=known_wrong_positions_initial,
                                                     available_answers_initial=available_answers_initial,
                                                     known_positions_initial=known_positions_initial,
                                                     available_guesses_initial = available_guesses_initial)

    if len(available_answers_initial) == 2:
        print("Only two answers left pick one of:")
        print(available_answers_initial[0],available_answers_initial[1])
        return available_answers_initial, [1,1], available_answers_initial #make return compatible
    elif len(available_answers_initial) == 1:
        print("The only answer remaining is")
        print(available_answers_initial[0])
        return available_answers_initial, [0], available_answers_initial #make return compatible
    else:
        if verbose:
            #print("length of possible answers", len(available_answers_initial))
            if not (len(available_answers_initial) == len(all_answers)): #don't want to see it first time
                print(available_answers_initial)
        if write_words:
            remaining_words_given_outcome_length = calculate_length_of_word_lists(remaining_words_given_outcome)
        else:
            remaining_words_given_outcome_length = remaining_words_given_outcome
        # do check sum
        if do_checksum:
            print("Doing checksum")
            possible_outcomes_for_all_guesses = \
              generate_possible_outcomes_for_all_guesses(available_guesses_initial,known_positions_initial)
            sum_list_length = sum_all_lengths(remaining_words_given_outcome_length)
            check_sum(sum_list_length,available_answers_initial,remaining_words_given_outcome,
                          possible_outcomes_for_all_guesses,available_guesses_initial)


        reversed = False
        metrics = []
        for m in mode:
            if m == 'ave' :
                metrics.append(calculate_average_remaining_list_length(remaining_words_given_outcome_length,
                                                                     len(available_answers_initial)))
            elif m == 'minimax':
                metrics.append(calculate_max_remaining_list_length(remaining_words_given_outcome_length,
                                                                 len(available_answers_initial)))
            elif m == 'split': # maximize
                metric = calculate_best_chance_after_one_guess(remaining_words_given_outcome_length,
                                                                   len(available_answers_initial))
                metrics.append([ -x for x in metric])
            elif m == 'variance':
                metrics.append(calculate_variance(remaining_words_given_outcome_length,
                                                                   len(available_answers_initial)))
                reversed = False
            elif m == 'cost':
                metrics.append(calculate_expected_guess_cost(remaining_words_given_outcome_length,len(available_answers_initial)))
                reversed = False
            else:
                raise KeyError(f'mode: {mode}, not available.')

        if len(mode) == 1:
            print("true")
            if debug_mode:
                sorted_lists = sorted(zip(metrics[0], available_guesses_initial[0:100]),reverse = reversed)
            else:
                sorted_lists = sorted(zip(metrics[0], available_guesses_initial),reverse = reversed)
        else:
            if debug_mode:
                sorted_lists = sorted(zip(*metrics, available_guesses_initial[0:100]),reverse = reversed)
            else:
                sorted_lists = sorted(zip(*metrics, available_guesses_initial),reverse = reversed)
        tuples = zip(*sorted_lists)
        sorted_values = []
        for m in mode:
            sorted_values.append([])
        
        *sorted_values, sorted_words = [list(tuple) for tuple in  tuples]

        if verbose:
            print_results(sorted_words,sorted_values,available_answers_initial,mode = mode,
                              number_of_results_to_display = number_of_results_to_display)

        return sorted_words, sorted_values[0], available_answers_initial

    
def print_results(sorted_words,sorted_values,available_answers_initial,mode = 'ave',
                      number_of_results_to_display = 20):
    answer_available = False
    print(f'Top {number_of_results_to_display} Results: Possible answers in \033[1;30;42mgreen\033[0;0m')
    print('------------------------------------------')
    line_1 = " word "
    line_2 = "      "

    for m in mode:
        if m == 'ave':
            line_1 += "|ave length"
            line_2 += "| of list  "
        elif m == 'minimax':
            line_1 += "|max length"
            line_2 += "| of list  "
        elif m == 'split':
            line_1 += "|chance right"
            line_2 += "| next guess "
        elif m == 'cost':
            line_1 += "|guesses "
            line_2 += "|to solve"
        elif m == 'variance':
            line_1 += "|variance of"
            line_2 += "|list length"
        else:
            raise KeyError(f'mode: {mode}, not available.')
    print(line_1)
    print(line_2)

    for word_index, (sorted_word, *sorted_value) in list(enumerate(zip(sorted_words, *sorted_values))):
        #print(sorted_value)
        if word_index >= number_of_results_to_display and answer_available:
            break
        elif word_index == number_of_results_to_display:
            print("...")
        elif word_index<number_of_results_to_display:
            if sorted_word in available_answers_initial:
                print_line(sorted_word,sorted_value,mode = mode,in_answers = True)
                answer_available = True
            else:
                print_line(sorted_word,sorted_value,mode = mode,in_answers = False)
        else:
            if sorted_word in available_answers_initial:
                print_line(sorted_word,sorted_value,mode = mode,in_answers = True)
                answer_available = True
            
def print_line(sorted_word,sorted_value,mode = 'ave',in_answers = False):
    #print(sorted_value)
    if in_answers:
        line = f'\033[1;30;42m{sorted_word} '
    else:
        line = f'{sorted_word} '
    for m, value in zip(mode,sorted_value):
        if m == 'ave':
            line += f'| {"%7.3f" % value}  '     
        elif m == 'minimax':
            line += f'|   {"%4d" % value}   ' 
        elif m == 'split':
            line += f'| {"%7.3f" % (-value*100)}%   '
        elif m == 'variance':
            line += f'|  {"%7.3f" % value}  '
        elif m == 'cost':
            line += f'|{"%7.3f" % value}'
        else:
            raise KeyError(f'mode: {mode}, not available.')
    if in_answers:
        line += '\033[0;0m'
    print(line)
    
def helper(mode = 'ave',number_of_results_to_display = 20):
    av = AvailableWords()
    while len(av) > 1:
        calc_outcomes(rerun=do_calculated_first_guesses_rerun,
                      number_of_results_to_display=number_of_results_to_display,
                      known_wrong_positions_initial=av.known_wrong_positions,
                      available_answers_initial=av.remaining_words,
                      known_positions_initial=av.known_positions,
                      available_guesses_initial=av.all_guesses,
                      mode = mode)
        av.ask_guess()


if __name__ == '__main__':
    helper(mode = ['split','variance','minimax','ave','cost'],number_of_results_to_display=25 )
    #calc_outcomes(rerun=False, number_of_results_to_display=20,mode = 'ave')
    #calc_outcomes(rerun = False,verbose = False)
    #calc_outcomes(['shape', 'drive'], ['22202', '00202'])
