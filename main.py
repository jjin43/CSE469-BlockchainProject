import sys
import parse_cmds


def main():
    parse_cmds.bchoc(sys.argv[1:])
    sys.exit(0)
    
if __name__ == '__main__':
   main()