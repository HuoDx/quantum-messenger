from flask import Flask, request, make_response, render_template, redirect
import config
from uuid import uuid4
from utils import wxpush
import user
from question import Question, add_question, get_questions_by_answerer, get_questions_by_asker, get_question, register_temporary, answer_question,remove_temporary
import re

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
    result = remove_temporary(token, user_uid)
    if result[0]:
        print('User logged in: ', result[1])
    wxpush.push_notification( 
        Notification(
            '''<h2>你好，欢迎你加入 Quantum Messenger 匿名问答</h2>
                <h4>这是一个简洁轻松的提问箱</h4>
                <p><a href="%s">我的提问箱</a></p>
                
                <p><del><a href="%s">我的问题（没做并且我懒得做了orz）</a></del></p>
                </ul>
            '''%(config.base+'/box/%s'%user_uid,''),
            Notification.HTML,
            '欢迎加入 Quantum Messenger 匿名问答'
            ),
        [user_uid]
    ) 
    return 'ok.'

@app.route('/')
def index():
    return redirect('/login')

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
        
        answered_questions = []
        unanswered_questions = []
        
        for question in reversed(get_questions_by_answerer(box_owner.uid)):
            if question is None:
                continue
            if question.has_answered():
                answered_questions.append(question)
            else:
                unanswered_questions.append(question)
                
        # print('Answered Questions:', [str(a) for a in answered_questions])
        # print('Unanswered Questions:', [str(a) for a in unanswered_questions])
        
        return render_template(
            'box.html',
            OWNER = box_owner,
            ANSWERED_QUESTIONS = answered_questions,
            UNANSWERED_QUESTIONS = unanswered_questions,
            IS_OWNER = is_owner 
        )
    else:
        # ask a question to the box
        q = request.form.get('question')
        if q is None or re.sub(r'[\s]', '', q) == '':
            return render_template('oops.html', ERROR_MESSAGE='Invalid Question - your question must not be empty.')
        
        logged_in = False
        qr_code_url = ''
        token = None
        if user.get_user_info(request.cookies.get('token'))[0]:
            # logged in
            u = user.get_user_info(request.cookies.get('token'))[1]
            add_question(Question.ask(q, u.uid, user_uid))
            logged_in = True
        else:
            token = str(uuid4())
            qr_code_url = wxpush.get_qr_codes(token)[1]
        
        
        response = make_response(render_template('ask-done.html',
                                                QR_CODE_URL = qr_code_url,
                                                IS_TEMP = not logged_in,
                                                BACK_URL = '/box/%s'%user_uid
        ))
        result = wxpush.push_notification(Notification(
            '<h3>您收到新的提问，点击下方链接查看</h3><a href="%s">查看我的提问箱</a>'%(config.base+'/box/%s'%user_uid),
            Notification.HTML,
            '您有新的提问！'
        ), [user_uid])
        if not result:
            print('Question answered, but was not pushed.')
        if not logged_in:
            response.set_cookie('token', token)
            question = Question.ask(q, None, user_uid)
            add_question(question)
            register_temporary(token, question.uid)
            
        return response
            
            
@app.route('/answer/<question_uid>', methods=['POST'])
def ans_question(question_uid):
    if user.get_user_info(request.cookies.get('token'))[0]:
        # logged in
        u = user.get_user_info(request.cookies.get('token'))[1]
        answer = request.form.get('answer')
        if answer is None or answer == '':
            return render_template('oops.html', ERROR_MESSAGE='Answer cannot be empty', BACK_URL = '/box/%s'%u.uid)
        result = answer_question(question_uid, answer, u.uid)
        if not result[0]:
            msg = 'Somebody is attempting to use an account that does not belong to himself to answer a question.'
            print(msg)
            print(result[1])
            return render_template('oops.html', ERROR_MESSAGE=msg, BACK_URL = '/box/%s'%u.uid)
        
        result = wxpush.push_notification(Notification(
            '<h3>您的问题已被回答，点击下方链接查看</h3><a href="%s">查看 ta 的提问箱</a>'%(config.base+'/box/%s'%u.uid),
            Notification.HTML,
            '您的提问被回答！'
        ), [get_question(question_uid).asker])
        if not result:
            print('Question answered, but was not pushed.')
        return redirect('/box/%s'%u.uid)
    else:
        return redirect('/login')
        

        
    

@app.route('/login', methods = ['GET'])
def login():
    if user.get_user_info(request.cookies.get('token'))[0]:
        # logged in
        u = user.get_user_info(request.cookies.get('token'))[1]
        print(u)
        return redirect('/box/%s'%u.uid)
    
    token = str(uuid4())
    result = wxpush.get_qr_codes(token)
    if result[0]:
        response = make_response(render_template('login.html', QR_CODE_URL = result[1]))
        response.set_cookie('token', token)
        return response
    
if __name__ == '__main__':
    if config.debug:
        app.run(
            host = config.host,
            port = config.port,
            debug = config.debug
        )
    else:
        import waitress
        waitress.serve(app, 
            host = config.host,
            port = config.port
        )

