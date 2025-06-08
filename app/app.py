from flask import Flask, render_template, request, redirect, session, url_for
from flask_socketio import SocketIO, send
import eventlet

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecret'
socketio = SocketIO(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nickname = request.form['nickname']
        session['nickname'] = nickname
        return redirect(url_for('chat'))
    return render_template('index.html')

@app.route('/chat')
def chat():
    nickname = session.get('nickname')
    if not nickname:
        return redirect('/')
    return render_template('chat.html', nickname=nickname)

@socketio.on('message')
def handle_message(msg):
    nickname = session.get('nickname', 'Anonymous')
    send(f"{nickname}: {msg}", broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
