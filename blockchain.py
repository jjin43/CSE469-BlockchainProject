import hashlib
import time
import uuid
import struct
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES


# AES helper functions
def encrypt_aes_ecb(self, data, key):
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(pad(data.encode('utf-8'), 16))

def decrypt_aes_ecb(self, data, key):
    cipher = AES.new(key, AES.MODE_ECB)
    return unpad(cipher.decrypt(data), 16).decode('utf-8')

# output helper functions
def verify_output(self, blockcount, state, badblock=None, badstate=None):
    print("Transactions in blockchain: " + str(blockcount))
    print("State of blockchain: " + state)
    if badblock:
        print("Bad block: " + badblock)
    
    # WIP
    # if badstate:

# class for creating blocks
class Block:
    def __init__(self, previous_hash, state, data, aes_key, case_id=None, evidence_item_id=None,  creator=None, owner=None):
        self.aes_key = aes_key
        self.previous_hash = previous_hash
        self.timestamp = time.time()
        self.case_id = self.encrypt_aes_ecb(case_id, aes_key) if case_id else None
        self.evidence_item_id = self.encrypt_aes_ecb(evidence_item_id, aes_key) if evidence_item_id else None
        self.state = state.encode('utf-8')
        self.creator = creator[:12] if creator else None
        self.owner = owner if owner in ['Police', 'Lawyer', 'Analyst', 'Executive'] else None
        self.data = data
        self.data_length = len(data.encode('utf-8'))
    
       
    def write_block(self, path):
        if self.case_id:
            self.case_id = encrypt_aes_ecb(self.case_id, self.aes_key)
        if self.evidence_item_id:
            self.evidence_item_id = encrypt_aes_ecb(self.evidence_item_id, self.aes_key)

        if (self.previous_hash == None):
            self.previous_hash = bytes(0)

        if (self.case_id == None):
            self.case_id = bytes(0)
        
        if (self.evidence_item_id == None):
            self.evidence_item_id = bytes(0)
        
        if (self.creator == None):
            self.creator = bytes(0)

        if (self.owner == None):
            self.owner = bytes(0)
        

        with open(path, 'ab') as file:

            file.write(self.previous_hash.ljust(32, b'\x00'))
            file.write(struct.pack('d', self.timestamp))
            file.write(self.case_id.ljust(32, b'\x00'))
            file.write(self.evidence_item_id.ljust(32, b'\x00'))
            file.write(self.state.ljust(12, b'\x00'))
            file.write(self.creator.ljust(12, b'\x00'))
            file.write(self.owner.ljust(12, b'\x00'))
            file.write(struct.pack('I', self.data_length))
            file.write(self.data.encode('utf-8'))
        

    
    

# for blockchain operations requiring iterating through the blockchain file
class Chain:
    def __init__(self, path, aes_key):
        self.path = path
        self.aes_key = aes_key
    
    
    # parse the block chain and validate all entries    
    def verify(self):
        # parse by chunks to avoid memory issues
        with open(self.path, 'rb') as f:
            done = False
            # WIP
                
                
                
    def get_last_block_hash(self):
        previous_hash = None
        with open(self.path, 'rb') as f:
            # iterate through the file to find the last block
            while True:
                last = previous_hash
                previous_hash = f.read(32)
                if not previous_hash:
                    break             
                # dummy read to skip the rest of the block
                timestamp = f.read(8)
                case_id = f.read(32)
                evidence_item_id = f.read(32)
                state = f.read(12)
                creator = f.read(12)
                owner = f.read(12)
                data_length = f.read(4)
                
            # when breaks, file pointer is at last block's data section
            # hashing data chunk by chunk to avoid memory issues
            hash = hashlib.sha256(previous_hash + timestamp + case_id + evidence_item_id + state + creator + owner + data_length)
            
            i = 0
            data_length_int = struct.unpack('I', data_length)[0]
            while i < data_length_int: 
                if i + 1024 <= data_length_int:
                    data = f.read(1024)
                    i += 1024
                else:
                    data = f.read(data_length_int - i)
                    i = data_length_int
                hash.update(data)
                
            return hash.digest()
                
    def item_id_exist(self, item_ids):
        with open(self.path, 'rb') as f:
            # iterate through the file to find the last block
            while True:
                previous_hash = f.read(32)
                if not previous_hash:
                    break
                # dummy read to skip the rest of the block
                timestamp = f.read(8)
                case_id = f.read(32)
                evidence_item_id = f.read(32)
                state = f.read(12)
                creator = f.read(12)
                owner = f.read(12)
                data_length = f.read(4)
                data = f.read(struct.unpack('I', data_length))
                if evidence_item_id in item_ids:
                    return True
        return False

    def is_checkedIn(self, item_id):
        with open(self.path, 'rb') as f:
            # iterate through the file to find the last block
            checkedIn = False
            while True:
                previous_hash = f.read(32)
                if not previous_hash:
                    break
                # dummy read to skip the rest of the block
                timestamp = f.read(8)
                case_id = f.read(32)
                evidence_item_id = f.read(32)
                state = f.read(12)
                creator = f.read(12)
                owner = f.read(12)
                data_length = f.read(4)
                data = f.read(struct.unpack('I', data_length))
                if evidence_item_id == item_id:
                    if state == "CHECKEDIN":
                        checkedIn = True
                    else:
                        checkedIn = False
        return checkedIn

            


    