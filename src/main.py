from copyreg import constructor
from flask import Flask, render_template, request, session, redirect, url_for, abort, jsonify
from lib.utils import valid_login, log_the_user_in, auth_required, stay_logged
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.sql import func
from lib.config import getConfig
import logging
import jwt

# import lib.db

# Env Variables
SECRET = getConfig().get("SECRET_KEY")
DATABASE_URI = getConfig().get("DATABASE_URI")

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = SECRET
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI


# Init db
db = SQLAlchemy()
db.init_app(app)
bcrypt = Bcrypt(app)

# User Class/Model
class User(db.Model, SerializerMixin):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100))
  email = db.Column(db.String(100), unique=True)
  password = db.Column(db.String(250))

  def __init__(self, name, email, password):
    self.name = name
    self.email = email
    self.password = password

class Message(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  message = db.Column(db.String(250))
  userId = db.Column(db.Integer)
  toUserId = db.Column(db.Integer)

  def __init__(self, message, userId, toUserId):
    self.message = message
    self.userId = userId
    self.toUserId = toUserId

class Friendship(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  accepted = db.Column(db.Boolean, default=False)
  requestingUserId = db.Column(db.Integer)
  acceptingUserId = db.Column(db.Integer)

  def __init__(self, accepted, requestingUserId, acceptingUserId):
    self.accepted = accepted
    self.requestingUserId = requestingUserId
    self.acceptingUserId = acceptingUserId

with app.app_context():
  db.create_all()


@app.route('/')
def index():
  return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
@stay_logged
def login():
  error = None
  if request.method == 'POST':
    if valid_login(request.form['email'], request.form['password']):
        # return log_the_user_in(request.form['username'], request.form['password'])
        try:
          user = User.query.filter_by(email=request.form['email']).first()
          if not user:
            error = 'Invalid username/password'
          elif not bcrypt.check_password_hash(user.password, request.form['password']):
            error = 'Invalid username/password'
          else:
            # encode the payload to set the details
            token = jwt.encode({
              "userId": user.id, # TODO: Check the login later
              'exp' : datetime.utcnow() + timedelta(minutes = 30)
            }, SECRET)
            session["token"] = token
            return redirect(url_for("dashboard"))
        except:
          logging.exception("An exception was thrown!")
          return abort(500)
    else:
        error = 'Invalid username/password'
  # the code below is executed if the request method
  # was GET or the credentials were invalid
  return render_template('login.html', error=error)


@app.route('/logout')
def logout():
  # remove the token from the session if it is there
  session.pop('token', None)
  return redirect(url_for('login'))


@app.route('/register', methods=["GET", "POST"])
@stay_logged
def register():
  error = None
  if request.method == 'POST':
    try:
      name = request.form['name']
      email = request.form['email']
      password = request.form['password']
      user = User.query.filter(User.email == email).first()
      if user:
        error = "User already exists"
        return render_template('register.html', error=error)
      computed_password = bcrypt.generate_password_hash(password)
      user = User(name=name, email=email, password=computed_password)
      db.session.add(user)
      db.session.commit()
      return redirect(url_for('login'))
    except:
      error = "Something went wrong, please check"
  return render_template('register.html', error=error)

@app.route('/dashboard')
@auth_required
def dashboard(userID):
  user = User.query.filter_by(id=userID).first()
  print(user)
  
  return render_template('dashboard.html', user=user)

@app.route('/profile')
@auth_required
def profile(userID):
  user = User.query.filter_by(id=userID).first()
  print(user)
  
  return render_template('profile.html', user=user)


@app.route('/friends')
@auth_required
def friends(userID):
  # get accepted friendships user requested, then get all users with the matching ids
  friendships = Friendship.query.filter(Friendship.requestingUserId == userID, Friendship.accepted == True).all()
  friendIDs = list(map(lambda friend: friend.acceptingUserId, friendships))
  users = User.query.filter(User.id.in_(friendIDs)).all()

  # Get other users, not friends. I.e get users excluding friends and current user
  friendIDs.append(userID)
  others = User.query.filter(User.id.notin_(friendIDs)).all()

  return render_template('friends.html', friends=users, others=others)

@app.route('/api/find')
@auth_required
def find_friends(userID):
  users = User.query.filter(User.name.ilike('%' + request.args["search"] + '%')).all()
  users = list(map(lambda user: user.to_dict(only=('id', 'name', 'email')), users))
  return jsonify(users)

# Remove a friend
@app.route('/api/remove-friend')
@auth_required
def remove_friend(userID):
  user_id = None
  try:
    user_id = request.args["user_id"]
    friendship = Friendship.qeury.filter(Friendship.acceptingUserId == user_id, Friendship.requestingUserId == userID, Friendship.accepted == True)
    if friendship:
      db.session.delete(friendship)
      db.session.commit()
    return jsonify({ "success": True })
  except:
    if not user_id:
      return jsonify({ "success": False, "message": "Include valid user id" })

# Remove a friend
@app.route('/api/add-friend')
@auth_required
def add_friend(userID):
  user_id = None
  try:
    user_id = int(request.args["user_id"])
    newFriendship = Friendship(accepted=False, requestingUserId=int(userID), acceptingUserId=user_id)
    db.session.add(newFriendship)
    db.session.commit()
    return jsonify({ "success": True })
  except:
    if not user_id:
      return jsonify({ "success": False, "message": "Include valid user id" })



@app.route('/user/<int:user_id>')
@auth_required
def user(user_id, userID):
  user = User.query.get_or_404(user_id)
  friendship = Friendship.query.filter(Friendship.requestingUserId == userID, Friendship.acceptingUserId == user_id).first()
  return render_template('user.html', user=user, friendship=friendship)


if __name__ == '__main__':
  app.run(debug=True)
