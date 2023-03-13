
import base64
from Crypto import Random
from Crypto.Cipher import AES
import src.keyfile as keyfile
from src.utils import utils

encrypt_key = keyfile.str_encrypt_key
IV = keyfile.str_IV

class AES128Crypto:

    def __init__(self, encrypt_key, iv):
        self.BS = AES.block_size
        self.encrypt_key = encrypt_key
        self.iv = iv
        self.pad = lambda s: bytes(s + (self.BS - len(s) % self.BS) * chr(self.BS - len(s) % self.BS), 'utf-8')
        self.unpad = lambda s: s[0:-ord(s[-1:])]
        self.utils = utils()

    # not likely to use encrypt function
    def encrypt(self, data, seq):
        data = bytes(data)
        
        data = self.pad(data)
        encryptIV = bytearray(self.iv)
        encryptIV[-2] = seq[0]
        encryptIV[-1] = seq[1]
        encryptIV = bytes(encryptIV)
        
        cipher = AES.new(self.encrypt_key, AES.MODE_CBC, encryptIV)
        
        return base64.b64encode(encryptIV + cipher.encrypt(data)).decode("utf-8")


    def decrypt(self, data, seq):
        data = bytes(data)
        decryptIV = bytearray(self.iv)
        decryptIV[-2] = seq[0]
        decryptIV[-1] = seq[1]
        decryptIV = bytes(decryptIV)
        cipher = AES.new(encrypt_key, AES.MODE_CBC, decryptIV)
        decrypted_data = cipher.decrypt(data)

        return decrypted_data
