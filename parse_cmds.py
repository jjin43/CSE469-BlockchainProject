# List of Commands:
# 
# bchoc add -c case_id -i item_id [-i item_id ...] -c creator -p password(creator’s)
# bchoc checkout -i item_id -p password
# bchoc checkin -i item_id -p password
# bchoc show cases -p password
# bchoc show items -c case_id -p password
# bchoc show history [-c case_id] [-i item_id] [-n num_entries] [-r] -p
# password
# bchoc remove -i item_id -y reason [-o owner] -p password(creator’s)
# bchoc init
# bchoc verify
import os
import blockchain


# TODO: handle command line calls
class bchoc:
    path = ""
    aes_key = ""
    
    def __init__(self, argv):
        if(os.environ['AES_KEY']):
            self.aes_key = os.environ['AES_KEY']  # provided key
        else:
            self.aes_key = 1234567890123456  # raw key
        
        if(os.environ['BCHOC_FILE_PATH']):
            self.path = os.environ['BCHOC_FILE_PATH']   # provided path
        else:
            self.path = os.getcwd() + "/bchoc.dat"  # raw binary file
        
        # No blockchain file exits, create one
        if not os.path.exists(self.path):
            with open(self.path, 'w') as f:
                previous_hash = None  # first block no prev hash, all 0s.
                initblock = blockchain.Block(previous_hash, "INITIAL", "Initial block", self.aes_key)
                initblock.write_block(f)
                
        self._parse_cmds(argv)
                
    def _parse_cmds(self, argv):
        if argv[0] == "add":
            case_id = argv[2]
            item_ids = []
            for i in range(3, len(argv)):
                if argv[i] == "-c":
                    break
                elif argv[i] != "-i":
                    item_ids.append(argv[i])
            creator = argv[i+1]
            password = argv[i+3]
            self.add(case_id, item_ids, creator, password)
        elif argv[0] == "checkin":
            self.checkin()
        elif argv[0] == "checkout":
            self.checkout()
        elif argv[0] == "show":
            if argv[1] == "cases":
                self.show_cases()
            elif argv[1] == "items":
                self.show_items()
            elif argv[1] == "history":
                self.show_history()
        elif argv[0] == "remove":
            self.remove()
        elif argv[0] == "init":
            self.init()
        elif argv[0] == "verify":
            self.verify()
        else:
            print("Invalid command")
            
    def add(self, case_id, item_ids, creator, password):
        for item_id in item_ids:
            WIP
    def checkin(self):
        WIP
    def checkout(self):
        WIP
    def show_cases(self):
        WIP
    def show_items(self):
        WIP
    def show_history(self):
        WIP
    def remove(self):
        WIP
    def init(self):
        if(os.environ['AES_KEY']):
            self.aes_key = os.environ['AES_KEY']  # provided key
        else:
            self.aes_key = 1234567890123456  # default key
        
        if(os.environ['BCHOC_FILE_PATH']):
            self.path = os.environ['BCHOC_FILE_PATH']   # provided path
        else:
            self.path = os.getcwd() + "/bchoc.dat"  # default file
        
        # No blockchain file exits, create one
        if not os.path.exists(self.path):
            previous_hash = None  # first block no prev hash, all 0s.
            initblock = blockchain.Block(previous_hash, "INITIAL", "Initial block", self.aes_key)
            initblock.write_block(self.path)
        
    def verify(self):
        Chain = blockchain.Chain(self.path, self.aes_key)
