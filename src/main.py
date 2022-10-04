from traceback import print_list
from flask import Flask, render_template, request, session, redirect, url_for, abort, jsonify, escape
from lib.utils import valid_login, log_the_user_in, auth_required, stay_logged
from flask_marshmallow import Marshmallow
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt
from sqlalchemy import or_, and_
from sqlalchemy.sql import func, expression
from lib.config import getConfig
from flask_socketio import SocketIO, emit
import logging
import jwt

def addMessage(senderID, receiverID, message):
  message = Message(message=message, senderId=senderID, receiverId=receiverID)
  db.session.add(message)
  db.session.commit()

# Env Variables
SECRET = getConfig().get("SECRET_KEY")
DATABASE_URI = getConfig().get("DATABASE_URI")

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET
app.secret_key = SECRET
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI


# Init
db = SQLAlchemy()
db.init_app(app)
socketio = SocketIO(app)
bcrypt = Bcrypt(app)
ma = Marshmallow(app)

# User Class/Model
class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100))
  email = db.Column(db.String(100), unique=True)
  password = db.Column(db.String(250))
  session_id = db.Column(db.String(200))
  created_on = db.Column(db.DateTime, server_default=db.func.now())
  updated_on = db.Column(db.DateTime, server_default=db.func.now(), onupdate=datetime.utcnow)

  def __init__(self, name, email, password):
    self.name = name
    self.email = email
    self.password = password

class UserSchema(ma.Schema):
  class Meta:
    model = User
    fields = ("id", "name", "email", "created_on", "updated_on")

# Init schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)
class Message(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  message = db.Column(db.String(250))
  senderId = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
  sender = db.relationship("User", backref="messages_sent", foreign_keys=[senderId])
  receiverId = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
  receiver = db.relationship("User", backref="messages_received", foreign_keys=[receiverId])
  created_on = db.Column(db.DateTime, server_default=db.func.now())
  updated_on = db.Column(db.DateTime, server_default=db.func.now(), onupdate=datetime.utcnow)

  def __init__(self, message, senderId, receiverId):
    self.message = message
    self.senderId = senderId
    self.receiverId = receiverId

class MessageSchema(ma.Schema):
  class Meta:
    model = Message
    include_fk = True
    fields = ("id", "message", "senderId", "receiverId", "created_on", "updated_on", "sender", "receiver")

# Init schema
message_schema = MessageSchema()
messages_schema = MessageSchema(many=True)

class Friendship(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  accepted = db.Column(db.Boolean, server_default=expression.false(), nullable=False)
  requestingUserId = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
  sender = db.relationship("User", backref="friendship_sent", foreign_keys=[requestingUserId])
  acceptingUserId = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
  receiver = db.relationship("User", backref="friendship_received", foreign_keys=[acceptingUserId])
  created_on = db.Column(db.DateTime, server_default=db.func.now())
  updated_on = db.Column(db.DateTime, server_default=db.func.now(), onupdate=datetime.utcnow)

  def __init__(self, accepted, requestingUserId, acceptingUserId):
    self.accepted = accepted
    self.requestingUserId = requestingUserId
    self.acceptingUserId = acceptingUserId

class FriendshipSchema(ma.Schema):
  class Meta:
    model = Friendship
    include_fk = True
    fields = ("id", "accepted", "requestingUserId", "acceptingUserId", "created_on", "updated_on", "sender", "receiver")

# Init schema
friendship_schema = FriendshipSchema()
friendships_schema = FriendshipSchema(many=True)

with app.app_context():
  db.create_all()

# Socketio event handlers
@socketio.on('connect')
@auth_required
def socket_connect(userID):
  user = User.query.filter_by(id=userID).first()
  user.session_id = request.sid
  db.session.commit()

@socketio.on('disconnect')
@auth_required
def socket_disconnect(userID):
  user = User.query.filter_by(id=userID).first()
  user.session_id = ""
  db.session.commit()

@socketio.on('send_message')
def socket_send_message(data):
  message = escape(data["message"])
  receiver = User.query.get(data["chatID"])
  sender = User.query.filter(User.session_id == request.sid).first()
  if receiver.session_id:
    emit("receive_message", {"message": message, "sender": user_schema.dump(sender)}, to=receiver.session_id)

# Route definitions
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
      logging.exception("An exception was thrown!")
      error = "Something went wrong, please check"
  return render_template('register.html', error=error)

@app.route('/dashboard')
@auth_required
def dashboard(userID):
  chatid = request.args.get("chatid")
  user = User.query.filter_by(id=userID).first()
  # addMessage(senderID=int(userID), receiverID=2, message="Hello Nicky")
  # Fetch and group messages
  chats = Message.query.filter(or_(Message.senderId == userID, Message.receiverId == userID)).order_by(Message.created_on.desc()).group_by(Message.receiverId).all()
  chats = messages_schema.dump(chats)
  for message in chats:
    message["sender"] = user_schema.dump(message["sender"])
    message["receiver"] = user_schema.dump(message["receiver"])
  # print(chats)
  return render_template('dashboard.html', user=user, chats=chats, chatid=chatid)

@app.route('/profile')
@auth_required
def profile(userID):
  user = User.query.filter_by(id=userID).first()
  return render_template('profile.html', user=user)


@app.route('/friend-requests')
@auth_required
def friend_requests(userID):
  f_requests = Friendship.query.filter(and_(Friendship.acceptingUserId == userID, Friendship.accepted == False)).all()
  f_requests = friendships_schema.dump(f_requests)
  # print(f_requests)
  for f_req in f_requests:
    f_req["sender"] = user_schema.dump(f_req["sender"])
    f_req["receiver"] = user_schema.dump(f_req["receiver"])
  
  return render_template("friend-requests.html", f_requests=f_requests)

@app.route('/friends')
@auth_required
def friends(userID):
  # get accepted friendships user requested, then get all users with the matching ids
  friendships = Friendship.query.filter(or_(Friendship.requestingUserId == userID, Friendship.acceptingUserId == userID), Friendship.accepted == True).all()
  # friendIDs = list(map(lambda friend: friend.acceptingUserId, friendships))
  friendIDs = []
  for friend in friendships:
    if friend.requestingUserId == userID:
      friendIDs.append(friend.acceptingUserId)
    else:
      friendIDs.append(friend.requestingUserId)

  users = User.query.filter(User.id.in_(friendIDs)).all()
  # Get other users, not friends. I.e get users excluding friends and current user
  friendIDs.append(userID)
  others = User.query.filter(User.id.notin_(friendIDs)).all()

  return render_template('friends.html', friends=users, others=others)

@app.route('/api/find')
@auth_required
def find_friends(userID):
  users = User.query.filter(User.name.ilike('%' + request.args["search"] + '%')).all()
  users = users_schema.dump(users)
  return jsonify(users)

# Remove a friend
@app.route('/api/remove-friend', methods=["POST"])
@auth_required
def remove_friend(userID):
  user_id = None
  try:
    friendship_id = request.args.get("friendship_id")
    if friendship_id:
      friendship = Friendship.query.filter(Friendship.id == friendship_id).first()
    else:
      user_id = request.args.get("user_id")
      friendship = Friendship.query.filter(or_(and_(Friendship.acceptingUserId == user_id, Friendship.requestingUserId == userID), and_(Friendship.acceptingUserId == userID, Friendship.requestingUserId == user_id))).first()
    db.session.delete(friendship)
    db.session.commit()
    return jsonify({ "success": True })
  except:
    logging.exception("An exception was thrown!")
    if not friendship_id:
      return jsonify({ "success": False, "message": "Include valid user id" })

# Remove a friend
@app.route('/api/add-friend', methods=["POST"])
@auth_required
def add_friend(userID):
  user_id = None
  try:
    friendship_id = request.args.get("friendship_id")
    if friendship_id:
      friendship_id = int(friendship_id)
      friendship = Friendship.query.filter(Friendship.id == friendship_id).first()
      friendship.accepted = True
    else:
      user_id = request.args.get("user_id")
      friendship = Friendship(accepted=False, requestingUserId=userID, acceptingUserId=user_id)
      db.session.add(friendship)

    db.session.commit()
    return jsonify({ "success": True })
  except:
    logging.exception("An exception was thrown!")
    if not user_id:
      return jsonify({ "success": False, "message": "Include valid user id" })



@app.route('/user/<int:user_id>')
@auth_required
def user(user_id, userID):
  user = User.query.get_or_404(user_id)
  friendship = Friendship.query.filter(or_(and_(Friendship.requestingUserId == userID, Friendship.acceptingUserId == user_id), and_(Friendship.acceptingUserId == userID, Friendship.requestingUserId == user_id))).first()
  return render_template('user.html', user=user, friendship=friendship, userID=userID)


if __name__ == '__main__':
  socketio.run(app, port=5000, debug=True)
  # app.run(debug=True)

