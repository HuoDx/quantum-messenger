
class UserInfo:
    def __init__(self, uid, nickname, avatar_url):
        self.uid = uid
        self.nickname = nickname
        self.avatar_url = avatar_url
    
    def __str__(self):
        return '%s\t%s\t%s'%(self.uid, self.nickname, self.avatar_url)

users = {} # uid -> user_info
sessions = {} # token -> uid

def login(token, uid, nickname, avatar_url):
    global sessions, users
    sessions.update({token: uid})
    users.update({uid: UserInfo(uid, nickname, avatar_url)})
    print('User [%s] has logged in.'%nickname)
    return True
    
def get_user_info(token) -> UserInfo:
    global sessions, users
    session = sessions.get(token)
    user = users.get(session)
    if user is not None:
        return True, user
    return False, 'user does not exist.'

def get_user_public_info(uid) -> UserInfo:
    global users
    return users.get(uid)
