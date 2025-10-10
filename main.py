from flask import Flask
app = Flask(__name__)
@app.route('/')
def home():
  return '<h1>This is the home page!<h1>'
@app.route('/user/<username>')
def user_screen(username):
  return f'''<h1>This is the user page!<h1>
            <p>Hello {username}! How are you?<p> 
            '''
app.run(debug=True)