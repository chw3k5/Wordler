# Preface
What started as lark, is now a fully featured 5-letter word puzzle for the terminal. 
This project is written entirely in Python3 using the Python standard libray.

# Installation 
Everything is the Python Standard Library, so there are
no packages to install. Developed in python 3.10.2, but made
to be backwards cooperative. Works and tested in
Terminal on OSX; git-bash, cmd, and PowerShell in Windows.

### Install Git
https://git-scm.com/downloads

Make sure to install gitbash it you are on Windows.

### Install Python
https://www.python.org/downloads/


### From gitbash or a terminal
### Clone this Repository (https://github.com/chw3k5/Wordler)
`git clone https://github.com/chw3k5/Wordler`

### change directory to where the code located
`cd Wordler/wordler`

# `Using play.py`
### commands from the terminal
`python play.py`

or 

`python3 play.py`

### More options for play.py
To see the (ongoing) options for play.py use:

`python play.py --help`

When new options are added, this help command is updated.

### More Python Help
If you wonder where python is installed use: 

`which python`

If you wonder what version of Python you are using, needs to be Python3: 

`python --version`

# Using `helper()` in `narrow.py`
This program gives you hints about remaining, ranked words 
based on results that you get from the Wordle game.

It is simple to run and works out-of-the-box.

### commands from the terminal
`python narrow.py`

or 

`python3 narrow.py`


# Updating
No promises, but you can always check for updates with

`git pull`

when in the Wordler directory.

# Manifesto
It is no fun to be dyslexic while Wordle continues to dominate casual 
conversation. If only there was some way to both feel superior and ruin it 
for everyone else...This system can be used to very quickly find the best guesses
and optimal path to a solution. All joking aside, this was a fun problem to
solve and in solving it, I was shown how clever this type of puzzle can be. 

## Is this cheating?
Using this system is cheating only if you acknowledge that having an
extra circuit in your brain to easily parse words and recognize letter ordering
is *also* cheating.

If that is not enough for you, then think of it as a simulation to help
you test and hone your Wordle skills. Because all modern chess is informed by
simulation, and Wordle is completely equivalent to chess, right?

The code will also create a shareable output, to make sure all of your Twitter/group 
chat/familial friends know how great you are.