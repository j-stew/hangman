### Running Hangman locally

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
Alternatively if you'd like to use virtualenvwrapper
```
mkvirtualenv hangman_env
workon hangman_env
```

#### Install requirements
```
pip install -r requirements.txt
```

#### Set environment variables
```
export DATABASE_URL=postgres://localhost/hangman
export DEBUG=True
export HOST=127.0.0.1
export PORT=5000
```

#### Create databases
```
psql -c 'CREATE DATABASE hangman'
psql -c 'CREATE DATABASE test_hangman'
```

#### Run locally
```
python run.py
```
Navigate to http://127.0.0.1:5000/login
