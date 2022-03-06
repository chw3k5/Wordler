





def determine_test_types(guess_word, solution_word):
    correct_guess_letters = set()
    wrong_place_letters = set()
    used_too_many_times_letters = set()
    index_to_guess_letter_and_display_type = {}
    remaining_word_indexes = list(range(len(guess_word)))
    remaining_word_letters = list(solution_word)
    for correct_index in list(remaining_word_indexes):
        guess_letter = guess_word[correct_index]
        word_letter = solution_word[correct_index]
        if word_letter == guess_letter:
            index_to_guess_letter_and_display_type[correct_index] = (guess_letter, '2')
            correct_guess_letters.add(guess_letter)
            remaining_word_indexes.remove(correct_index)
            remaining_word_letters.remove(guess_letter)

    for is_used_index in list(remaining_word_indexes):
        guess_letter = guess_word[is_used_index]
        if guess_letter in remaining_word_letters:
            index_to_guess_letter_and_display_type[is_used_index] = (guess_letter, '1')
            wrong_place_letters.add(guess_letter)

            remaining_word_indexes.remove(is_used_index)
            remaining_word_letters.remove(guess_letter)

    for is_used_index in list(remaining_word_indexes):
        guess_letter = guess_word[is_used_index]
        index_to_guess_letter_and_display_type[is_used_index] = (guess_letter, '0')
        used_too_many_times_letters.add(guess_letter)
        remaining_word_indexes.remove(is_used_index)
    if len(remaining_word_indexes) != 0:
        raise TypeError
    return index_to_guess_letter_and_display_type, correct_guess_letters, wrong_place_letters, \
           used_too_many_times_letters