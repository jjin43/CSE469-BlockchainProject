def parse(str):
    cmds = str.split()
    if cmds[0] != "bchoc":
        printline("Command Unknown: try 'bchoc'")
        
    if cmds[1] == "...":
        # call function in blockchain.py
        x = 0
    if cmds[1] == "exit":
        return