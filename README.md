### Running [Hangman](http://mr-hangman.herokuapp.com/login) locally
Set-up should be 6 terminal commands (assuming OSX and Postgresql set-up)

#### Clone the project
```
git clone https://github.com/j-stew/hangman.git
cd hangman
```

#### Create a virtualenv
```
virtualenv hangman_env
source hangman_env/bin/activate
```
Alternatively, if you prefer virtualenvwrapper
```
mkvirtualenv hangman_env
workon hangman_env
```

#### Run setup script
```
bash setup.sh
```

#### Run locally
```
python run.py
```
Navigate to http://127.0.0.1:5000/login
