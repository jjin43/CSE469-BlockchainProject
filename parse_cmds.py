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


# TODO: handle command line calls
class bchoc:
    def __init__(self):
        if(os.environ['BCHOC_FILE_PATH']):
            self.path = os.environ['BCHOC_FILE_PATH']   # provided path
        else:
            self.path = os.getcwd() + "/bchoc.dat"  # raw binary file
            
    def add(self):
        
    def checkin(self):
    
    def checkout(self):
    
    def show_cases(self):
        
    def show_items(self):
        
    def show_history(self):

    def remove(self):
        
    def init(self):
        
    def verify(self):
    
    