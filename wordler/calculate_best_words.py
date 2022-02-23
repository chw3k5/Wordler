import os
from copy import deepcopy
from getpass import getuser
from multiprocessing import Pool
from narrow import calc_remaining_words, AvailableWords
from read_words import write_calculated_results, all_answers, all_guesses, all_outcomes_list, read_calculated_results
#import pdb


# dev options
do_calculated_first_guesses_rerun = False
first_guess_number_of_results_to_display = 25
write_csv_outcomes = False
read_from_csv_outcomes = False
do_checksum = True 
write_words = False #needed to parse failures of checksum but slow to read and right
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
    all_guesses = all_guesses[:1]
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
        if word.count(letter)>1: #repeated #cant have 22112 for two repeated letters or 21112 for three
            if letter not in repeated_letters: #only need to do this once
                repeated_letters.append(letter)
                impossible_outcome = '' #22112
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
                #print("removeing",impossible_outcome)
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
                    #print("removing",outcome)
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

        
            
     
    return possible_outcomes

def calculate_average_remaining_list_length(remaining_words_given_outcome, length_remaining_words):
    average_remaining_list_length = []
    for outcomes_this_guess in remaining_words_given_outcome:
        squared_values = [outcome_this_guess * outcome_this_guess for outcome_this_guess in outcomes_this_guess]
        sum_values = float(sum(squared_values))
        average_remaining_list_length.append(sum_values / length_remaining_words)
    return average_remaining_list_length

def sum_all_lengths(remaining_words_given_outcome):
    sum_list_length = []
    for outcomes_this_guess in remaining_words_given_outcome:
        sum_values = sum(outcomes_this_guess)
        sum_list_length.append(sum_values)
    return sum_list_length

def check_sum(sum_list_length,available_answers,remaining_words_given_outcome,all_possible_outcomes):
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
            pritn("to restrictive rules/not all possilbe outcomes considered for i = ",i,all_guesses[i])


def generate_possible_outcomes_for_all_guesses(all_guesses,known_positions_initial = None):
    possible_outcomes_for_all_guesses = []
    for i in range(0,len(all_guesses)):
        possible_outcomes_for_all_guesses.append(trim_outcomes(all_guesses[i],known_positions_initial))

    #print(possible_outcomes_for_all_guesses)
        
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
                      available_answers_initial=deepcopy(all_answers), known_positions_initial=None):
    if known_wrong_positions_initial is None:
        known_wrong_positions_initial = {}
    if known_positions_initial is None:
        known_positions_initial = {}

    #print(guess_word)
    possible_outcomes = trim_outcomes(guess_word,known_positions_initial)
    #print(guess_word)
    for single_outcome in possible_outcomes:
        #print(single_outcome)
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
    guess_index, guess_word, known_wrong_positions_initial, available_answers_initial,known_positions_initial = args
    this_word_outcomes = \
      list(per_word_outcomes(guess_word=guess_word, known_wrong_positions_initial=known_wrong_positions_initial,
                             available_answers_initial=available_answers_initial,
                             known_positions_initial=known_positions_initial))
    print(f'{" %3d" % (100*guess_index/len(all_guesses))}% complete', end='\r')
    #print(guess_word)
    return this_word_outcomes


def generate_all_words_outcomes(known_wrong_positions_initial=None, available_answers_initial=None,
                                known_positions_initial=None):
    if available_answers_initial is None:
        available_answers_initial = deepcopy(all_answers)
    if multiprocessing_threads is None:
        all_outcomes_list = []
        for guess_index, guess_word in list(enumerate(all_guesses)):
            this_word_outcomes = per_word_outcomes_wrapper(args=(guess_index, guess_word,known_wrong_positions_initial,
                                                                 available_answers_initial,known_positions_initial))

            all_outcomes_list.append(this_word_outcomes)

    else:
        all_args = [(guess_index, guess_word, known_wrong_positions_initial, available_answers_initial,
                     known_positions_initial) for guess_index, guess_word in list(enumerate(all_guesses))]
        with Pool(multiprocessing_threads) as p:
            #all_outcomes_list = p.map(per_word_outcomes_wrapper, all_args)
            all_outcomes_list = list(p.imap(per_word_outcomes_wrapper, all_args))
    return all_outcomes_list


def calc(known_wrong_positions_initial=None, available_answers_initial=None, known_positions_initial=None):
    if available_answers_initial is None:
        available_answers_initial = deepcopy(all_answers)
    print("Calculating optimal words...")
    remaining_words_given_outcome = generate_all_words_outcomes(
                        known_wrong_positions_initial=known_wrong_positions_initial,
                            available_answers_initial=available_answers_initial,
                                known_positions_initial=known_positions_initial)
    return remaining_words_given_outcome


def calc_outcomes(guess_words=None, guess_results=None, rerun=False, number_of_results_to_display=25,
                  known_wrong_positions_initial=None, available_answers_initial=None,
                  known_positions_initial=None):
    if available_answers_initial is None:
        available_answers_initial = deepcopy(all_answers)
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
                #print("here 1",len(available_guesses))
                remaining_words_given_outcome = calc(known_wrong_positions_initial=known_wrong_positions_initial,
                                                     available_answers_initial=available_answers_initial,
                                                     known_positions_initial=known_positions_initial)
                #print("here 2",len(available_guesses))
        else:
            if rerun: #first guesses are a bit slow and only change if word banks are updated
                remaining_words_given_outcome = calc(known_wrong_positions_initial=known_wrong_positions_initial,
                                                     available_answers_initial=available_answers_initial,
                                                     known_positions_initial = known_positions_initial)
                write_calculated_results(remaining_words_given_outcome=remaining_words_given_outcome,
                                         as_csv=write_csv_outcomes,words = write_words)
                

            else:
                remaining_words_given_outcome = read_calculated_results(from_csv=read_from_csv_outcomes,words = write_words)
    else:
        #generate available answers base on first guess
        known_wrong_positions_initial, known_positions_initial, required_letter_count_this_guess, \
          available_answers_initial, known_not_used = \
            calc_remaining_words(known_wrong_positions={}, available_answers=deepcopy(all_answers),guess_word=guess_words[0],
                                 guess_results=guess_results[0], known_positions={})


        available_answers_initial

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
        return available_answers_initial, [1,1], available_answers_initial #make return compatible
    elif len(available_answers_initial) == 1:
        print("Only answer remaining is  ", available_answers_initial)
        return available_answers_initial, [0], available_answers_initial #make return compatible
    else:

        print("length of possible answers", len(available_answers_initial))
        print(available_answers_initial)
        if write_words:
            remaining_words_given_outcome_length = calculate_length_of_word_lists(remaining_words_given_outcome)
        else:
            remaining_words_given_outcome_length = remaining_words_given_outcome
        # do check sum
        if do_checksum:
            print("Doing checksum")
            possible_outcomes_for_all_guesses = generate_possible_outcomes_for_all_guesses(all_guesses,known_positions_initial)
            sum_list_length = sum_all_lengths(remaining_words_given_outcome_length)
            check_sum(sum_list_length,available_answers_initial,remaining_words_given_outcome,possible_outcomes_for_all_guesses)
        #pdb.set_trace()
        average_remaining_list_length = \
            calculate_average_remaining_list_length(remaining_words_given_outcome_length, len(available_answers_initial))

        if debug_mode:
            sorted_lists = sorted(zip(average_remaining_list_length, all_guesses[0:1]))
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
        return sorted_words, sorted_values, available_answers_initial

    

def helper():
    av = AvailableWords()
    while len(av) > 1:
        print("length of all guesses is",len(all_guesses))
        calc_outcomes(rerun=do_calculated_first_guesses_rerun,
                      number_of_results_to_display=first_guess_number_of_results_to_display,
                      known_wrong_positions_initial=av.known_wrong_positions,
                      available_answers_initial=av.remaining_words,
                      known_positions_initial=av.known_positions)
        av.ask_guess()



if __name__ == '__main__':
    helper()
    #calc_outcomes(rerun=False, number_of_results_to_display=20)
    #calc_outcomes(rerun = True)
    #calc_outcomes(['shape', 'drive'], ['22202', '00202'])
    #calc_outcomes(['roate', 'salon','macho'], ['01100', '02010','02202'])
    # logic is calc_outcomes->calc->generate_all_words_outcomes->per_word_outcomes_wrapper
    # ->per_word_outcomes->calc_remaining_words
