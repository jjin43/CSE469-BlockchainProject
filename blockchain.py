import hashlib
import time
import uuid
import struct
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES


# AES helper functions
def encrypt_aes_ecb(data, key):
    cipher = AES.new(key, AES.MODE_ECB)
    dataBytes = pad(struct.pack('I', data), 16)
    return cipher.encrypt(dataBytes)

def decrypt_aes_ecb(data, key):
    cipher = AES.new(key, AES.MODE_ECB)
    return struct.unpack('I', cipher.decrypt(data).strip(b'\x00').strip(b'\x0c'))[0]

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
        self.case_id = case_id if case_id else None
        self.evidence_item_id = evidence_item_id if evidence_item_id else None
        self.state = state.encode('utf-8')
        self.creator = creator[:12].encode('utf-8') if creator else None
        self.owner = owner.encode('utf-8') if owner in ['Police', 'Lawyer', 'Analyst', 'Executive'] else None
        self.data = data
        self.data_length = len(data.encode('utf-8'))
    
       
    def write_block(self, path):
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
        
        if self.case_id:
            self.case_id = encrypt_aes_ecb(int(self.case_id), self.aes_key)
        if self.evidence_item_id:
            self.evidence_item_id = encrypt_aes_ecb(int(self.evidence_item_id), self.aes_key)
        
        with open(path, 'ab') as file:
            
            file.write(struct.pack("32s d 32s 32s 12s 12s 12s I", self.previous_hash,
                                   self.timestamp, self.case_id, self.evidence_item_id,
                                   self.state, self.creator, self.owner, self.data_length))
            
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
            if data_length == b'':
                data_length_int = 0
                hash.update(b'')
            else:
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
                
    def item_id_exist(self, item_id):
        with open(self.path, 'rb') as f:
            # iterate through the file to find the last block
            while True:
                previous_hash = f.read(32)
                if not previous_hash:
                    break
                # dummy read to skip the rest of the block
                timestamp = f.read(8)
                case_id = f.read(32)
                aes_evidence_item_id = f.read(32)
                state = f.read(12)
                creator = f.read(12)
                owner = f.read(12)
                data_length = f.read(4)
                data = f.read(struct.unpack('I', data_length)[0])
                if not state.strip(b'\x00').decode('utf-8') == 'INITIAL':
                    if decrypt_aes_ecb(aes_evidence_item_id.strip(b'\x00'), self.aes_key) == int(item_id):
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
                aes_evidence_item_id = f.read(32)
                state = f.read(12)
                creator = f.read(12)
                owner = f.read(12)
                data_length = f.read(4)
                data = f.read(struct.unpack('I', data_length)[0])
                if(not state.decode('utf-8') == "INITIAL"):
                    if decrypt_aes_ecb(aes_evidence_item_id.strip(b'\x00'), self.aes_key) == item_id:
                        if state == "CHECKEDIN":
                            checkedIn = True
                        else:
                            checkedIn = False
        return checkedIn

            


    