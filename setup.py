import os
from distutils.core import setup

setup(name='Wordler',
      version='0.3',
      description='Wordle Emulator, and Suggestion Generator',
      author='Caleb Wheeler',
      author_email='chw3k5#gmail.com',
      packages=['wordler'],
      data_files=[('wordler', [os.path.join('wordler', 'all_words.csv'),
                               os.path.join('wordler', 'allowed_guesses.csv')])]
      )
