import hashlib
import json


class Transaction:
    def __init__(self, fromAddress, toAddress, amount):
        self.fromAddress = fromAddress
        self.toAddress = toAddress
        self.amount = amount

class Block:
    def __init__(self, transactions, previousHash):
        self.transactions=transactions
        self.previousHash=previousHash
        self.hashVal=self.calculateHash(transactions)

    def mineBlock(self):
        pass

    def calculateHash(self, data):
        hashVal = hashlib.sha256(json.dumps(data, sort_keys=True).encode())
        return str(hashVal.hexDigest())

class Blockchain():
    def __init__(self):
        self.pendingTransactions = []
        genesisBlock = Block(transactions=[], previousHash=0)
        self.chain = [genesisBlock]

    def __repr__(self):
        return str(self.pendingTransactions)

    def mineBlock(self):
        newBlock = Block(transactions=self.pendingTransactions, previousHash=self.chain[-1].hashVal)
        self.chain.append(newBlock)
        self.pendingTransactions=[]

    def addTransaction(self, data):
        self.pendingTransactions.append(data)



myBlockchain = Blockchain()

myBlockchain.addTransaction(Transaction("a", "b", 100))

print(myBlockchain)
