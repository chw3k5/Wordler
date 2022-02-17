import numpy as np
from narrow import AvailableWords
from play import Wordle


all_guesses = sorted(Wordle.allowed_guesses)


def generate_all_results():
    for i in range(0, 3):
        for j in range(0, 3):
            for k in range(0, 3):
                for n in range(0, 3):
                    for m in range(0, 3):
                        yield str(i) + str(j) + str(k) + str(n) + str(m)


all_outcomes_list = list(iter(generate_all_results()))


def generate_per_word_outcomes(guess_word):
    for single_outcome in all_outcomes_list:
        av = AvailableWords(verbose=False)
        av.ask_guess(guess_word=guess_word, results=single_outcome)
        yield len(av.remaining_words)


def generate_all_words_outcomes():
    for guess_index, guess_word in list(enumerate(sorted(all_guesses))):
        print(f'{"%5d" % guess_index}, {guess_word}')
        this_word_outcomes = list(iter(generate_per_word_outcomes(guess_word=guess_word)))
        print(f'      Max outcomes value for {guess_word} {max(this_word_outcomes)}')
        yield this_word_outcomes


def calc():
    remaining_words_given_outcome = np.array(list(iter(generate_all_words_outcomes())))
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

    average_remaining_list_length = np.sum(remaining_words_given_outcome * remaining_words_given_outcome / len(all_guesses),
                                           axis=0)
    a = np.argsort(average_remaining_list_length)
    sorted_words = np.asarray(all_guesses)[a]
    sorted_values = average_remaining_list_length[a]

    print(f'Top {number_of_results_to_display} Results:')
    print(" word | (likely length of narrowed list)")
    for word_index, (sorted_word, sorted_value) in list(enumerate(zip(sorted_words, sorted_values))):
        if word_index == number_of_results_to_display:
            break
        print(f'{sorted_words} | ({sorted_value})')


if __name__ == '__main__':
    calc_outcomes(rerun=True, number_of_results_to_display=20)
