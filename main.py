from flask import Flask, redirect, url_for
app = Flask(__name__)
@app.route('/')
def home():
  return '''<h1>This is the home page!</h1>
            
          
  '''
@app.route('/user/<username>')
def user_screen(username):
  return f'''<h1>This is the user page!</h1>
            <p>Hello {username.title()}! How are you?</p>
            <a href='http://google.com/'>Click here!</a>
            '''
@app.route('/help')
def help():
  return redirect(url_for("home"))

app.run(debug=True)