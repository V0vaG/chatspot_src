# ✅ Do this first — before anything else!
import eventlet
eventlet.monkey_patch()

# Then continue with your imports
from flask import Flask, send_file, render_template, request, redirect, session, url_for, send_from_directory
from flask_socketio import SocketIO, send, emit
import os
from werkzeug.utils import secure_filename
import qrcode
from io import BytesIO

from hotspot import start_hotspot

port = 5000


hot_spot_enabled = True  # Set to True to enable hotspot mode

print(f"hot_spot: {hot_spot_enabled}")

if  hot_spot_enabled:
    ssid = 'ChatSpot'
    password = '12345678'
    site_ip = '192.168.4.1'

    start_hotspot(ssid, password, site_ip, 'wlan0')
    
    print(f"SSID: {ssid}, password: {password}")
    print(f"Server running on http://{site_ip}:{port}")



app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecret'
socketio = SocketIO(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit



connected_users = 0


@app.route('/qr')
def generate_qr():
    ssid = ssid
    password = password
    url = f"http://{site_ip}:{port}"

    wifi_qr_text = f"WIFI:T:WPA;S:{ssid};P:{password};;\n{url}"
    img = qrcode.make(wifi_qr_text)
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')


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

@socketio.on('connect')
def on_connect(auth):  # <-- Accept the 'auth' argument
    global connected_users
    connected_users += 1
    emit('user_count', connected_users, broadcast=True)

@socketio.on('disconnect')
def on_disconnect():  # This one is OK with 0 args
    global connected_users
    connected_users = max(0, connected_users - 1)
    emit('user_count', connected_users, broadcast=True)

@socketio.on('message')
def handle_message(msg):
    nickname = session.get('nickname', 'Anonymous')
    send(f"{nickname}: {msg}", broadcast=True)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file:
        return 'No file received', 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        file.save(filepath)
    except Exception as e:
        print(f"❌ Failed to save file: {e}")
        return 'Internal error', 500

    nickname = session.get('nickname', 'Anonymous')
    ext = filename.rsplit('.', 1)[-1].lower()
    if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
        msg = f"{nickname} sent an image:<br><img src='/uploads/{filename}' style='max-width:200px;'>"
    else:
        msg = f"{nickname} uploaded a file: <a href='/uploads/{filename}' download>{filename}</a>"

    socketio.emit('message', msg)
    return ('', 204)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)



if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=port)
