import random
from narrow import AvailableWords


class GetHint:
    hint_types = ['caleb']

    def __init__(self, hint_type=None):
        if hint_type is None:
            self.hint_type = None
        else:
            self.hint_type = hint_type.strip().lower()
            if hint_type not in self.hint_types:
                raise KeyError(f"'{self.hint_type}' is not one of hint types: {self.hint_types}")

        self.av = None

    def caleb(self, guess_words, guess_results):
        self.av = AvailableWords(verbose=False)
        for guess_word, results_this_guess in zip(guess_words, guess_results):
            self.av.ask_guess(guess_word=guess_word, results=results_this_guess)
        top_five_words = []
        ranked_words_by_rank = self.av.ranked_words_by_rank
        for word_index, (word, rank) in list(enumerate(ranked_words_by_rank)):
            top_five_words.append(word)
            if word_index > 3:
                break
        return random.choice(top_five_words)

    def get_hint(self, guess_words, guess_results):
        if self.hint_type is None:
            hint_type = random.choice(self.hint_types)
        else:
            hint_type = self.hint_type
        return self.__getattribute__(hint_type)(guess_words=guess_words, guess_results=guess_results)


if __name__ == '__main__':
    get_hint = GetHint()
    guess_words = ['alter', 'owner', 'miser', 'sheer']
    guess_results = ['00022', '00022', '00122', '11022']
    print(get_hint.get_hint(guess_words=guess_words, guess_results=guess_results))
