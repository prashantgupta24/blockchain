import hashlib
import json
import time
import rsa

class Transaction:
    def __init__(self, fromAddress, toAddress, amount):
        self.fromAddress = fromAddress
        self.toAddress = toAddress
        self.amount = amount
        self.timestamp = time.time() #TODO unique timestamp in one ?
        self.signature = ""

    def __repr__(self):
        #return f"From {self.fromAddress} to {self.toAddress}, amount:{self.amount}"
        return str(self.getData())

    def addSignature(self, signature):
        self.signature = signature

    def getData(self):
        return {"timestamp":self.timestamp, "from_address":str(self.fromAddress), "to_address":str(self.toAddress), "amount":self.amount}

class Block:
    def __init__(self, transactions, previousHash):
        self.transactions=transactions
        self.previousHash=previousHash
        self.hashVal=self.calculateHash()
        self.nonce = 0 #TODO

    def __repr__(self):
        return f"Transactions are {str(self.transactions)} \n\nPrevious hash is {self.previousHash} \nMy hash is {self.hashVal}"

    def calculateHash(self):
        #TODO POW
        data = [x.getData() for x in self.transactions]
        data.append(self.previousHash)
        #print(f"data is {data}")
        hashVal = hashlib.sha256(json.dumps(data, sort_keys=True).encode())
        return str(hashVal.hexdigest())

class Blockchain():
    def __init__(self):
        self.pendingTransactions = []
        self.debug = True
        self.minedCoinbase = 50
        genesisBlock = Block(transactions=[], previousHash=0)
        self.chain = [genesisBlock]

    def __repr__(self):
        result = []
        for block in self.chain:
            result.append("\nBlock " + str(self.chain.index(block))+"\n\n"+str(block))
        return "\n\n".join(result)

    def mineBlock(self, user):
        isChainValid, issueBlock = self.validateChain()
        if isChainValid:
            self.pendingTransactions.insert(0, Transaction(fromAddress="SYSTEM", toAddress=user, amount=self.minedCoinbase))
            newBlock = Block(transactions=self.pendingTransactions, previousHash=self.chain[-1].hashVal)
            self.chain.append(newBlock)
            self.pendingTransactions=[]
        else:
            print(f"Chain is not valid! Someone tampered with the data! Issue with block {issueBlock}. Removing block {issueBlock}...")
            if self.debug:
                print(self.chain[issueBlock])
            self.chain = self.chain[:issueBlock]


    def validateChain(self):
        result = True
        issueBlock = 0

        for i in range(len(self.chain)):
            block = self.chain[i]
            #print(block)

            if block.hashVal != block.calculateHash() or (i < len(self.chain) - 1 and self.chain[i+1].previousHash != block.hashVal):
                if self.debug:
                    print("block hash not matching!")
                result = False
                issueBlock = i
                break

            for transaction in block.transactions:
                if transaction.fromAddress == "SYSTEM":
                    if transaction.amount != self.minedCoinbase:
                        if self.debug:
                            print(f"transaction SYSTEM not matching! {transaction}")
                        result = False
                        issueBlock = i
                        break

                elif not self.isTransactionValid(transaction=transaction):
                    if self.debug:
                        print(f"Transaction not matching! {transaction}")
                    result = False
                    issueBlock = i
                    break

                elif self.getBalance(transaction.fromAddress) < transaction.amount:
                    if self.debug:
                        print(f"Balance not proper! {transaction}")
                    result = False
                    issueBlock = i
                    break

        return result, issueBlock


    def getBalance(self, user):
        balance = 0
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.toAddress == user:
                    balance += transaction.amount
                if transaction.fromAddress == user:
                    balance -= transaction.amount

        return balance

    def addTransaction(self, transaction):
        if not self.isTransactionValid(transaction=transaction):
            print(f"Incorrect signature for transaction\n{transaction}!\n")
        elif self.getBalance(transaction.fromAddress) >= transaction.amount:
            self.pendingTransactions.append(transaction)
        else:
            print(f"Insufficient balance! You only have {self.getBalance(transaction.fromAddress)} coins but you are trying to send {transaction.amount}")

    @staticmethod
    def isTransactionValid(transaction):
        if transaction.signature == "":
            return False

        try:
            rsa.verify(str(transaction).encode(encoding='utf_8'), transaction.signature, transaction.fromAddress)
        except rsa.VerificationError:
            return False

        return True
