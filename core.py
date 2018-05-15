import hashlib
import json


class Transaction:
    def __init__(self, fromAddress, toAddress, amount):
        self.fromAddress = fromAddress
        self.toAddress = toAddress
        self.amount = amount

    def __repr__(self):
        return f"From {self.fromAddress} to {self.toAddress}, amount:{self.amount}"

    def getData(self):
        return {"from_address":self.fromAddress, "to_address":self.toAddress, "amount":self.amount}

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

    def mineBlock(self):
        newBlock = Block(transactions=self.pendingTransactions, previousHash=self.chain[-1].hashVal)
        self.chain.append(newBlock)
        self.pendingTransactions=[]

    def isChainValid(self):
        for i in range(1,len(self.chain)):
            block1 = self.chain[i-1]
            block2 = self.chain[i]

            if block1.hashVal != block1.calculateHash():
                return False

            if block2.previousHash != block1.hashVal:
                return False

        return True


    def getBalance(self, user):
        balance = 0
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.toAddress == user:
                    balance += transaction.amount
                if transaction.fromAddress == user:
                    balance -= transaction.amount

        return balance

    def addTransaction(self, data):
        self.pendingTransactions.append(data)
