import sys
import parse_cmds
import blockchain

def main():

    # initialize the blockchain, with an initial block
    bc = blockchain.Chain()
    done = True
    
    print("CSE 469 - Group Project: SYJH")
    print("********** [Application Starting] **********")
    while not done:
        done = parse_cmds.parse(input())
    
    print("********** [Application Closing] **********")
              
        
    
    
if __name__ == '__main__':
   main()