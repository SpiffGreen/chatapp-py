from flask import redirect, url_for, session, abort
from datetime import datetime, timedelta
from lib.config import getConfig
from functools import wraps
import logging
import jwt

# A list of helper functions to run

SECRET = getConfig().get("SECRET_KEY")

def valid_login(username, password):
  # perform verification
  return True

def log_the_user_in(username, password):
  try:
    # encode the payload to set the details
    token = jwt.encode({
      "userId": 1, # TODO: Check the login later
      'exp' : datetime.utcnow() + timedelta(minutes = 30)
    }, SECRET)
    session["token"] = token
    return redirect(url_for("dashboard"))
  except:
    logging.exception("An exception was thrown!")
    return abort(500)

def auth_required(func):
  @wraps(func)
  def wrapper_func(*args, **kwargs):
    if not "token" in session:
      return redirect(url_for("login"))
    try:
      data = jwt.decode(session["token"], SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
      return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
      return 'Invalid token. Please log in again.'
    except:
      logging.exception("An exception was thrown!")
      return "Custom Error"
    return func(userID=data['userId'], *args, **kwargs)
  return wrapper_func

def stay_logged(func):
  @wraps(func)
  def wrapper_func(*args, **kwargs):
    if "token" in session:
      return redirect(url_for("dashboard"))
    return func(*args, **kwargs)
  return wrapper_func