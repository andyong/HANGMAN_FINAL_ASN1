# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START app]
import logging
import urllib2
import json
import os
import re

from flask import Flask, flash, render_template, request, session, redirect, url_for, escape

app = Flask(__name__)
#app.secret_key = '\xfd\x0b\xcf\x90\xb3f}\xe54\xfeX\xdd\xf2\x96X\xe23\xe1\x85{\x91\x0c\x9e1'
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    #session['word_to_guess'] = GenerateRandomWord()
    return render_template('start.html')

@app.route('/success')
def success():
    #session['word_to_guess'] = GenerateRandomWord()
    session['no_of_games_won'] = 0
    session['no_of_games_lost'] = 0
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    letterNumber = "^[a-zA-Z0-9]+$";
    error = None
    if request.method == 'POST':
        if re.match(letterNumber, request.form['username']) and re.match(letterNumber, request.form['password']):
            #session['logged_in'] = True
            return redirect(url_for('success'))
        elif request.form['username'] == '' or request.form['password'] == '':
            error = '1 or more field requires input'
        else:
            #flash('You were successfully logged in')
            error = 'Invalid credentials'

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    session.clear()
    return redirect(url_for('index'))

@app.route('/new_game', methods=['POST'])
def new_game():
    init_game()
    #logging.debug(word_to_guess)
    result ={
    "word_length" : len(session['word_to_guess'])
    }

    return json.dumps(result) #return string of result

def init_game():
    #global word_to_guess
    #global word_state
    #global bad_guesses
    #global no_of_games_won
    #global no_of_games_lost

    session['word_to_guess'] = GenerateRandomWord() #new word
    session['word_state'] = init_word_state(session['word_to_guess'])
    session['bad_guesses'] = 0
    pass

def init_word_state(words):
    return "_" * len(words) #length of word in _

def GenerateRandomWord():
    urlreq = urllib2.Request('http://setgetgo.com/randomword/get.php')
    response = urllib2.urlopen(urlreq)
    word = response.read()
    return word

@app.route('/check_letter', methods=['POST'])
def check_letter():
    if request.json is None:
        return 'Error! Input of a letter is required!'

    guess_letter = request.json
    #logging.debug(guess_letter['guess'])

    return check_input(guess_letter['guess'])

def check_input(input):
    #global word_to_guess
    #global word_state
    #global bad_guesses
    #global no_of_games_won
    #global no_of_games_lost
    input = str(input).lower()

    if input in session['word_to_guess']:
        fill_in_letter(input)
    else:
        session['bad_guesses'] += 1
        #logging.debug(bad_guesses)

    if session['bad_guesses'] == 8: #lose
        result = {
        "game_state" : "LOSE",
        "word_state" : session['word_state'],
        "answer" : session['word_to_guess'],
        }
        session['no_of_games_lost'] += 1

    elif session['word_to_guess'] == session['word_state']: #win
        result = {
        "game_state" : "WIN",
        "word_state" : session['word_state'],
        }
        session['no_of_games_won'] += 1

    else: #ongoing
        result = {
        "game_state" : "ONGOING",
        "word_state" : session['word_state'],
        "bad_guesses" : session['bad_guesses']
        }
    return json.dumps(result)

def fill_in_letter(guess):
     #global word_to_guess
     #global word_state
     x = list(session['word_state'])
     if guess in session['word_to_guess']:
         indices = find_all(session['word_to_guess'], guess)
         x = list(session['word_state'])
         for i in indices:
            x[i] = guess
            session['word_state'] = "".join(x)

     #logging.debug(word_state)
     return session['word_state']

def find_all(word, input):
    return [i for i, letter in enumerate(word) if letter == input]

@app.route('/score', methods=['GET'])
def get_score():
    #global no_of_games_won
    #global no_of_games_lost
    #if 'games_won' not in request.session:

    result = {
        "games_won" : session['no_of_games_won'],
        "games_lost" : session['no_of_games_lost']
    }
    #logging.debug(no_of_games_won)
    #logging.debug(session['games_won'])
    #logging.debug(session['gno_of_games_lost'])
    #logging.debug(no_of_games_lost)
    return json.dumps(result)

@app.route('/score', methods=['DELETE'])
def reset_score():
    #global no_of_games_won
    #global no_of_games_lost
    #no_of_games_won = no_of_games_lost = 0
    session['no_of_games_won'] = 0
    session['no_of_games_lost'] = 0
    result = {
        "games_won" : session['no_of_games_won'],
        "games_lost" : session['no_of_games_lost']
    }
    #logging.debug(no_of_games_won)
    #logging.debug(no_of_games_lost)
    return json.dumps(result)

if __name__ == "__main__":
    # set the secret key.  keep this really secret:
    app.run(debug=True)

@app.errorhandler(400)
def client_error(e):
    logging.exception('An error occurred during a request')
    return redirect('/success')
    #return 'Bad Request.', 400

@app.errorhandler(403)
def user_error(e):
    logging.exception('An error occurred during a request')
    #return redirect('/', code = 302)
    return redirect('/success')
    #return 'Forbidden.', 403

@app.errorhandler(404)
def not_found_error(e):
    logging.exception('An error occurred during a request')
    return redirect('/success')
    #return 'Error, requested resource could not be found.', 404

@app.errorhandler(405)
def not_allowed_error(e):
    logging.exception('An error occurred during a request')
    return redirect('/success')

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return redirect('/success')
    #return 'An internal error occurred.', 500
# [END app]
