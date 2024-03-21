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


# TODO: figure out if we need to throw an error if there are too many arguments
# TODO: figure out if <-o owner> can exist and is just ignored or throws an error w/out RELEASED
# TODO: I think checking for the bchoc file should include checking for the initial node
class bchoc:
    path = ""
    aes_key = ""
    arguments = []

    acceptableReasons = ["DISPOSED", "DESTROYED", "RELEASED"]
    acceptableOwners = ["POLICE", "LAWYER", "ANALYST", "EXECUTIVE"]
    
    def __init__(self, argv):
        if('AES_KEY' in os.environ):
            self.aes_key = os.environ['AES_KEY'].encode('utf-8').ljust(16, b'\0')  # provided key
        else:
            self.aes_key = str(12345).encode('utf-8').ljust(16, b'\0')
        
        if('BCHOC_FILE_PATH' in os.environ):
            self.bchocFileExists = True
            self.path = os.environ['BCHOC_FILE_PATH']   # provided path
            
        else:
            self.bchocFileExists = False
            self.path = os.getcwd() + "/bchoc.dat"  # raw binary file

        # save arguments
        self.arguments = argv
                
        # Parse commands and execute them
        self.chain = blockchain.Chain(self.path, self.aes_key)
        self._parse_cmds()
    
    # Returns the next argument in the list of arguments and consumes,
    #throwing an error if it does not exist
    # Receives nothing
    # Returns a string representing the argument
    def getNextArg(self):
        # Try to pop, and throw the error if it does not work
        try:
            return self.arguments.pop(0)
        except (IndexError):
            print("Error: Incorrect number of arguments")
            exit(1)

    # Returns the next argument in a list of arguments without consuming
    # Receives nothing
    # Returns a string representing the next argument
    def peekNextArg(self):
        # Check that there are still arguments remaining
        if (len(self.arguments) > 0):
            return self.arguments[0]
        # If there are none, return the end of argument string
        else:
            return "END_OF_ARGUMENT"

    # Checks that the next argument is correct while consuming it, throwing an error if no match
    # Receives a string representing the expected value
    # Returns no value
    def expectArg(self, expectVal):
        # Get the next argument
        nextArg = self.getNextArg()
        
        # If it does not match with expected, throw an error
        if (nextArg != expectVal):
            print(f"Unexpected command line argument: {nextArg} instead of {expectVal}")
            exit(1)

    # Parses and begins executing the command line arguments
    # Receives no value
    # Returns no value
    def _parse_cmds(self):
        # Get the operation
        operation = self.getNextArg()

        # No blockchain file exits, create one and note creation NOTE: MAY REQUIRE REPAIR
        if not os.path.isfile(self.path):
            previous_hash = b'\x00' * 32  # first block no prev hash, all empty bytes.
            initblock = blockchain.Block(previous_hash, "INITIAL", "Initial block", self.aes_key)
            initblock.write_block(self.path)

        # Follow the path matching the command, throwing an error if there is no match
        if operation == "add":
            self._parse_add()
        elif operation == "checkin":
            self._parse_checkin()
        elif operation == "checkout":
            self._parse_checkout()
        elif operation == "show":
            self._parse_show()
        elif operation == "remove":
            self._parse_remove()
        elif operation == "init":
            self.initOutput()
        elif operation == "verify":
            self.verify()
        else:
            print("Invalid command")
            exit(1)
            
    # Parses and calls execution of the add argument
    # Receives no value
    # Returns no value
    def _parse_add(self):
        # Grab the case id
        self.expectArg("-c")
        case_id = self.getNextArg()

        # Get all item ids
        item_ids = []
        moreItems = True
        while(moreItems):
            self.expectArg("-i")
            newID = self.getNextArg()

            item_ids.append(newID)

            tempArg = self.peekNextArg()
            moreItems = tempArg == "-i"
            
        # Get creator
        self.expectArg("-c")
        creator = self.getNextArg()

        # Get password
        self.expectArg("-p")
        password = self.getNextArg()
        
        self.add(case_id, item_ids, creator, password)

    # Parses and calls execution of the show argument
    # Receives no value
    # Returns no value
    def _parse_show(self):
        # Get the show type
        showType = self.getNextArg()

        # Follow the path aligning with the found type
        if showType == "cases":
            self._parse_show_cases()
        elif showType == "items":
            self._parse_show_items()
        elif showType == "history":
            self._parse_show_history()
        else:
            print("Incorrect show type (Expects: 'cases', 'items', or 'history')")
            exit(1)

    # Parses and calls execution of the checkin argument
    # Receives no value
    # Returns no value
    def _parse_checkin(self):
        # Get the item's id
        self.expectArg("-i")
        itemId = self.getNextArg()
    
        # Get the password
        self.expectArg("-p")
        password = self.getNextArg()

        self.checkin(itemId, password)
    
    # Parses and calls execution of the checkout argument
    # Receives no value
    # Returns no value
    def _parse_checkout(self):
        # Get the item's id
        self.expectArg("-i")
        itemId = self.getNextArg()
    
        # Get the password
        self.expectArg("-p")
        password = self.getNextArg()

        self.checkout(itemId, password)
    
    # Parses and calls execution of the remove argument
    # Receives no value
    # Returns no value
    def _parse_remove(self):
        # Get the item's id
        self.expectArg("-i")
        itemId = self.getNextArg()
    
        # Get the reason
        whyForm = self.peekNextArg()
        if (whyForm == "-y"):
            self.expectArg("-y")
        else:
            self.expectArg("--why")
        
        reason = self.getNextArg().upper() # NOTE: the conversion to uppercase
        self.verifyReason(reason)

        # Check if there is an owner released to, verifying and saving if so
        tempArg = self.peekNextArg()
        owner = ""
        if (reason == "RELEASED"): 
            self.expectArg("-o")
            owner = self.getNextArg().upper() # NOTE: the conversion to uppercase
            self.verifyOwner(owner)

        # Get the password
        self.expectArg("-p")
        password = self.getNextArg()

        self.remove(itemId, reason, owner, password)

    # Verifies whether or not a given reason is one of the valid 3, throwing an error if not
    # Receives the reason given as an argument
    # Returns no value
    def verifyReason(self, reason):
        # Check for any match, returning if found
        for acceptReason in self.acceptableReasons:
            if (reason == acceptReason):
                return

        # Throw an error if no match is found
        print("Invalid reason (Expects: DISPOSED, DESTROYED, or RELEASED)")
        exit(1)

    # Verifies whether or not a given owner is one of the valid 4, throwing an error if no
    # Receives the owner as a string
    # Returns no value
    def verifyOwner(self, owner):
        # Check for any match, returing if found
        for acceptOwner in self.acceptableOwners:
            if (owner == acceptOwner):
                return
        
        # Throw an error if no match is found
        print("Invalid owner (Expects: POLICE, LAWYER, ANALYST, or EXECUTIVE)")
        exit(1)

    # Parses and calls execution of the cases argument from the show branch
    # Receives no value
    # Returns no value
    def _parse_show_cases(self):
        # get the password
        self.expectArg("-p")
        password = self.getNextArg()

        self.show_cases(password)
    
    # Parses and calls execution of the items argument from the show branch
    # Receives no value
    # Returns no value 
    def _parse_show_items(self):
        # Get the case-id
        self.expectArg("-c")
        caseID = self.getNextArg()

        # Get the password
        self.expectArg("-p")
        password = self.getNextArg()

        self.show_items(caseID, password)


    # Parses and calls execution of the cases argument from the show branch
    # Receives no value
    # Returns no value
    def _parse_show_history(self):
        caseID = ""
        itemID = ""
        numEntries = ""
        isReversed = False

        # Check for caseID, saving if there
        tempArg = self.peekNextArg()
        if (tempArg == "-c"):
            self.expectArg("-c")
            caseID = self.getNextArg()
        
        # Check for itemID, saving if there 
        tempArg = self.peekNextArg()
        if (tempArg == "-i"):
            self.expectArg("-i")
            itemID = self.getNextArg()
        
        # Check for a number of entries, saving if there
        tempArg = self.peekNextArg()
        if (tempArg == "-n"):
            self.expectArg("-n")
            numEntries = self.getNextArg()

        # Check if reverse is requested
        tempArg = self.peekNextArg()
        if (tempArg == "-r"):
            self.expectArg("-r")
            isReversed = True
        elif (tempArg == "--reverse"):
            self.expectArg("--reverse")
            isReversed = True

        # Get the password
        self.expectArg("-p")
        password = self.getNextArg()

        # self.show_history(caseID, itemID, numEntries, isReversed, password)


    def add(self, case_id, item_ids, creator, password):
        for item_id in item_ids:
            if(self.chain.item_id_exist(item_id)):   
                print("Error: Item ID [" + str(item_id) + "] already exists in the blockchain")
                exit(1)
        
        data = "" # Data is empty for now, will be provided?
        
        for item_id in item_ids:
            newBlock = blockchain.Block(self.chain.get_last_block_hash(), "CHECKEDIN", data, self.aes_key, case_id, item_id, creator, owner=None)
            newBlock.write_block(self.path)
            
    def checkin(self, item_id, password):
        if(not self.chain.item_id_exist(item_id)):   
            print("Error: Cannot Check In [" + str(item_id) + "]. Item ID does not exist in the blockchain")
            exit(1)
        if(self.chain.is_checkedIn(item_id)):
            print("Error: Cannot Check In [" + str(item_id) + "]. Item ID is already checked in")
            exit(1)
        self.chain.checkin(item_id)
        
    def checkout(self, item_id, password):
        if(not self.chain.item_id_exist(item_id)):   
            print("Error: Cannot Check out [" + str(item_id) + "]. Item ID does not exist in the blockchain")
            exit(1)
        if(not self.chain.is_checkedIn(item_id)):
            print("Error: Cannot Check out [" + str(item_id) + "]. Item ID is already checked out")
            exit(1)
        self.chain.checkout(item_id)
        
    def show_cases(self, password):
        print("Exisitng Cases: " + self.chain.get_cases())
        
    def show_items(self, caseID, password):
        if not self.chain.case_id_exist(caseID):
            print("Error: Cannot show items. Case ID does not exist in the blockchain")
            exit(1)
        print("Evidences Under Case [" + caseID + "]: " + self.chain.get_items(caseID))
        
    def show_history(self):
        WIP
    def remove(self, item_id, reason, owner, password):
        # reason is one of DISPOSED, DESTROYED, RELEASED
        if(not self.chain.item_id_exist(item_id)):   
            print("Error: Cannot remove" + str(item_id) + ". Item ID does not exist in the blockchain")
            exit(1)
        self.chain.remove(item_id, reason, owner)
    

    def initOutput(self):
        if (self.bchocFileExists):
            print("Blockchain file found with INITIAL block.")
        else:
            print("Blockchain file not found. Created INITIAL block.")
    
    def verify(self):
        state = "OKAY"
        badblock = self.chain.verify()
        if badblock!=0:
            state = "ERROR"
        print("Transactions in blockchain: " + str(self.chain.get_blockcount()))
        print("State of blockchain: " + state)
        if badblock:
            print("Bad block: " + badblock)
            exit(1)
