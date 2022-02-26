import random
from narrow import AvailableWords
from calculate_best_words import calc_outcomes


class GetHint:
    hint_types = ['caleb', 'natalie', 'jada', 'jordan']

    def __init__(self, hint_type=None, hard_mode=False, bot_mode=False):
        # settings
        self.hard_mode = hard_mode
        self.bot_mode = bot_mode
        if hint_type is None:
            self.hint_type = None
        else:
            self.hint_type = hint_type.strip().lower()
            if self.hint_type not in self.hint_types:
                raise KeyError(f"'{self.hint_type}' is not one of hint types: {self.hint_types}")
        # data that is initialized later
        self.av = None
        self.remaining_guesses = None
        self.guess_words = None
        self.guess_results = None
        self.decision_tree = {}  # for jordan's bot to not have to recalculate
        # data that is initialized now
        if bot_mode:
            if hint_type is None:
                raise ValueError('hint_type cannot be None when bot_mode==True')
            self.av = AvailableWords(verbose=False)
            self.remaining_guesses = set(self.av.remaining_guesses)
            self.guess_words = []
            self.guess_results = []

    def find_remaining_words(self, guess_words, guess_results):
        self.av = AvailableWords(verbose=False)
        for guess_word, results_this_guess in zip(guess_words, guess_results):
            self.av.ask_guess(guess_word=guess_word, results=results_this_guess)
        self.remaining_guesses = set(self.av.remaining_guesses)

    def caleb(self, guess_words, guess_results, skip_calculation=False):
        if not skip_calculation:
            self.find_remaining_words(guess_words=guess_words, guess_results=guess_results)

        top_five_words = []
        ranked_words_by_rank = self.av.ranked_words_by_rank
        for word_index, (word, rank) in list(enumerate(ranked_words_by_rank)):
            top_five_words.append(word)
            if len(top_five_words) == 5:
                break
        return random.choice(top_five_words)

    def natalie(self, guess_words, guess_results, skip_calculation=False):
        if not skip_calculation:
            self.find_remaining_words(guess_words=guess_words, guess_results=guess_results)
        top_words = []
        ranked_vowel_guesses_by_rank = self.av.ranked_vowel_guesses_by_rank
        if ranked_vowel_guesses_by_rank:
            for word_index, (word, rank) in list(enumerate(ranked_vowel_guesses_by_rank)):
                if self.hard_mode and word in self.remaining_guesses:
                    top_words.append(word)
                else:
                    top_words.append(word)
                if len(top_words) == 13:
                    break
            return random.choice(top_words)
        else:
            return self.jada(guess_words=guess_words, guess_results=guess_results, skip_calculation=True)

    def jada(self, guess_words, guess_results, skip_calculation=False):
        if not skip_calculation:
            self.find_remaining_words(guess_words=guess_words, guess_results=guess_results)
        top_words = []
        ranked_guesses_by_rank = self.av.ranked_guesses_by_rank
        remaining_words = self.av.remaining_words
        if len(remaining_words) > 2:
            for word_index, (word, rank) in list(enumerate(ranked_guesses_by_rank)):
                if self.hard_mode and word in self.remaining_guesses:
                    top_words.append(word)
                else:
                    top_words.append(word)
                if len(top_words) == 13:
                    break
            return random.choice(top_words)
        else:
            return random.choice(remaining_words)

    def jordan(self, guess_words, guess_results, skip_calculation=False,
               pick_possible_factor=1.1, start_word=None, bros=False, bros_number=100):

        previous_decision = self.check_decision_tree(guess_words, guess_results)
        if previous_decision != None:
            print("Already decided")
            return previous_decision

        if not skip_calculation:
            self.find_remaining_words(guess_words=guess_words, guess_results=guess_results)

        print(len(self.av.remaining_words))
        if start_word is not None:
            if len(guess_words) < 1:
                self.add_decision_tree(start_word, guess_words, guess_results)
                return start_word

        if bros:  # combine caleb and jordan (who are brothers)
            print("bro mode")
            top_words = []
            ranked_guesses_by_rank = self.av.ranked_guesses_by_rank
            for word_index, (word, rank) in list(enumerate(ranked_guesses_by_rank)):
                top_words.append(word)
                if len(top_words) == bros_number:
                    break
            check_guesses = top_words + self.av.remaining_words

            sorted_words, sorted_values, available_answers = \
                calc_outcomes(rerun=False, verbose=True,
                              number_of_results_to_display=10,
                              known_wrong_positions_initial=self.av.known_wrong_positions,
                              available_answers_initial=self.av.remaining_words,
                              known_positions_initial=self.av.known_positions,
                              available_guesses_initial=check_guesses)
        else:
            sorted_words, sorted_values, available_answers = \
                calc_outcomes(rerun=False, verbose=True,
                              number_of_results_to_display=10,
                              known_wrong_positions_initial=self.av.known_wrong_positions,
                              available_answers_initial=self.av.remaining_words,
                              known_positions_initial=self.av.known_positions)

        if sorted_words[0] in available_answers:
            self.add_decision_tree(sorted_words[0], guess_words, guess_results)
            return sorted_words[0]
        else:
            sorted_word, sorted_value = None, None
            for sorted_word, sorted_value in zip(sorted_words, sorted_values):
                if sorted_word in available_answers:
                    break
            print(sorted_value, sorted_values[0] * pick_possible_factor)
            if sorted_value < sorted_values[0] * pick_possible_factor:
                self.add_decision_tree(sorted_word, guess_words, guess_results)
                print(sorted_word)
                return sorted_word
            else:
                print(sorted_words[0])
                self.add_decision_tree(sorted_words[0], guess_words, guess_results)
                return sorted_words[0]

    def add_decision_tree(self, picked_word, guess_words, guess_results):
        # dictionary of past decisiosn
        if len(guess_results) > 0:
            key_list = []
            for i in range(0, len(guess_results)):
                key_list.append(guess_words[i])
                key_list.append(guess_results[i])
            key_tuple = tuple(key_list)

            if not key_tuple in self.decision_tree.keys():
                self.decision_tree[key_tuple] = picked_word

    def check_decision_tree(self, guess_words, guess_results):
        if len(guess_results) > 0:
            key_list = []
            for i in range(0, len(guess_results)):
                key_list.append(guess_words[i])
                key_list.append(guess_results[i])
            key_tuple = tuple(key_list)

            if key_tuple in self.decision_tree.keys():
                return self.decision_tree[key_tuple]
            else:
                return None

    def get_hint(self, guess_words, guess_results):
        if self.hint_type is None:
            hint_type = random.choice(self.hint_types)
        else:
            hint_type = self.hint_type
        return self.__getattribute__(hint_type)(guess_words=guess_words, guess_results=guess_results)


if __name__ == '__main__':
    list_pos = -4
    get_hint = GetHint(hint_type='jada', hard_mode=True)
    guess_words = ['alter', 'owner', 'miser', 'sheer']
    guess_results = ['00022', '00022', '00122', '11022']
    print(get_hint.get_hint(guess_words=guess_words[:list_pos], guess_results=guess_results[:list_pos]))
