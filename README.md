Mr. Hangman is a guessing game that allows users to guess letters in a
randomly selected word. The app comes with 240 common English words.
You can add more words to the game by adding words to the words.txt file.

Features I want to add:
* 'stick' hangman graphic with HTML5 canvas element
* setup.sh adds environment variables to virtualenvwrapper

### Running [Hangman](http://mr-hangman.herokuapp.com/login) locally
Set-up should be 3 terminal commands

Assumes:
  1. Mac OS X
  2. Postgresql set-up locally
  3. pip and virtualenvwrapper installed

#### Clone the project
```
git clone https://github.com/j-stew/hangman.git
cd hangman
```

#### Run setup script
```
source setup.sh
```

##### After initial set-up, run app locally with:
```
python run.py
```
Navigate to http://127.0.0.1:5000/login
