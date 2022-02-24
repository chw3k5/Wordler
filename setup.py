import os
from distutils.core import setup

dir_name_this_file = os.path.dirname(os.path.realpath(__file__))
module_dir = os.path.join(dir_name_this_file, 'wordler')
data_dir = os.path.join(module_dir, 'data')

setup(name='Wordler',
      version='0.6',
      description='Wordle Emulator, and Suggestion Generator',
      author='Caleb Wheeler and Jordan Wheeler',
      packages=['wordler'],
      data_files=[('wordler/data', [os.path.join(data_dir, 'all_words.csv'),
                                    os.path.join(data_dir, 'allowed_guesses.csv'),
                                    os.path.join(data_dir, 'calculated_first_guesses.pkl')])]
      )
