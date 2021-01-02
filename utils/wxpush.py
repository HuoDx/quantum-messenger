import requests
import config
from pprint import pprint
from notifications.notification import Notification

HEADER = {
    'Content-Type': 'Application/json'
}
def post_json(url:str, json_object: dict) -> dict:
    return requests.post(url, json = json_object, headers = HEADER).json()

def get_qr_codes(carry):
    '''
    gets a URL for QR code that carries the `carry` in callback API.
    '''
    post_data = {
        "appToken": config.app_token,   # 必填，appToken,前面有说明，应用的标志
        "extra": carry[:64],      # 必填，二维码携带的参数，最长64位
        "validTime": config.temp_login_valid_time    # 可选，二维码的有效期，默认30分钟，最长30天，单位是秒
    }
    response = post_json('http://wxpusher.zjiecode.com/api/fun/create/qrcode', post_data)
    if response.get('success', False):
        # success
        print(response)
        return True, response.get('data').get('shortUrl')
    return False, response

def push_notification(notification: Notification, user_uids:[]):
    post_data = {
        "appToken":config.app_token,
        "content": notification.content,
        "summary": notification.summary,#消息摘要，显示在微信聊天页面或者模版消息卡片上，限制长度100，可以不传，不传默认截取content前面的内容。
        "contentType": notification._type,#内容类型 1表示文字  2表示html(只发送body标签内部的数据即可，不包括body标签) 3表示markdown 
        "uids": user_uids
    }
    response = post_json('http://wxpusher.zjiecode.com/api/send/message', post_data)
    if response.get('success', False):
        # success
        pprint(response)
        return True
    return False

    
