import os
import parse_cmds
import blockchain


def main():

    # initialize the blockchain, with an initial block
    bc = blockchain.Chain()
    
    print("CSE 469 - Group Project: SYJH")
    print("********** [Application Starting] **********")
    status = parse()
    
    print("********** [Application Closing] **********")
    return status
        


# TODO: Parse the commands to variables and call the function in parse_cmds.py with them as arguments, pass multiple of the same input as a list
def parse():
    bchoc = parse_cmds()
    while True:
        cmd = input()
        cmdArr = cmd.split()
        
        if cmdArr[0] != "bchoc":
            print("Command Unknown: Try 'bchoc [command] [options]'")
            return False
        
        if cmdArr[1] == "add":
            bchoc.add()
        elif cmdArr[1] == "checkin":
            
        elif cmdArr[1] == "checkout":
            
        elif cmdArr[1] == "show":
            
        elif cmdArr[1] == "remove":
            
        elif cmdArr[1] == "init":
            
        elif cmdArr[1] == "verify":
        
        elif cmdArr[1] == "help":
            
        elif cmdArr[1] == "exit":
            return 0
        else:
            print("Command Unknown: Try 'bchoc help'")
            
    
if __name__ == '__main__':
   main()