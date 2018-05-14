import hashlib
import json

class Blockchain():
    def __init__(self):
        self.transactions = []

    def __repr__(self):
        return str(self.transactions)

    def addBlock(self, data):
        self.transactions.append(data)

    def getHash(self, data):
        hashVal = hashlib.sha256(json.dumps(data, sort_keys=True).encode())
        return str(hashVal.hexDigest())

blockchain = Blockchain()
blockchain.addBlock(1)
blockchain.addBlock(4)
blockchain.addBlock(5)

print(blockchain)
