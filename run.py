from hangman import hangman_app

hangman_app.run(host=hangman_app.config['HOST'],
    port=int(hangman_app.config['PORT']))
