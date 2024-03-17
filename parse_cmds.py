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
    
    def __init__(self, argv):
        if('AES_KEY' in os.environ):
            self.aes_key = os.environ['AES_KEY']  # provided key
        else:
            self.aes_key = 1234567890123456  # raw key
        
        if('BCHOC_FILE_PATH' in os.environ):
            self.path = os.environ['BCHOC_FILE_PATH']   # provided path
        else:
            self.path = os.getcwd() + "/bchoc.dat"  # raw binary file

        # save arguments
        self.arguments = argv
                
        # Parse commands and execute them
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
        operation = self.getNextArg() # NOTE: Verify that this is @ 0

        # No blockchain file exits, create one and note creation NOTE: MAY REQUIRE REPAIR
        bchocFileExists = True
        if not os.path.exists(self.path):
            bchocFileExists = False # for use in init, prevents repeat creation

            previous_hash = None  # first block no prev hash, all 0s.
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
            self.init(bchocFileExists)
        elif operation == "verify":
            self.verify()
        else:
            print("Invalid command")
            exit(1);
            
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
        
        # self.add(case_id, item_ids, creator, password)    

    # Parses and calls execution of the show argument
    # Receives no value
    # Returns no value
    def _parse_show(self):
        # Get the show type
        showType = self.getNextArg();

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

        # self.checkin(itemId, password)
    
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

        # self.checkout(itemId, password)
    
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
        
        reason = self.getNextArg()
        self.verifyReason(reason)

        # Check if there is an owner released to, saving if so
        tempArg = self.peekNextArg()
        owner = ""
        if (reason == "RELEASED"): # NOTE: check that this needs to be all uppercase
            self.expectArg("-o")
            owner = self.getNextArg()

        # Get the password
        self.expectArg("-p")
        password = self.getNextArg()

        # self.remove(itemId, reason, owner, password)

    # Verifies whether or not a given reason is one of the valid 3, throwing an error if not
    # Receives the reason given as an argument
    # Returns no value
    def verifyReason(self, reason):
        # Check for any match
        isDisposed = reason == "DISPOSED"
        isDestroyed = reason == "DESTROYED"
        isReleased = reason == "RELEASED"

        # Throw an error if none match
        if (isDisposed or isDestroyed or isReleased):
            return
        else:
            print("Invalid reason (Expects: DISPOSED, DESTROYED, or RELEASED)")
            exit(1);

    # Parses and calls execution of the cases argument from the show branch
    # Receives no value
    # Returns no value
    def _parse_show_cases(self):
        # get the password
        self.expectArg("-p")
        password = self.getNextArg()

        # self.show_cases(password)
    
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

        # self.show_items(caseID, password)


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
            caseID = self.getNextArg();
        
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
            WIP
    def checkin(self, itemID, password):
        WIP
    def checkout(self, itemID, password):
        WIP
    def show_cases(self, password):
        WIP
    def show_items(self, caseID, password):
        WIP
    def show_history(self):
        WIP
    def remove(self, itemId, reason, owner, password):
        WIP
    

    # Executes the init argument
    # Receives a boolean representing whether or not the blockchain file was found earlier
    # Returns no value
    def init(self, bchocFileExists):
        if (bchocFileExists):
            print("Blockchain file found with INITIAL block.")
        else:
            print("Blockchain file not found. Created INITIAL block.")
    
    # Executes the verify argument
    # Receives no value
    # Returns no value
    def verify(self):
        Chain = blockchain.Chain(self.path, self.aes_key)
