import sys
import parse_cmds
import blockchain

def main():
    done = True
    print("CSE 469 - Group Project: SYJH")
    print("********** [Application Starting] **********")
    while not done:
        done = parse_cmds.parse(input())
    
    print("********** [Application Closing] **********")
              
        
    
    
if __name__ == '__main__':
   main()