import random
from narrow import AvailableWords


class GetHint:
    hint_types = ['caleb', 'natalie', 'jada']

    def __init__(self, hint_type=None, hard_mode=False):
        self.hard_mode = hard_mode
        if hint_type is None:
            self.hint_type = None
        else:
            self.hint_type = hint_type.strip().lower()
            if self.hint_type not in self.hint_types:
                raise KeyError(f"'{self.hint_type}' is not one of hint types: {self.hint_types}")

        self.av = None
        self.remaining_guesses = None

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
