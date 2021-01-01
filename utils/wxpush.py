import requests
import config
from pprint import pprint

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
    
