import hashlib
import json
import rsa

class Transaction:
    def __init__(self, fromAddress, toAddress, amount):
        self.fromAddress = fromAddress
        self.toAddress = toAddress
        self.amount = amount
        self.signature = ""

    def __repr__(self):
        return f"From {self.fromAddress} to {self.toAddress}, amount:{self.amount}"

    def addSignature(self, signature):
        self.signature = signature

    def getData(self):
        return {"from_address":str(self.fromAddress), "to_address":str(self.toAddress), "amount":self.amount}

class Block:
    def __init__(self, transactions, previousHash):
        self.transactions=transactions
        self.previousHash=previousHash
        self.hashVal=self.calculateHash()

    def __repr__(self):
        return f"Transactions are {str(self.transactions)} \nPrevious hash is {self.previousHash} \nMy hash is {self.hashVal}"

    def calculateHash(self):
        data = [x.getData() for x in self.transactions]
        data.append(self.previousHash)
        #print(f"data is {data}")
        hashVal = hashlib.sha256(json.dumps(data, sort_keys=True).encode())
        return str(hashVal.hexdigest())

class Blockchain():
    def __init__(self):
        self.pendingTransactions = []
        genesisBlock = Block(transactions=[], previousHash=0)
        self.chain = [genesisBlock]

    def __repr__(self):
        result = []
        for block in self.chain:
            result.append("Block " + str(self.chain.index(block))+"\n\n"+str(block))
        return "\n\n".join(result)

    def mineBlock(self, user):
        isChainValid, issueBlock = self.validateChain()
        if isChainValid:
            self.pendingTransactions.insert(0, Transaction(fromAddress="SYSTEM", toAddress=user, amount=50))
            newBlock = Block(transactions=self.pendingTransactions, previousHash=self.chain[-1].hashVal)
            self.chain.append(newBlock)
            self.pendingTransactions=[]
        else:
            print(f"Chain is not valid! Someone tampered with the data! Issue with block {issueBlock}")

    def validateChain(self):
        result = True
        issueBlock = 0
        # for i in range(1,len(self.chain)):
        #     block1 = self.chain[i-1]
        #     block2 = self.chain[i]
        #
        #     if block1.hashVal != block1.calculateHash():
        #         result = False
        #         issueBlock = block1
        #
        #     if block2.hashVal != block2.calculateHash():
        #         result = False
        #         issueBlock = block2
        #
        #     if block2.previousHash != block1.hashVal:
        #         result = False
        #         issueBlock

        for i in range(len(self.chain)):
            if self.chain[i].hashVal != self.chain[i].calculateHash() or (i < len(self.chain) - 1 and self.chain[i+1].previousHash != self.chain[i].hashVal):
                result = False
                issueBlock = i

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
        if self.getBalance(transaction.fromAddress) >= transaction.amount:
            self.pendingTransactions.append(transaction)
        else:
            print(f"Insufficient balance! You only have {self.getBalance(transaction.fromAddress)} coins but you are trying to send {transaction.amount}")

    def isTransactionValid(self, transaction):
        if transaction.signature == "" or not rsa.verify(str(transaction).encode(encoding='utf_8'), transaction.signature, transaction.fromAddress):
            return False

        return True


# (pub, priv) = rsa.newkeys(512)
# print(pub)
