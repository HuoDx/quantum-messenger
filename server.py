from flask import Flask, request, make_response, render_template
import config
from uuid import uuid4
from utils import wxpush
import user
app = Flask(__name__)

@app.route('/wxpush-callback', methods = ['POST'])
def callback():
    
    json_data = request.json.get('data')
    
    user_uid = json_data.get('uid')
    user_nickname = json_data.get('userName', 'New User')
    user_avatar = json_data.get('userHeadImg', '')
    timestamp = json_data.get('time')
    source = json_data.get('source')
    token = json_data.get('extra')
    
    user.login(token, user_uid, user_nickname, user_avatar)
    
    return 'ok.'

@app.route('/login', methods = ['GET'])
def login():
    if user.get_user_info(request.cookies.get('token'))[0]:
        # logged in
        u = user.get_user_info(request.cookies.get('token'))[1]
        print(u)
        return '<h1>%s, %s</h1>'%(u.nickname, u.avatar_url) # TODO: redirect to index or something
    
    token = str(uuid4())
    result = wxpush.get_qr_codes(token)
    if result[0]:
        response = make_response(render_template('login.html', QR_CODE_URL = result[1]))
        response.set_cookie('token', token)
        return response
    
if __name__ == '__main__':
    app.run(
        host = config.host,
        port = config.port,
        debug = config.debug
    )

