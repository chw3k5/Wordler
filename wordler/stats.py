import os


dir_name_this_file = os.path.dirname(os.path.realpath(__file__))
stats_dir = os.path.join(dir_name_this_file, 'stats')
if not os.path.exists(stats_dir):
    os.mkdir(stats_dir)


class UserStats:
    def __init__(self, username, verbose=False):
        # settings
        self.username = username
        self.verbose = verbose
        self.stats_file_path = os.path.join(stats_dir, f'{self.username}.psv')

        # data attributes
        self.results_per_word = None

        # initialize the data
        self.read_stats()

    def read_stats(self):
        if os.path.exists(self.stats_file_path):
            with open(self.stats_file_path, 'r') as f:
                for raw_data_this_word in [raw_line.strip() for raw_line in f.readlines()]:
                    solution_word, guess_number, *guess_words = raw_data_this_word.split('|')
                    self.results_per_word[solution_word] = {'guess_number': guess_number,
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
