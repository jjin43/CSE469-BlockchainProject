import hashlib
import time
import uuid
import struct
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from base64 import b64encode,b64decode


# TODO: This is kind of a mess, mostly my experimentation with encryption stuff. The block chain should be from a raw binary file.
class Block:
    def __init__(self, previous_hash, case_id, evidence_item_id, state, creator, owner, data, aes_key):
        self.previous_hash = previous_hash
        self.timestamp = time.time()
        self.case_id = self.encrypt_aes_ecb(case_id, aes_key)
        self.evidence_item_id = self.encrypt_aes_ecb(evidence_item_id, aes_key)
        self.state = state
        self.creator = creator[:12]  # only take the first 12 characters, upper limit
        self.owner = owner if owner in ['Police', 'Lawyer', 'Analyst', 'Executive'] else 'Invalid'
        self.data = data
        self.data_length = len(data.encode('utf-8'))
        

    # incorrect padding, WIP
    def encrypt(plaintext,key):
        key = get_random_bytes(32)  # this will be given
        iv = get_random_bytes(16)   # initialization vector, makes same text generate different cipher text
        cipher = AES.new(key,AES.MODE_CBC,iv)
        return b64encode(cipher.encrypt(pad(plaintext.encode(),16))).decode()
    
    def decrypt(ciphertext,key):
        key = get_random_bytes(32)  # this will be given
        iv = get_random_bytes(16)   # initialization vector, makes same text generate different cipher text
        cipher = AES.new(key,AES.MODE_CBC,iv)
        return unpad(cipher.decrypt(b64decode(ciphertext.encode())),16).decode()
    
    def get_this_hash(self):
        block_contents = str(self.previous_hash) + str(self.timestamp) + self.case_id + self.evidence_item_id + self.state + self.creator + self.owner + str(self.data_length) + self.data
        return hashlib.sha256(block_contents.encode()).hexdigest()
    
    


class Chain:
    def __init__(self):
        self.chain = []
        self.aes_key = get_random_bytes(16)  # AES-128 key

    def add_block(self, case_id, evidence_item_id, state, creator, owner, data):
        if self.chain:
            previous_hash = self.chain[-1].get_this_hash()  
        else:
            previous_hash = '0' * 64  # first block no prev hash, all 0s.
        block = Block(previous_hash, case_id, evidence_item_id, state, creator, owner, data, self.aes_key)
        self.chain.append(block)


    