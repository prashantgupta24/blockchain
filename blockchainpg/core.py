import os
import hashlib
import json
import time
import rsa
from dotenv import load_dotenv, find_dotenv

from blockchainpg.blockchain_utils import convertToPrivKey, convertToPubKey

load_dotenv(find_dotenv())

"""
The transaction class holds all aspects of a transaction object, which includes the addresses, timestamp, and
most importantly, the signature. Due to the signature, a transaction cannot be modified in any way, and can neither be duplicated. The signature is what holds the authenticity of a transaction.
"""

class Transaction:
    def __init__(self, fromAddress, toAddress, amount, timestamp=None, signature=None):
        self.fromAddress = fromAddress
        self.toAddress = toAddress
        self.amount = amount
        if timestamp:
            if isinstance(timestamp, str):
                self.timestamp = float(timestamp)
            elif isinstance(timestamp, float):
                self.timestamp = timestamp
            else:
                self.timestamp = time.time()
        else:
            self.timestamp = time.time()

        if signature:
            if isinstance(signature, str):
                self.signature = signature
            elif isinstance(signature, bytes):
                self.signature =signature.hex()
            else:
                self.signature = ""
        else:
            self.signature = ""

    def __repr__(self):
        data = {
            "Timestamp": self.timestamp,
            "FromAddress": str(self.fromAddress),
            "ToAddress": str(self.toAddress),
            "Amount": self.amount
        }
        return json.dumps(data, indent = 2)

    def __eq__(self, other):
        return self.signature == other.signature

    def __hash__(self):
        return hash(self.signature)

    def addSignature(self, signature):
        self.signature = signature

    def getData(self):
        return {
            "Timestamp": self.timestamp,
            "FromAddress": str(self.fromAddress),
            "ToAddress": str(self.toAddress),
            "Amount": self.amount,
            "Signature": self.signature
        }

"""
The block is also an integral part of the blockchain. It holds a set of verified transactions, and it has a hash value calculated based on the mining difficulty set. The nonce value is incremented until the hashVal has the corresponding number of zeros.
"""
class Block:
    def __init__(self, transactions, previousHash, miningDifficulty, nonce=0, hashVal=None):
        self.transactions=transactions
        self.previousHash=previousHash
        self.nonce = nonce
        self.miningDifficulty = miningDifficulty
        if hashVal is None:
            self.hashVal=self.calculateHash()
        else:
            self.hashVal = hashVal

    def getData(self):
        blockData = {}
        blockData["Transactions"] = []
        for transaction in self.transactions:
            blockData["Transactions"].append(transaction.getData())
        blockData["PreviousHash"] = self.previousHash
        blockData["MyHash"] = self.hashVal
        blockData["Nonce"] = self.nonce
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

        self.nonce = data["nonce"]
        return str(hashVal.hexdigest())

class Blockchain():
    def __init__(self):
        self.debug = True
        self.minedCoinbase = 50
        self.miningDifficulty = 5
        self.chain = []
        self.nodes = set()
        self.pendingTransactions = set()

    def setupGenesisBlock(self):
        genesisBlock = Block(transactions=[], previousHash=0, miningDifficulty=self.miningDifficulty)
        self.chain.append(genesisBlock)

    def __repr__(self):
        return json.dumps(self.getData(), indent = 2)

    def getData(self):
        chainData = {}
        chainData["LengthOfChain"] = len(self.chain)
        chainData["Nodes"] = list(self.nodes)
        chainData["Blocks"] = {}
        chainData["PendingTransactions"] = []
        for block in self.chain:
            chainData["Blocks"]["Block " + str(self.chain.index(block))] = block.getData()
        for transaction in self.pendingTransactions:
            chainData["PendingTransactions"].append(transaction.getData())
        return chainData

    def mineBlock(self, user):
        isChainValid, issueBlock = self.isChainValid()
        if isChainValid:
            miningTransaction = Transaction(fromAddress=convertToPubKey(os.getenv("PUB_KEY")), toAddress=user, amount=self.minedCoinbase)
            signature = rsa.sign(str(miningTransaction).encode(encoding='utf_8'), convertToPrivKey(os.getenv("PRIV_KEY")), "SHA-256")
            miningTransaction.addSignature(signature=signature.hex())

            verifiedTransactionsForBlock = []
            for transaction in self.pendingTransactions:
                if self._isTransactionValid(transaction=transaction):
                    verifiedTransactionsForBlock.append(transaction)

            verifiedTransactionsForBlock.insert(0, miningTransaction)

            newBlock = Block(transactions=verifiedTransactionsForBlock, previousHash=self.chain[-1].hashVal, miningDifficulty=self.miningDifficulty)
            self.chain.append(newBlock)
            self.pendingTransactions = self.pendingTransactions - set(verifiedTransactionsForBlock)
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
                    result, message = self._isTransactionValid(transaction=transaction)
                    if not result:
                        if self.debug:
                            print(message)
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
        result, message = self._isTransactionValid(transaction=transaction)
        if not result:
            return False, message

        self.pendingTransactions.add(transaction)
        return True, "Transaction added successfully!"

    def _isTransactionValid(self, transaction):
        if transaction.signature == "":
            return False, "Signature empty!"

        if not isinstance(transaction, Transaction):
            return False, f"Not a transaction object!\n{transaction}!\n"

        if transaction in self.pendingTransactions:
            return False, f"Transaction already present!\n{transaction}!\n"

        userBalance = self.getBalance(transaction.fromAddress)
        if userBalance < transaction.amount:
            if convertToPubKey(os.getenv("PUB_KEY")) != transaction.fromAddress:
                return False, f"Insufficient balance! You only have {userBalance} coins but you are trying to send {transaction.amount}"

        try:
            rsa.verify(str(transaction).encode(encoding='utf_8'), bytes.fromhex(transaction.signature), transaction.fromAddress)
        except rsa.VerificationError:
            return False, f"signature not matching!"

        return True, "Valid"
