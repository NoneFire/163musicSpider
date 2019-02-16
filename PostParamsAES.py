# encoding:utf-8

from Crypto.Cipher import AES
import base64
#新的aes加密包必须将传入的参数全部转化为utf-8二进制编码
first_param = '{rid:"", offset:"0", total:"true", limit:"20", csrf_token:""}'
second_param = "010001"
third_param = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
forth_param = "0CoJUm6Qyw8W8jud".encode('utf-8')

def AES_encrypt(param, key, iv):
    pad = 16 - len(param) % 16
    text = param + (pad * chr(pad)).encode('utf-8')
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    encrypt_text = encryptor.encrypt(text)
    encrypt_text = base64.b64encode(encrypt_text)
    return encrypt_text

def get_params(i):  #i是传入的参数，用来判定页数，从0开始，0，20，30，60...
    if i == 0:
        first_param = '{rid:"", offset:"0", total:"true", limit:"20", csrf_token:""}'.encode('utf-8')
    else:
        offset = str(i * 20)
        first_param = '{rid:"", offset:"%s", total:"%s", limit:"20", csrf_token:""}' % (offset, 'flase')
        first_param =first_param.encode('utf-8')
    iv = "0102030405060708".encode('utf-8')
    first_key = forth_param
    second_key = (16 * 'F').encode('utf-8')
    h_encText = AES_encrypt(first_param, first_key, iv)
    h_encText = AES_encrypt(h_encText, second_key, iv)
    return h_encText.decode('utf-8') #再解密为utf-8模式

def get_encSecKey():
    encSecKey = "257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c"
    #encSecKey='8d9efaf527b7647868a6ce205146c641ddd63e9b148e3c8be2eeda402ad3779c978adb0a8e2ee28f238185ff4b8510751234a13f5e159e98c66cccc60478e470c660039dd82445eca6b0b672ee03185ceb2a5cb4a1fe2a49900c0ce94b296055417e1ed572f2f9f45497e25fa197340043d61fb1963434f0d5ae6610b6d486c0'
    return encSecKey

if __name__ == '__main__':
    print('get_params()',get_params(1))
    print('get_encSecKey()',get_encSecKey())

