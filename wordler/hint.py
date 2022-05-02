import random
from calculate_best_words import calc_outcomes, print_results


class GetHint:
    hint_types = ['caleb', 'natalie', 'jada', 'jordan']

    def __init__(self, hint_type=None, hard_mode=False, bot_mode=False,verbose = True):
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
        self.guess_words = None
        self.guess_results = None
        self.decision_memory = {}  # for jordan's bot to not have to recalculate
        self.verbose = verbose
        # data that is initialized now
        self.reset()

    def reset(self):
        self.guess_words = []
        self.guess_results = []

    @staticmethod
    def caleb(av):
        top_five_words = []
        ranked_words_by_rank = av.ranked_words_by_rank
        for word_index, (word, rank) in list(enumerate(ranked_words_by_rank)):
            top_five_words.append(word)
            if len(top_five_words) == 5:
                break
        return random.choice(top_five_words)

    def natalie(self, av):
        top_words = []
        if len(av) > 2 and len(av.ranked_vowel_guesses_by_rank) > 0:
            second_best_rank_trigger = False
            highest_rank = -1
            for word_index, (word, rank) in list(enumerate(av.ranked_vowel_guesses_by_rank)):
                if rank > highest_rank:
                    highest_rank = rank
                elif highest_rank > rank:
                    second_best_rank_trigger = True
                if len(top_words) > 13 and second_best_rank_trigger:
                    break
                elif self.hard_mode:
                    if word in av.remaining_guesses:
                        top_words.append(word)
                else:
                    top_words.append(word)
            return random.choice(top_words)
        else:
            return self.jada(av=av)

    def jada(self, av):
        top_words = []
        if len(av.remaining_words) > 2:
            for word_index, (word, rank) in list(enumerate(av.all_guesses_by_rank)):
                if self.hard_mode:
                    if word in av.remaining_guesses:
                        top_words.append(word)
                else:
                    top_words.append(word)
                if len(top_words) == 13:
                    break
            return random.choice(top_words)
        else:
            return random.choice(av.remaining_words)

    def jordan(self, av, guess_words, guess_results, mode=None,
               pick_possible_factor=1.0001, start_word=None, bros=False, bros_number=100):
        if mode is None:
            mode = ['split', 'variance']

        previous_decision = self.check_decision_memory(guess_words, guess_results)
        if previous_decision is not None:
            print("Already decided")
            if self.verbose:
                if len(previous_decision[1])>2:
                    print_results(previous_decision[1],previous_decision[2],previous_decision[3],mode = mode,
                      number_of_results_to_display = 10)
            return previous_decision[0]

        if bros:  # combine caleb and jordan (who are brothers)
            top_words = []
            ranked_guesses_by_rank = av.ranked_guesses_by_rank
            for word_index, (word, rank) in list(enumerate(ranked_guesses_by_rank)):
                top_words.append(word)
                if len(top_words) == bros_number:
                    break
            check_guesses = top_words + av.remaining_words

            sorted_words, sorted_values, available_answers = \
                calc_outcomes(rerun=False, verbose=self.verbose,
                              number_of_results_to_display=10,
                              known_wrong_positions_initial=av.known_wrong_positions,
                              available_answers_initial=av.remaining_words,
                              known_positions_initial=av.known_positions,
                              available_guesses_initial=check_guesses, mode=mode)
        else:
            if self.hard_mode:
                sorted_words, sorted_values, available_answers = \
                  calc_outcomes(rerun=False, verbose=self.verbose,
                              number_of_results_to_display=10,
                              known_wrong_positions_initial=av.known_wrong_positions,
                              available_answers_initial=av.remaining_words,
                              known_positions_initial=av.known_positions,
                              available_guesses_initial=av.remaining_guesses, mode=mode)
            else:
                sorted_words, sorted_values, available_answers = \
                  calc_outcomes(rerun=False, verbose=self.verbose,
                              number_of_results_to_display=10,
                              known_wrong_positions_initial=av.known_wrong_positions,
                              available_answers_initial=av.remaining_words,
                              known_positions_initial=av.known_positions,
                              available_guesses_initial=av.all_guesses, mode=mode)
                
        if len(guess_words) < 1:
            if start_word is not None:
                return start_word
            else:
                return(random.choice(sorted_words[0:10]))
    
        if sorted_words[0] in available_answers:
            self.add_decision_memory(sorted_words[0], guess_words, guess_results,
                                         sorted_words, sorted_values, available_answers)
            return sorted_words[0]
        else:
            sorted_word, sorted_value = None, None
            for sorted_word, *sorted_value in zip(sorted_words, *sorted_values):
                if sorted_word in available_answers:
                    break
            if sorted_value[0] < sorted_values[0][0] * pick_possible_factor and mode[0] != 'split':
                self.add_decision_memory(sorted_word, guess_words, guess_results,
                                             sorted_words, sorted_values, available_answers)
                return sorted_word
            elif sorted_value[0] * pick_possible_factor < sorted_values[0][0] and mode[0] == 'split':
                self.add_decision_memory(sorted_word, guess_words, guess_results,
                                             sorted_words, sorted_values, available_answers)
                return sorted_word
            else:
                self.add_decision_memory(sorted_words[0], guess_words, guess_results,
                                             sorted_words, sorted_values, available_answers)
                return sorted_words[0]

    def add_decision_memory(self, picked_word, guess_words, guess_results,
                                sorted_words, sorted_values, available_answers):
        # dictionary of past decision
        if len(guess_results) > 0:
            key_list = []
            for i in range(0, len(guess_results)):
                key_list.append(guess_words[i])
                key_list.append(guess_results[i])
            key_tuple = tuple(key_list)

            if not key_tuple in self.decision_memory.keys():
                self.decision_memory[key_tuple] = [picked_word, sorted_words,
                                                       sorted_values, available_answers]

    def check_decision_memory(self, guess_words, guess_results):
        if len(guess_results) > 0:
            key_list = []
            for i in range(0, len(guess_results)):
                key_list.append(guess_words[i])
                key_list.append(guess_results[i])
            key_tuple = tuple(key_list)

            if key_tuple in self.decision_memory.keys():
                return self.decision_memory[key_tuple]
            else:
                return None

    def get_hint(self, av, guess_words, guess_results, hint_type=None):
        if hint_type is None:
            if self.hint_type is None:
                hint_type = random.choice(self.hint_types)
            else:
                hint_type = self.hint_type
        if hint_type == 'jordan':
            return self.__getattribute__(hint_type)(av, guess_words, guess_results)
        return self.__getattribute__(hint_type)(av)
