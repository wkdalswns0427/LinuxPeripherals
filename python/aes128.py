
import base64
from Crypto import Random
from Crypto.Cipher import AES
import keyfile

encrypt_key = keyfile.str_encrypt_key
IV = keyfile.str_IV

# encrypt_key and iv data should be in str type (e.g. str_IV = '\x41\x69\x72\x50\x6F\x69\x6E\x74\x48\x69\x70\x61\x73\x73\xFF\xFF')
str_dummy = '\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
thisistest = "this"
dummy_list = [0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x40]


dummy_seq = [0x00, 0x01]

class AES128Crypto:

    def __init__(self, encrypt_key, iv):
        self.BS = AES.block_size
        self.encrypt_key = encrypt_key[:16].encode(encoding='utf-8', errors='strict')
        self.iv = iv
        self.pad = lambda s: bytes(s + (self.BS - len(s) % self.BS) * chr(self.BS - len(s) % self.BS), 'utf-8')
        self.unpad = lambda s: s[0:-ord(s[-1:])]
        
    
    def hexlist2str(self, list):
        L = len(list)
        str_list = []
        for i in range(L):
            hexstr = str(hex(list[i])).replace('0x','',1)
            str_list.append(hexstr)
        joined_list = r"\x" + r"\x".join(str_list)

        return joined_list


    def encrypt(self, data, seq):
        if type(data)==list:
            data = self.hexlist2str(data)
        elif type(data)==str:
            pass
        else:
            TypeError("Invalid input type")
            
        data = self.pad(data)
        encryptIV = bytearray(self.iv)
        encryptIV[-2] = seq[0]
        encryptIV[-1] = seq[1]
        encryptIV = bytes(encryptIV)
        
        cipher = AES.new(self.encrypt_key, AES.MODE_CBC, encryptIV)
        
        return base64.b64encode(encryptIV + cipher.encrypt(data)).decode("utf-8")


    def decrypt(self, data, seq):
        data = base64.b64decode(data)

        decryptIV = bytearray(self.iv)
        decryptIV[-2] = seq[0]
        decryptIV[-1] = seq[1]
        decryptIV = bytes(decryptIV)
        
        encrypted_msg = data[self.BS:]
        cipher = AES.new(self.encrypt_key, AES.MODE_CBC, decryptIV)
        
        return self.unpad(cipher.decrypt(encrypted_msg)).decode('utf-8')

##############################################################################################################################

if __name__ == "__main__":
    AESagent = AES128Crypto(encrypt_key, IV)

    enc_res = AESagent.encrypt(dummy_list, dummy_seq)
    print(enc_res)
    
    dec_res = AESagent.decrypt(enc_res, dummy_seq)
    print(dec_res)
