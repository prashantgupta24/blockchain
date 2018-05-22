import os
import hashlib
import json
import time
import rsa
from dotenv import load_dotenv

load_dotenv()

class Transaction:
    def __init__(self, fromAddress, toAddress, amount):
        self.fromAddress = fromAddress
        self.toAddress = toAddress
        self.amount = amount
        self.timestamp = time.time()
        self.signature = ""

    def __repr__(self):
        return json.dumps(self.getData(), indent = 2)

    def __eq__(self, other):
        return self.signature == other.signature

    def __hash__(self):
        return hash(self.signature)

    def addSignature(self, signature):
        self.signature = signature

    def getData(self):
        return {
            "Timestamp": self.timestamp,
            "From_address": str(self.fromAddress),
            "To_address": str(self.toAddress),
            "Amount": self.amount
        }


class Block:
    def __init__(self, transactions, previousHash, miningDifficulty):
        self.transactions=transactions
        self.previousHash=previousHash
        self.nonce = 0
        self.miningDifficulty = miningDifficulty
        self.hashVal=self.calculateHash()

    def getData(self):
        blockData = {}
        blockData["Transactions"] = []
        for transaction in self.transactions:
            blockData["Transactions"].append(transaction.getData())
        blockData["Previous hash"] = self.previousHash
        blockData["My hash"] = self.hashVal
        return blockData

    def calculateHash(self):
        data = {}
        data["transactions"] = [x.getData() for x in self.transactions]
        data["previousHash"] = self.previousHash
        data["nonce"] = self.nonce

        hashVal = hashlib.sha256(json.dumps(data, sort_keys=True).encode())
        hexdigest = hashVal.hexdigest()
        while(hexdigest)[:self.miningDifficulty] != "0"*self.miningDifficulty:
            data["nonce"] += 1
            hashVal = hashlib.sha256(json.dumps(data, sort_keys=True).encode())
            hexdigest = hashVal.hexdigest()

        return str(hashVal.hexdigest())

class Blockchain():
    def __init__(self):
        self.pendingTransactions = set()
        self.debug = True
        self.minedCoinbase = 50
        self.miningDifficulty = 2
        genesisBlock = Block(transactions=[], previousHash=0, miningDifficulty=self.miningDifficulty)
        self.chain = [genesisBlock]

    def __repr__(self):
        return json.dumps(self.getData(), indent = 2)

    def getData(self):
        chainData = {}
        chainData["lengthOfChain"] = len(self.chain)
        chainData["Blocks"] = {}
        for block in self.chain:
            chainData["Blocks"]["Block " + str(self.chain.index(block))] = block.getData()
        return chainData

    def mineBlock(self, user):
        isChainValid, issueBlock = self.isChainValid()
        if isChainValid:
            miningTransaction = Transaction(fromAddress=convertToPubKey(os.getenv("PUB_KEY")), toAddress=user, amount=self.minedCoinbase)
            signature = rsa.sign(str(miningTransaction).encode(encoding='utf_8'), convertToPrivKey(os.getenv("PRIV_KEY")), "SHA-256")
            miningTransaction.addSignature(signature=signature)

            pendingTransactionsForBlock = list(self.pendingTransactions)
            pendingTransactionsForBlock.insert(0, miningTransaction)

            newBlock = Block(transactions=pendingTransactionsForBlock, previousHash=self.chain[-1].hashVal, miningDifficulty=self.miningDifficulty)
            self.chain.append(newBlock)
            self.pendingTransactions = set()
        else:
            print(f"Chain is not valid! Someone tampered with the data! Issue with block {issueBlock}. Removing block {issueBlock} ...")
            if self.debug:
                print("\nBlock which is being removed is:\n")
                print(self.chain[issueBlock])
            self.chain = self.chain[:issueBlock]

    def isChainValid(self):
        allTransactions = set()

        for blockNum in range(len(self.chain)):
            block = self.chain[blockNum]

            if block.hashVal != block.calculateHash() or (blockNum < len(self.chain) - 1 and self.chain[blockNum+1].previousHash != block.hashVal):
                if self.debug:
                    print("block hash not matching!")
                return False, blockNum

            for transaction in block.transactions:
                if transaction.signature in allTransactions:
                    if self.debug:
                        print(f"Transaction already present \n{transaction}")
                    return False, blockNum
                else:
                    allTransactions.add(transaction.signature)

                    if not self.isTransactionValid(transaction=transaction):
                        if self.debug:
                            print(f"Transaction signature not matching! {transaction}")
                        return False, blockNum

        return True, -1


    def getBalance(self, user):
        balance = 0
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.toAddress == user:
                    balance += transaction.amount
                if transaction.fromAddress == user:
                    balance -= transaction.amount

        for transaction in self.pendingTransactions:
            if transaction.toAddress == user:
                balance += transaction.amount
            if transaction.fromAddress == user:
                balance -= transaction.amount

        return balance

    def addTransaction(self, transaction):
        if not isinstance(transaction, Transaction):
            return False, f"Not a transaction object!\n{transaction}!\n"
        if transaction in self.pendingTransactions:
            return False, f"Transaction already present!\n{transaction}!\n"
        if not self.isTransactionValid(transaction=transaction):
            return False, f"Incorrect signature for transaction\n{transaction}!\n"

        userBalance = self.getBalance(transaction.fromAddress)
        if userBalance < transaction.amount:
            return False, f"Insufficient balance! You only have {userBalance} coins but you are trying to send {transaction.amount}"

        self.pendingTransactions.add(transaction)
        return True, "Transaction added successfully!"

    @staticmethod
    def isTransactionValid(transaction):
        if transaction.signature == "":
            return False

        try:
            rsa.verify(str(transaction).encode(encoding='utf_8'), transaction.signature, transaction.fromAddress)
        except rsa.VerificationError:
            return False

        return True

def convertToPubKey(pubKeyStr):
    n, e = [int(key.strip()) for key in pubKeyStr.split(",")]
    return rsa.PublicKey(n=n, e=e)

def convertToPrivKey(privKeyStr):
    n, e, d, p, q = [int(key.strip()) for key in privKeyStr.split(",")]
    return rsa.PrivateKey(n=n, e=e, d=d, p=p, q=q)
