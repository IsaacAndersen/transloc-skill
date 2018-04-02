from flask import Flask, render_template
from flask_ask import Ask, statement, question, session


app = Flask(__name__)
ask = Ask(app, '/alexa_transloc')

desired_stops = [
	4188200, # "Campus Dr at Swift Ave (Westbound) (12007)"
	4195822, # "Swift Ave at 300 Swift (13009)"
	 ]

@app.route('/')
def homepage():
	return 'heyoooo'

@ask.launch
def start_skill():
	welcome_message = 'Hello!'
	return statement(welcome_message)

@ask.intent("Intent")
def share_something():
	busTime = ''
	return statement(bus_time)

@ask.intent("NoIntent")
def no_intent():
    bye_text = ''
    return statement(bye_text)


print(get_routes())

if __name__ == '__main__':
    app.run(debug=True)