from flask import Flask, render_template, request
from lib.utils import valid_login, log_the_user_in

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'],
                       request.form['password']):
            return log_the_user_in(request.form['username'])
        else:
            error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('login.html', error=error)

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/friends')
def friends():
    return render_template('friends.html')

@app.route('/user/<u_id>')
def user():
    return render_template('friend.html')

if __name__ == '__main__':
   app.run(debug=True)