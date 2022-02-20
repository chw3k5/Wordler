import os
import pickle
from random import shuffle


dir_name = os.path.dirname(os.path.realpath(__file__))
all_words_path = os.path.join(dir_name, 'all_words.csv')
allowed_guesses_path = os.path.join(dir_name, 'allowed_guesses.csv')
calculated_first_guesses_path = os.path.join(dir_name, 'calculated_first_guesses.csv')
prefix, _ = calculated_first_guesses_path.rsplit('.', 1)
calculated_first_guesses_path_pickle = prefix + '.pkl'



def generate_all_results():
    for i in range(0, 3):
        i_str = str(i)
        for j in range(0, 3):
            j_str = str(j)
            for k in range(0, 3):
                k_str = str(k)
                for n in range(0, 3):
                    n_str = str(n)
                    for m in range(0, 3):
                        yield  i_str + j_str + k_str + n_str + str(m)


def words_into_list(path=all_words_path):
    with open(path, 'r') as f:
        return [raw_line.strip().lower() for raw_line in f]


def build_by_letter_dict(word_list):
    by_letter = {}
    for single_word in word_list:
        letter0 = single_word[0]
        letter1 = single_word[1]
        letter2 = single_word[2]
        letter3 = single_word[3]
        letter4 = single_word[4]
        if letter0 not in by_letter.keys():
            by_letter[letter0] = {}
        if letter1 not in by_letter[letter0].keys():
            by_letter[letter0][letter1] = {}
        if letter2 not in by_letter[letter0][letter1].keys():
            by_letter[letter0][letter1][letter2] = {}
        if letter3 not in by_letter[letter0][letter1][letter2].keys():
            by_letter[letter0][letter1][letter2][letter3] = {}
        by_letter[letter0][letter1][letter2][letter3][letter4] = single_word
    return by_letter


def words_shuffled(path=all_words_path):
    all_word_list = words_into_list(path=path)
    shuffle(all_word_list)
    return all_word_list


def words_into_by_letter_dict(path=all_words_path):
    all_word_list = words_into_list(path=path)
    by_letter = build_by_letter_dict(word_list=all_word_list)
    shuffle(all_word_list)
    return by_letter, all_word_list


all_outcomes_list = list(generate_all_results())
all_word_list = words_into_list()
all_answers = set(all_word_list)
allowed_guesses = set(words_into_list(path=allowed_guesses_path)) | all_answers
all_guesses = sorted(allowed_guesses)


def write_calculated_results(remaining_words_given_outcome, guessed_list=None, as_csv=True):
    if as_csv:
        if guessed_list is None:
            guessed_list = all_guesses
        header = 'guess_word'
        for outcome in all_outcomes_list:
            header += f',{outcome}'
        header += '\n'
        body_lines = []
        for guess_index, guess_word in list(enumerate(guessed_list)):
            guess_outcomes = remaining_words_given_outcome[guess_index]
            guess_line = f'{guess_word}'
            for guess_outcome in guess_outcomes:
                guess_line += f',{guess_outcome}'
            guess_line += '\n'
            body_lines.append(guess_line)
        with open(calculated_first_guesses_path, 'w') as f:
            f.write(header)
            for line in body_lines:
                f.write(line)
    else:
        with open(calculated_first_guesses_path_pickle, 'wb') as f:
            pickle.dump(remaining_words_given_outcome, f)

def read_calculated_results(guessed_list=None, from_csv=True):
    if from_csv:
        with open(calculated_first_guesses_path, 'r') as f:
            header = f.readline()
            body_lines = f.readlines()
        _, *all_outcomes = header.split(',')
        outcomes_list = [outcome.strip() for outcome in all_outcomes]
        words_given_outcome = {}
        for line in body_lines:
            guess_word_raw, *guess_outcomes_raw = line.split(',')
            guess_word = guess_word_raw.strip()
            guess_outcomes = [int(guess_outcome.strip()) for guess_outcome in guess_outcomes_raw]
            words_given_outcome[guess_word] = {outcome: guess_outcome for outcome, guess_outcome
                                                         in zip(outcomes_list, guess_outcomes)}
        remaining_words_given_outcome = []
        if guessed_list is None:
            guessed_list = all_guesses
        for allowed_guess in guessed_list:
            outcomes_dict = words_given_outcome[allowed_guess]
            outcomes_this_word = []
            for outcome in all_outcomes_list:
                outcomes_this_word.append(outcomes_dict[outcome])
            remaining_words_given_outcome.append(outcomes_this_word)
    else:
        with open(calculated_first_guesses_path_pickle, "rb") as open_file:
            remaining_words_given_outcome = pickle.load(open_file)
    return remaining_words_given_outcome


if __name__ == '__main__':
    look_up_by_letter, shuffled_word_list = words_into_by_letter_dict()










