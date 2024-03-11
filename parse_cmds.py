# List of Commands:
# 
# bchoc add -c case_id -i item_id [-i item_id ...] -c creator -p
# password(creator’s)
# bchoc checkout -i item_id -p password
# bchoc checkin -i item_id -p password
# bchoc show cases -p password
# bchoc show items -c case_id -p password
# bchoc show history [-c case_id] [-i item_id] [-n num_entries] [-r] -p
# password
# bchoc remove -i item_id -y reason [-o owner] -p password(creator’s)
# bchoc init
# bchoc verify


def parse(bc, str):
    cmds = str.split()
    if cmds[0] != "bchoc":
        print("Command Unknown: Try 'bchoc'")
        
    