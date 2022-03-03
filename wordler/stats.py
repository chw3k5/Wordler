import os
import math

dir_name_this_file = os.path.dirname(os.path.realpath(__file__))
stats_dir = os.path.join(dir_name_this_file, 'stats')
if not os.path.exists(stats_dir):
    os.mkdir(stats_dir)


class UserStats:
    max_hist_len = 30

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
        self.average_number_of_guesses = None

        # initialize the data
        self.read_stats()

    def __len__(self):
        return len(self.results_per_word)

    def read_stats(self):
        self.results_per_word = {}
        if os.path.exists(self.stats_file_path):
            with open(self.stats_file_path, 'r') as f:
                for raw_data_this_word in [raw_line.strip() for raw_line in f.readlines()]:
                    solution_word, guess_number, guess_words, guess_results = raw_data_this_word.split('|')
                    self.results_per_word[solution_word] = {'guess_number': int(guess_number),
                                                            'guesses': guess_words.split(','),
                                                            'guess_results': guess_results.split(',')}
        else:
            self.results_per_word = {}

    def write_stats(self):
        # prepare the data for writing.
        line_strs = []
        for solution_word in sorted(self.results_per_word.keys()):
            data_this_solution = self.results_per_word[solution_word]
            guess_number = data_this_solution['guess_number']
            guesses = data_this_solution['guesses']
            guess_results = data_this_solution['guess_results']
            line_str = f'{solution_word}|{guess_number}'
            for guess_index, guess_word in list(enumerate(guesses)):
                if guess_index == 0:
                    delimiter = '|'
                else:
                    delimiter = ','
                line_str += f'{delimiter}{guess_word}'
            for guess_index, guess_result in list(enumerate(guess_results)):
                if guess_index == 0:
                    delimiter = '|'
                else:
                    delimiter = ','
                line_str += f'{delimiter}{guess_result}'
            else:
                line_str += '\n'
            line_strs.append(line_str)
        # write the file
        with open(self.stats_file_path, 'w') as f:
            for line_str in line_strs:
                f.write(line_str)

    def add_game(self, solution_word, guesses,guess_results):
        guess_number = len(guesses)
        if guess_number == 0:
            raise ValueError(f'0 guesses is not a possible number of guesses to reach a puzzle solution.')

        self.results_per_word[solution_word] = {'guess_number': guess_number, 'guesses': guesses,'guess_results':guess_results}

    def get_prior_guesses(self):
        return {solution_word for solution_word in sorted(self.results_per_word.keys())}

    def del_stats_file(self):
        os.remove(self.stats_file_path)
        self.read_stats()

    def calc(self):
        self.by_number_of_guesses = {}
        guess_number_sum = 0
        for solution_word in sorted(self.results_per_word.keys()):
            guess_number = self.results_per_word[solution_word]['guess_number']
            guess_number_sum += guess_number
            if guess_number not in self.by_number_of_guesses:
                self.by_number_of_guesses[guess_number] = set()
            self.by_number_of_guesses[guess_number].add(solution_word)
        self.guess_number_sum = guess_number_sum
        self.average_number_of_guesses = float(guess_number_sum) / len(self.results_per_word)

    def get_histogram_str(self, verbose=False):
        # do calculations
        uni_squares_suffixes = [' ','\u258F', '\u258E', '\u258D', '\u258C', '\u258B', '\u258A', '\u2589', '\u2588']
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
        hard_mode_str = ''
        if self.hard_mode:
            hard_mode_str += ' in hard mode'
        hist_str = f'\n{self.username}{hard_mode_str}:\n' + \
                   f'   average number of guesses {"%1.3f" % self.average_number_of_guesses}\n' + \
                   f'   total   number of guesses {"%4d" % self.guess_number_sum}\n\n' + \
                   f'{"attempts": >8} |{"histogram": <{self.max_hist_len}}  {"total": >5}\n' + \
                   f'-----------------{"-" * self.max_hist_len}\n'
        for guess_number in range(1, sorted_guess_numbers[-1] + 1):
            if guess_number in self.by_number_of_guesses.keys():
                len_this_guess = len(self.by_number_of_guesses[guess_number])
            else:
                len_this_guess = 0
            number_of_x = math.floor(float(len_this_guess) / count_to_hist_space)
            remainder = math.ceil((float(len_this_guess) - number_of_x * count_to_hist_space) / count_to_hist_space * 8)
            hist_str += f'{guess_number: >8}  '
            for i in range(0, number_of_x):
                hist_str += "\u2588"
            hist_str += uni_squares_suffixes[remainder]
            for i in range(0, self.max_hist_len - number_of_x):
                hist_str += " "
            hist_str += f' {len_this_guess: >5}\n'

        # return/display results
        if verbose:
            print(hist_str)
        return hist_str

    def compute_guesses_per_len(self):
        self.calc()
        max_guesses = max(list(self.by_number_of_guesses.keys()))
        for key in self.results_per_word.keys(): # make all lists same size for sorting
            for j in range(0,max_guesses-len(self.results_per_word[key]['guesses'])):
                self.results_per_word[key]['guess_results'].append('na   ')

        dict_of_list = {}
        for j in range(0,max_guesses):
            dict_of_list[str(j)] = []
            for key in self.results_per_word.keys():
                dict_of_list[str(j)].append(self.results_per_word[key]['guess_results'][j])

        guess_numbers = []
        for key in self.results_per_word.keys():
            guess_numbers.append(self.results_per_word[key]['guess_number'])

        # just checking first 5 guesses
        zipped = zip(dict_of_list['0'],dict_of_list['1'],dict_of_list['2'],dict_of_list['3'],\
                         dict_of_list['4'],dict_of_list['5'],guess_numbers)
        sorted_lists = sorted(zipped)
        dict_of_list_sorted = {}
        guess_numbers_sorted = []

        dict_of_list_sorted['0'],dict_of_list_sorted['1'],dict_of_list_sorted['2'],dict_of_list_sorted['3'],\
          dict_of_list_sorted['4'],dict_of_list_sorted['5'],guess_numbers_sorted = zip(*sorted_lists)

        #for i in range(0,len(dict_of_list_sorted['0'])):
        #    print(dict_of_list_sorted['0'][i],dict_of_list_sorted['1'][i],dict_of_list_sorted['2'][i],\
        #              dict_of_list_sorted['3'][i],dict_of_list_sorted['4'][i],dict_of_list_sorted['5'][i],\
        #              guess_numbers_sorted[i])

        len_list = []
        guess_count_list = []
        
        for j in range(0,max_guesses):
            count = 1
            guess_count = 0
            for k in range(1,len(dict_of_list_sorted[str(j)])):
                if k == len(dict_of_list_sorted[str(j)])-1: # stop counting you have reached end of list
                    if count !=1:
                        if dict_of_list_sorted[str(j)][k] == dict_of_list_sorted[str(j)][k-1] and\
                          dict_of_list_sorted[str(j)][k] != 'na   ' and\
                          dict_of_list_sorted[str(j)][k] != '22222':
                            count = count +1
                            guess_count = guess_count + guess_numbers_sorted[k-1]-j-1
                        len_list.append(count)
                        guess_count_list.append(guess_count)
                    count = 1
                    guess_count = 0
                elif dict_of_list_sorted[str(j)][k] == dict_of_list_sorted[str(j)][k-1] and \
                  dict_of_list_sorted[str(j)][k] != 'na   ' and \
                  dict_of_list_sorted[str(j)][k] != '22222':
                    count = count +1
                    guess_count = guess_count + guess_numbers_sorted[k-1]-j-1
                else:
                    if count !=1:
                        guess_count = guess_count + guess_numbers_sorted[k-1]-j-1
                        len_list.append(count)
                        guess_count_list.append(guess_count)
                    count = 1
                    guess_count = 0


        guesses_per_word = []
        for i in range(0,len(len_list)):
            guesses_per_word.append(guess_count_list[i]/len_list[i])
        ave_list_len = []
        ave_list = []
        count_list = []
        for i in range(0,len(dict_of_list_sorted['0'])+1):
            if len_list.count(i)>0:
                count = 0
                total_guesses = 0
                for j in range(0,len(len_list)):
                    if len_list[j] == i:
                        count = count+1
                        total_guesses = total_guesses+guesses_per_word[j]
                count_list.append(count)
                ave_list.append(total_guesses/count)
                ave_list_len.append(i)

        print()
        print("list length| ave guess cost | n occurances")
        for i in range(0,len(ave_list)):
            print(f'   {"%3d" % ave_list_len[i]}     | '+ \
                      f'     {"%3.2f" % ave_list[i]}      |    {"%4d" % count_list[i]}       ') 
                               

if __name__ == '__main__':
    us = UserStats(username='trace_fastest_cost', hard_mode=False)
    us.get_histogram_str(verbose=True)
    #us.compute_guesses_per_len()
