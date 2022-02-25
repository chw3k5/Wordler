import os


dir_name_this_file = os.path.dirname(os.path.realpath(__file__))
stats_dir = os.path.join(dir_name_this_file, 'stats')
if not os.path.exists(stats_dir):
    os.mkdir(stats_dir)


class UserStats:
    max_hist_len = 20

    def __init__(self, username, hard_mode=False):
        # settings
        self.username = username
        self.hard_mode = hard_mode
        if self.hard_mode:
            self.stats_file_path = os.path.join(stats_dir, f'{self.username}_hard.psv')
        else:
            self.stats_file_path = os.path.join(stats_dir, f'{self.username}.psv')

        # data attributes
        self.results_per_word = None
        self.by_number_of_guesses = None

        # initialize the data
        self.read_stats()

    def read_stats(self):
        self.results_per_word = {}
        if os.path.exists(self.stats_file_path):
            with open(self.stats_file_path, 'r') as f:
                for raw_data_this_word in [raw_line.strip() for raw_line in f.readlines()]:
                    solution_word, guess_number, guess_words = raw_data_this_word.split('|')
                    self.results_per_word[solution_word] = {'guess_number': int(guess_number),
                                                            'guesses': guess_words.split(',')}
        else:
            self.results_per_word = {}

    def write_stats(self):
        # prepare the data for writing.
        line_strs = []
        for solution_word in sorted(self.results_per_word.keys()):
            data_this_solution = self.results_per_word[solution_word]
            guess_number = data_this_solution['guess_number']
            guesses = data_this_solution['guesses']
            line_str = f'{solution_word}|{guess_number}'
            for guess_index, guess_word in list(enumerate(guesses)):
                if guess_index == 0:
                    delimiter = '|'
                else:
                    delimiter = ','
                line_str += f'{delimiter}{guess_word}'
            else:
                line_str += '\n'
            line_strs.append(line_str)
        # write the file
        with open(self.stats_file_path, 'w') as f:
            for line_str in line_strs:
                f.write(line_str)

    def add_game(self, solution_word, guesses):
        guess_number = len(guesses)
        if guess_number == 0:
            raise ValueError(f'0 guesses is not a possible number of guesses to reach a puzzle solution.')

        self.results_per_word[solution_word] = {'guess_number': guess_number, 'guesses': guesses}

    def get_prior_guesses(self):
        return [solution_word for solution_word in sorted(self.results_per_word.keys())]

    def del_stats_file(self):
        os.remove(self.stats_file_path)
        self.read_stats()
        
    def calc(self):
        self.by_number_of_guesses = {}
        for solution_word in sorted(self.results_per_word.keys()):
            guess_number = self.results_per_word[solution_word]['guess_number']
            if guess_number not in self.by_number_of_guesses:
                self.by_number_of_guesses[guess_number] = set()
            self.by_number_of_guesses[guess_number].add(solution_word)

    def get_histogram_str(self, verbose=False):
        # do calculations
        self.calc()
        max_len = -1
        sorted_guess_numbers = sorted(self.by_number_of_guesses.keys())
        for guess_number in sorted_guess_numbers:
            len_this_guess = len(self.by_number_of_guesses[guess_number])
            if len_this_guess > max_len:
                max_len = len_this_guess
        floor_div = max_len // self.max_hist_len
        count_to_hist_space = float(floor_div + 1)

        # generate in-line histogram
        hist_str = ''
        for guess_number in sorted_guess_numbers:
            len_this_guess = len(self.by_number_of_guesses[guess_number])
            number_of_x = round(float(len_this_guess) / count_to_hist_space)
            hist_str += f'{guess_number: >2} |{"x" * number_of_x: <{self.max_hist_len}}  {len_this_guess: >5}\n'

        # return/display results
        if verbose:
            print(hist_str)
        return hist_str


if __name__ == '__main__':
    us = UserStats(username='Natalie', hard_mode=False)
    us.get_histogram_str(verbose=True)
