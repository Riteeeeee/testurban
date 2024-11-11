from flask import Flask, request, render_template, redirect, url_for, session,jsonify
from flask_socketio import SocketIO, join_room, leave_room, send, emit
import random

global customers
customers={}

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"
socketio = SocketIO(app)

rooms = {}
ascii_letters=['A','B','C','D','E']

def generate_room_code(length: int, existing_codes: list[str]) -> str:
    while True:
        code_chars = [random.choice(ascii_letters) for _ in range(length)]
        code = ''.join(code_chars)
        if code not in existing_codes:
            return code

@app.route('/', methods=["GET", "POST"])
def home():
    print(">.............................")

    session.clear()
    if request.method == "POST":
        name = request.form.get('name')
        create = request.form.get('create', False)
        code = request.form.get('code')
        join = request.form.get('join', False)
        if not name:
            return render_template('home.html', error="Name is required", code=code)
        if create != False:
            room_code = generate_room_code(6, list(rooms.keys()))
            new_room = {
                'members': 0,
                'messages': []
            }
            rooms[room_code] = new_room
        if join != False:
            # no code
            if not code:
                return render_template('home.html', error="Please enter a room code to enter a chat room", name=name)
            # invalid code
            if code not in rooms:
                return render_template('home.html', error="Room code invalid", name=name)
            room_code = code
        session['room'] = room_code
        session['name'] = name
        customers[name]=room_code
        print(customers)
        print(name,room_code)
        return redirect(url_for('room'))
    else:
        return render_template('home.html')
# ...
@app.route('/api/customers')
def get_customers():
    return jsonify(customers)





@app.route('/room')
def room():
    room = session.get('room')
    name = session.get('name')
    # # if name is None or room is None or room not in rooms:
    # #     return redirect(url_for('home'))
    # messages = rooms[room]['messages']
    # return render_template('room.html', room=room, user=name, messages=messages)
    # if name is None or room is None or room not in rooms:
    #     return redirect(url_for('home'))

    try:
        del customers[name1]
        messages = ""
        return render_template('room.html', room=room, user=name, messages=messages)
    except:

        messages = ""
        return render_template('room.html', room=room, user=name, messages=messages)

@app.route('/test')
def test():
    return render_template('test.html',customers=customers)

...
@socketio.on('connect')
def handle_connect():
    name = session.get('name')
    room = session.get('room')
    if name is None or room is None:
        return
    if room not in rooms:
        leave_room(room)
    join_room(room)
    send({
        "sender": "",
        "message": f"{name} has entered the chat"
    }, to=room)

...

...
@socketio.on('message')
def handle_message(payload):
    room = session.get('room')
    name = session.get('name')
    if room not in rooms:
        return
    message = {
        "sender": name,
        "message": payload["message"]
    }
    send(message, to=room)
    rooms[room]["messages"].append(message)
...

...
@socketio.on('disconnect')
def handle_disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)
    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
        send({
        "message": "",
        "sender": ""
    }, to=room)
...


@socketio.on('join_room')
def handle_join_room(data):
    global name1
    name1 = data['name']
    room2 = data['room']

    # If room doesn't exist, create it
    if room2 not in rooms:
        rooms[room2] = {'members': 0, 'messages': []}

    # Join the room and increment members count
    join_room(room2)
    rooms[room2]['members'] += 1

    # Send a redirection event back to the client

    emit('redirect_to_room', {"url": url_for('room')}, to=request.sid)
    # Notify other users in the room
    send({"sender": "", "message": f"AGENT has entered the chat"}, to=room)

if __name__ == "__main__":
    socketio.run(app, debug=True,allow_unsafe_werkzeug=True)