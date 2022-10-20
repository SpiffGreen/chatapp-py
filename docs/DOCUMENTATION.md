# Chat App

## Functional Requirements

## Database Design
DB sql dumb - [Click Here](./chatapp.sql)

![DB design](./chatapp-db-design.png)

### Models
1. User - to store user details
2. Message - store message, with sender and receiver details
3. Friendship - stores state of relationship between two users, if accepted is true, both users are truely friends, i.e requesting user sends a friend request and the accepting user accepts the request.
  In the case of a user creating a friendship the default value of accepted is false, making it a friend request until ther receiving user accepts the reequest.

## Architectural Design

## Program Flow

## Tech stack and Dependencies
- Flask
- Flask-SQLAlchemy
- Flask-Socketio
- Bcrypt
- Eventlet