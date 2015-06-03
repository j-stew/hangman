from hangman import hangman_app

port = int(os.environ.get("PORT", 5000))
hangman_app.run(host='0.0.0.0', port=port)
