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
    return struct.unpack('I', cipher.decrypt(data).strip(b'\x00').strip(b'\x0c').ljust(4,b'\x00'))[0]


# class for creating blocks
class Block:
    def __init__(self, previous_hash, state, data, aes_key, case_id=None, evidence_item_id=None,  creator=None, owner=None, rawBytes=False):
        self.rawBytes = rawBytes
        if not rawBytes:
            self.aes_key = aes_key
            self.previous_hash = previous_hash
            self.timestamp = time.time()
            self.case_id = case_id if case_id else bytes(0)
            self.evidence_item_id = evidence_item_id if evidence_item_id else bytes(0)
            self.state = state.encode('utf-8')
            self.creator = creator[:12].encode('utf-8') if creator else bytes(0)
            self.owner = owner.encode('utf-8') if owner in ['Police', 'Lawyer', 'Analyst', 'Executive'] else bytes(0)
            self.data = data
            self.data_length = len(data.encode('utf-8'))
        else:
            self.aes_key = aes_key
            self.previous_hash = previous_hash
            self.timestamp = time.time()
            self.case_id = case_id
            self.evidence_item_id = evidence_item_id
            self.state = state
            self.creator = creator
            self.owner = owner
            self.data = data
            self.data_length = len(data)

    
       
    def write_block(self, path):
        if not self.rawBytes:
            if self.case_id:
                self.case_id = encrypt_aes_ecb(int(self.case_id), self.aes_key)
            if self.evidence_item_id:
                self.evidence_item_id = encrypt_aes_ecb(int(self.evidence_item_id), self.aes_key)
        
        with open(path, 'ab') as file:
            # debug prints
            # print("self.previous_hash:", type(self.previous_hash), self.previous_hash)
            # print("self.timestamp:", type(self.timestamp), self.timestamp)
            # print("self.case_id:", type(self.case_id), self.case_id)
            # print("self.evidence_item_id:", type(self.evidence_item_id), self.evidence_item_id)
            # print("self.state:", type(self.state), self.state)
            # print("self.creator:", type(self.creator), self.creator)
            # print("self.owner:", type(self.owner), self.owner)
            # print("self.data_length:", type(self.data_length), self.data_length)
            
            file.write(struct.pack("32s d 32s 32s 12s 12s 12s I", self.previous_hash,
                       self.timestamp, self.case_id, self.evidence_item_id,
                       self.state, self.creator, self.owner, self.data_length))
            
            if(self.rawBytes):
                file.write(self.data)
            else:
                file.write(self.data.encode('utf-8'))
        

    
    

# for blockchain operations requiring iterating through the blockchain file
class Chain:
    def __init__(self, path, aes_key):
        self.chunk_mem = 1024
        self.path = path
        self.aes_key = aes_key
    
    
    # parse the block chain and validate all entries    
    def verify(self):
        # verify #1: check hash correctness
        with open(self.path, 'rb') as f:
            actual_prev_hash = b'\x00' * 32  # initial block has no previous hash
            count = 0
            while True:
                count += 1
                previous_hash = f.read(32)
                if not previous_hash:
                    break
                if previous_hash != actual_prev_hash:
                    return count             
                # dummy read to skip the rest of the block
                timestamp = f.read(8)
                case_id = f.read(32)
                evidence_item_id = f.read(32)
                state = f.read(12)
                creator = f.read(12)
                owner = f.read(12)
                data_length = f.read(4)
                
                # hashing data chunk by chunk to avoid memory issues
                hash = hashlib.sha256(previous_hash + timestamp + case_id + evidence_item_id + state + creator + owner + data_length)
                
                i = 0
                data_length_int = struct.unpack('I', data_length)[0]
                while i < data_length_int: 
                    if i + self.chunk_mem < data_length_int:
                        data = f.read(self.chunk_mem)
                        i += self.chunk_mem
                    else:
                        data = f.read(data_length_int - i)
                        i = data_length_int
                    hash.update(data)
                actual_prev_hash = hash.digest()
        
        # verify #2: check for inproper actions (removed item being checked in, etc.)   
        # WIP
        
        
        # No errors found 
        return 0
                
                
                
    def get_last_block_hash(self):
        
        with open(self.path, 'rb') as f:
            # iterate through the file to find the last block
            previous_hash = None
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
                data_address = f.tell()
                data = f.read(struct.unpack('I', data_length)[0])
                
            # when breaks, use data_address to read the data section of the last block
            # hashing data chunk by chunk to avoid memory issues

            hash = hashlib.sha256(last + timestamp + case_id + evidence_item_id + state + creator + owner + data_length)
            
            i = 0
            data_length_int = struct.unpack('I', data_length)[0]
            while i < data_length_int: 
                if i + self.chunk_mem < data_length_int:
                    f.seek(data_address + i, 0)
                    data = f.read(self.chunk_mem)
                    i += self.chunk_mem
                else:
                    f.seek(data_address + i, 0)
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
    
    def case_id_exist(self, case_id):
        with open(self.path, 'rb') as f:
            # iterate through the file to find the last block
            while True:
                previous_hash = f.read(32)
                if not previous_hash:
                    break
                # dummy read to skip the rest of the block
                timestamp = f.read(8)
                aes_case_id = f.read(32)
                item_id = f.read(32)
                state = f.read(12)
                creator = f.read(12)
                owner = f.read(12)
                data_length = f.read(4)
                data = f.read(struct.unpack('I', data_length)[0])
                if not state.strip(b'\x00').decode('utf-8') == 'INITIAL':
                    if decrypt_aes_ecb(aes_case_id.strip(b'\x00'), self.aes_key) == int(case_id):
                        return True

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
                
                state = state.decode('utf-8').strip('\x00')
                if(not state == "INITIAL"):
                    if decrypt_aes_ecb(aes_evidence_item_id.strip(b'\x00'), self.aes_key) == int(item_id):
                        if state == "CHECKEDIN":
                            checkedIn = True
                        else:
                            checkedIn = False
        return checkedIn
    
    def get_blockcount(self):
        with open(self.path, 'rb') as f:
            count = 0
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
                count += 1
        return count
    
    def checkin(self, item_id):
        with open(self.path, 'rb') as f:
            target_data = None
            target_case_id = None
            target_evidence_item_id = None
            target_creator = None
            target_owner = None
            
            while True:
                previous_hash = f.read(32)
                if not previous_hash:
                    break
                # dummy read to skip the rest of the block
                timestamp = f.read(8)   #discard
                case_id = f.read(32)
                evidence_item_id = f.read(32)
                state = f.read(12)      #discard
                creator = f.read(12)
                owner = f.read(12)
                data_length = f.read(4)
                data = f.read(struct.unpack('I', data_length)[0])
                if(decrypt_aes_ecb(evidence_item_id.strip(b'\x00'), self.aes_key) == int(item_id)):
                    target_data = data
                    target_case_id = case_id
                    target_evidence_item_id = evidence_item_id
                    target_creator = creator
                    target_owner = owner
                
            updatedBlock = Block(self.get_last_block_hash(), "CHECKEDIN".encode('utf-8'), target_data, self.aes_key, target_case_id, target_evidence_item_id, target_creator, target_owner, rawBytes=True)
            updatedBlock.write_block(self.path)
                
    def checkout(self, item_id):
        with open(self.path, 'rb') as f:
            target_data = None
            target_case_id = None
            target_evidence_item_id = None
            target_creator = None
            target_owner = None
            
            while True:
                previous_hash = f.read(32)
                if not previous_hash:
                    break
                # dummy read to skip the rest of the block
                timestamp = f.read(8)   #discard
                case_id = f.read(32)
                evidence_item_id = f.read(32)
                state = f.read(12)      #discard
                creator = f.read(12)
                owner = f.read(12)
                data_length = f.read(4)
                data = f.read(struct.unpack('I', data_length)[0])
                if(decrypt_aes_ecb(evidence_item_id.strip(b'\x00'), self.aes_key) == int(item_id)):
                    target_data = data
                    target_case_id = case_id
                    target_evidence_item_id = evidence_item_id
                    target_creator = creator
                    target_owner = owner
                
            updatedBlock = Block(self.get_last_block_hash(), "CHECKEDOUT".encode('utf-8'), target_data, self.aes_key, target_case_id, target_evidence_item_id, target_creator, target_owner, rawBytes=True)
            updatedBlock.write_block(self.path)
                
    def get_cases(self):
        caseList = []
        with open(self.path, 'rb') as f:
            while True:
                previous_hash = f.read(32)
                if not previous_hash:
                    break
                # dummy read to skip the rest of the block
                timestamp = f.read(8)   #discard
                aes_case_id = f.read(32)
                evidence_item_id = f.read(32)
                state = f.read(12)      #discard
                creator = f.read(12)
                owner = f.read(12)
                data_length = f.read(4)
                data = f.read(struct.unpack('I', data_length)[0])
                case_id = decrypt_aes_ecb(aes_case_id.strip(b'\x00'), self.aes_key)
                if case_id not in caseList and state.strip(b'\x00').decode('utf-8') != "INITIAL":
                    print(case_id, repr(state.decode('utf-8')))
                    caseList.append(case_id)
        return caseList
    
    def get_items(self, target_case_id):
        itemList = []
        with open(self.path, 'rb') as f:
            while True:
                previous_hash = f.read(32)
                if not previous_hash:
                    break
                # dummy read to skip the rest of the block
                timestamp = f.read(8)   #discard
                aes_case_id = f.read(32)
                aes_evidence_item_id = f.read(32)
                state = f.read(12)      #discard
                creator = f.read(12)
                owner = f.read(12)
                data_length = f.read(4)
                data = f.read(struct.unpack('I', data_length)[0])
                case_id = decrypt_aes_ecb(aes_case_id.strip(b'\x00'), self.aes_key)
                item_id = decrypt_aes_ecb(aes_evidence_item_id.strip(b'\x00'), self.aes_key)
                if case_id==int(target_case_id) and state.strip(b'\x00').decode('utf-8') != "INITIAL":
                    itemList.append(item_id)
        return itemList
    
    def remove(self, item_id, reason_state, new_owner=None):
        with open(self.path, 'rb') as f:
            target_data = None
            target_case_id = None
            target_evidence_item_id = None
            target_creator = None
            target_owner = None
            
            while True:
                previous_hash = f.read(32)
                if not previous_hash:
                    break
                # dummy read to skip the rest of the block
                timestamp = f.read(8)   #discard
                case_id = f.read(32)
                evidence_item_id = f.read(32)
                state = f.read(12)      #discard
                creator = f.read(12)
                owner = f.read(12)
                data_length = f.read(4)
                data = f.read(struct.unpack('I', data_length)[0])
                if(decrypt_aes_ecb(evidence_item_id.strip(b'\x00'), self.aes_key) == int(item_id)):
                    target_data = data
                    target_case_id = case_id
                    target_evidence_item_id = evidence_item_id
                    target_creator = creator
                    target_owner = owner
                
            if(new_owner):
                updatedBlock = Block(self.get_last_block_hash(), reason_state.encode('utf-8'), target_data, self.aes_key, target_case_id, target_evidence_item_id, target_creator, new_owner.encode('utf-8'), rawBytes=True)
            else:
                updatedBlock = Block(self.get_last_block_hash(), reason_state.encode('utf-8'), target_data, self.aes_key, target_case_id, evidence_item_id, target_creator, target_owner, rawBytes=True)
            updatedBlock.write_block(self.path)
            


    