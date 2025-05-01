from flask import Flask, render_template, jsonify, request, session
import requests
import random

app = Flask(__name__)
app.secret_key = 'HelloGrader'

#Randomly scrape the github page to select a word to be used for the hangman game
def getWord():
    url = 'https://raw.githubusercontent.com/Xethron/Hangman/master/words.txt'
    r = requests.get(url)

    words = r.text.splitlines()
    random_word = random.choice(words).strip()
    return random_word.upper()

#Starts the game and chooses a random word. Initializes session objects to empty and max number of guesses.
@app.route('/startGame')
def startGame():
    session['word'] = getWord()
    session['guesses'] = []
    session['remaining_guesses'] = 6
    return jsonify({
        'word' : session['word'],
        'remaining_guesses' : session['remaining_guesses'],
        'display' : getDisplay()
    })

#Switch the _ with guessed letters of target word
def getDisplay():
    display = []
    for char in session['word']:
        if char in session['guesses']:
            display.append(char)
        else:
            display.append('_')
    display = ' '.join(display)
    return display

#for when first visit to page starts game automatically so user does not have to click button
@app.route('/')
def show_page():
    if 'word' not in session:  
        startGame()
    return render_template('index.html')


@app.route('/guess', methods=['POST'])
def makeGuess():
    letter = request.json['letter'].upper()
    #Check if letter has been guessed. See if letter is in word if not subtract one from guesses
    if letter not in session['guesses']:
        session['guesses'].append(letter)
        session.modified = True  # ← Add this line
        if letter not in session['word']:
            session['remaining_guesses'] -= 1
    
    #Switch the _ with guessed letters of target word
    getDisplay()

    #checks to see if game is won, lost, or to continue
    status = 'playing'
    display = getDisplay()
    if '_' not in display:
        status = 'win'
    elif session["remaining_guesses"] <= 0:
        status = 'loss'
    return jsonify({
        'display': display,
        'status': status,
        'remaining_guesses': session['remaining_guesses'],
        'word' : session['word'] if status == 'loss' else None
        })



if __name__ == '__main__':
    app.run(debug=True)