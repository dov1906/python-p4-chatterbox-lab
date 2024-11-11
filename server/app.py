from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return "Welcome to the Message API!"

# GET /messages: returns all messages as JSON, ordered by created_at in ascending order
@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = [message.to_dict() for message in Message.query.order_by(Message.created_at.asc()).all()]

        response = make_response(messages, 200)
        return response

    elif request.method == 'POST':
        data = request.get_json()
        new_message = Message(
            body=data.get("body"),
            username=data.get("username")
        )

        db.session.add(new_message)
        db.session.commit()

        response = make_response(new_message.to_dict(), 201)
        return response

# PATCH /messages/<int:id> and DELETE /messages/<int:id>
@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def message_by_id(id):
    message = Message.query.get(id)

    if not message:
        response_body = {"message": "Message not found. Please try again."}
        response = make_response(response_body, 404)
        return response

    if request.method == 'GET':
        response = make_response(message.to_dict(), 200)
        return response

    elif request.method == 'PATCH':
        data = request.get_json()
        if 'body' in data:
            message.body = data['body']
            db.session.commit()

        response = make_response(message.to_dict(), 200)
        return response

    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()

        response_body = {"delete_successful": True, "message": "Message deleted."}
        response = make_response(response_body, 200)
        return response

if __name__ == '__main__':
    app.run(port=5555)
