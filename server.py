from flask import Flask, request, make_response, render_template
import config
from uuid import uuid4
from utils import wxpush
import user
from notifications.notification import Notification
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
    wxpush.push_notification( 
        Notification(
            '''<h2>你好，欢迎你加入 Quick Magic 匿名问答</h2>
                <h4>这是一个简洁轻松的提问箱</h4>
                <ul>
                <li><a href="%s">我的提问箱</a></li>
                <li><a href="%s">我的问题</a></li>
                </ul>
            '''%('',''),
            Notification.HTML,
            '欢迎加入 Quick Magic 匿名问答'
            ),
        [user_uid]
    ) 
    return 'ok.'

@app.route('/box/<user_uid>', methods=['GET', 'POST'])
def box(user_uid):
    user_fetch = user.get_user_info(request.cookies.get('token'))
    if request.method == 'GET':
        # see the box
        # this is public - all users can see the answered questions.
        # however, if the owner is viewing his/her/their box, he/she/they is/are able to also see the unanswered questions.
        box_owner = user.get_user_public_info(user_uid)
        if box_owner is None:
            return render_template('oops.html', ERROR_MESSAGE = 'Strange... the box owner does not exist. \n // r u messing up with the UIDs of users???')
        is_owner = (user_fetch[0] and user_fetch[1].uid == user_uid)
        

        
    

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
    import question
    # app.run(
    #     host = config.host,
    #     port = config.port,
    #     debug = config.debug
    # )

