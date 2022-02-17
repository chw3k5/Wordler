import os
from random import shuffle


dir_name = os.path.dirname(os.path.realpath(__file__))
all_words_path = os.path.join(dir_name, 'all_words.csv')


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


if __name__ == '__main__':
    look_up_by_letter, shuffled_word_list = words_into_by_letter_dict()










