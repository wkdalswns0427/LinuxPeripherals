
import base64
from Crypto import Random
from Crypto.Cipher import AES
import src.keyfile as keyfile
from src.utils import utils


local_IV = keyfile.local_IV

class AES128Crypto:

    def __init__(self, encrypt_key, iv):
        self.BS = AES.block_size
        self.encrypt_key = encrypt_key
        self.iv = iv
        self.pad = lambda s: s + bytes((self.BS - len(s) % self.BS) * chr(self.BS - len(s) % self.BS), 'utf-8')
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
        cipher = AES.new(self.encrypt_key, AES.MODE_CBC, decryptIV)
        decrypted_data = cipher.decrypt(data)

        return decrypted_data


    def re_encrypt(self, data):
        data = bytes(data)
        
        data = self.pad(data)
        encryptIV = bytes(local_IV)
        
        cipher = AES.new(self.encrypt_key, AES.MODE_CBC, encryptIV)

        # base64.b64encode(encryptIV + cipher.encrypt(data)).decode("utf-8")
        encoded = base64.b64encode(cipher.encrypt(data))
        
        return encoded

    def re_decrypt(self, data):
        data = bytes(data)
        data = self.pad(data)
        decryptIV = bytes(local_IV)
        cipher = AES.new(self.encrypt_key, AES.MODE_CBC, decryptIV)

        data = base64.b64decode(data)
        decrypted_data = cipher.decrypt(data)

        return list(decrypted_data)

# b'p4vxZnCF5sqOHKD8JzhPFQ==' : 00 00 01 0e 0a 03 70 95