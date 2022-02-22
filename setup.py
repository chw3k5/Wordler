import os
from distutils.core import setup

setup(name='Wordler',
      version='0.5',
      description='Wordle Emulator, and Suggestion Generator',
      author='Caleb Wheeler and Jordan Wheeler',
      packages=['wordler'],
      data_files=[('wordler', [os.path.join('wordler', 'all_words.csv'),
                               os.path.join('wordler', 'allowed_guesses.csv'),
                               os.path.join('wordler', 'calculated_first_guesses.pkl')])]
      )
