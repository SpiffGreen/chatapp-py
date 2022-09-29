from flask import Flask, render_template, request, session, redirect, url_for
from lib.utils import valid_login, log_the_user_in, auth_required, stay_logged
import lib.db

app = Flask(__name__)
app.config["SECRET_KEY"] = "s3cr3tee_321"


@app.route('/')
def index():
  return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
@stay_logged
def login():
  error = None
  if request.method == 'POST':
    if valid_login(request.form['username'], request.form['password']):
        return log_the_user_in(request.form['username'], request.form['password'], app.config['SECRET_KEY'])
    else:
        error = 'Invalid username/password'
  # the code below is executed if the request method
  # was GET or the credentials were invalid
  return render_template('login.html', error=error)


@app.route('/logout')
def logout():
  # remove the token from the session if it is there
  session.pop('token', None)
  return redirect(url_for('index'))


@app.route('/register')
@stay_logged
def register():
  return render_template('register.html')

@app.route('/dashboard')
@auth_required
def dashboard():
  return render_template('dashboard.html')


@app.route('/friends')
@auth_required
def friends():
  return render_template('friends.html')


@app.route('/user/<u_id>')
@auth_required
def user():
  if not "token" in session:
    return redirect(url_for("login"))
  return render_template('friend.html')


if __name__ == '__main__':
  app.run(debug=True)
