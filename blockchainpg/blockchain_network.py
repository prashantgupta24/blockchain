import shelve
import json
import rsa
import requests
from flask import Flask, request

from blockchainpg.core import Blockchain, Transaction
from blockchainpg.blockchain_utils import convertToPrivKey, convertToPubKey
from blockchainpg.network_utils import isDataValid, deconstructTransactionFromJson, getBlockchainDataFromJson, runConsensusAlgorithm, writeBlockchainToDb, propagateTransactionToAllNodes

class BlockchainNetwork():
    def __init__(self):
        self.blockchainDb = shelve.open("blockchainDb")
        self.blockchain = Blockchain()
        self.debug = True

        if 'blockchain.chain' in self.blockchainDb:
            try:
                self.blockchain.chain = self.blockchainDb['blockchain.chain']
                self.blockchain.nodes = self.blockchainDb['blockchain.nodes']
                self.blockchain.pendingTransactions = self.blockchainDb['blockchain.pendingTransactions']
                if self.debug:
                    print("Blockchain found in db! Extracted information from it")
            except Exception:
                if self.debug:
                    print("Error extracting information from blockchain db")
                self.blockchain.setupGenesisBlock()
        else:
            if self.debug:
                print("Blockchain not found in db! Creating new")
            self.blockchain.setupGenesisBlock()

def createApp():
    app = Flask('pgBlockchain')
    blockchainNetwork = BlockchainNetwork()


    @app.route('/blockchain', methods=['GET'])
    def getBlockchain():
        return str(blockchainNetwork.blockchain), 200

    @app.route('/balance/<pubKeyStr>', methods=['GET'])
    def getBalance(pubKeyStr):
        return "Coins left: " + str(blockchainNetwork.blockchain.getBalance(user=convertToPubKey(pubKeyStr))), 200

    """
    Called by the /mine endpoint. This is to broadcast to all the nodes in the blockchain that a new block is mined. The consensus algorithm runs after this broadcast message, and the longest valid chain takes preference and all nodes are updated.

    """
    @app.route('/mine/broadcast', methods=['POST'])
    def newBlockFound():
        result, message = runConsensusAlgorithm(blockchainNetwork=blockchainNetwork)
        if blockchainNetwork.debug:
            print(f"Result from consensus is {result} with message {message}")
        writeBlockchainToDb(blockchainNetwork=blockchainNetwork)
        return "", 200

    @app.route('/mine/<pubKeyStr>', methods=['GET'])
    def mineBlock(pubKeyStr):
        blockchainNetwork.blockchain.mineBlock(user=convertToPubKey(pubKeyStr))
        for node in blockchainNetwork.blockchain.nodes:
            try:
                requests.post(f'http://{node}/mine/broadcast', json = {})
            except Exception:
                if blockchainNetwork.debug:
                    print(f"Node {node} not reachable...")
        writeBlockchainToDb(blockchainNetwork=blockchainNetwork)
        return "Block mined!", 201

    """
    An internal endpoint. This is called when a new node registers onto the blockchain system. The master node's address book is updated with the new node's address, and the new node copies the blockchain data from the master.
    """
    @app.route('/blockchain/internal/add/node', methods=['POST'])
    def addNodeToBlockchain():
        data = request.get_json()
        nodeAddress = data["MyAddress"]
        blockchainNetwork.blockchain.nodes.add(nodeAddress)
        writeBlockchainToDb(blockchainNetwork=blockchainNetwork)
        return "", 201

    @app.route('/new/node', methods=['POST'])
    def addNewNode():
        try:
            data = request.get_json()
            masterAddress = data["Master"]
            nodeAddress = data["MyAddress"]
            requests.post(f'http://{masterAddress}/blockchain/internal/add/node', json = {"MyAddress":nodeAddress})
            (result, blockchainNetwork.blockchain) = getBlockchainDataFromJson(requests.get(f'http://{masterAddress}/blockchain').json())
            writeBlockchainToDb(blockchainNetwork=blockchainNetwork)
            if not result:
                return "Error fetching from master!", 404
            return "Your node was updated!", 201

        except Exception as e:
            print(e)
            #raise e
            return "Invalid json!", 500

    @app.route('/new/keys', methods=['GET'])
    def getKeys():
        keyMap = {}
        [pub_key, priv_key]=rsa.newkeys(512)
        pub_key_str = str(pub_key)
        priv_key_str = str(priv_key)
        keyMap["publicKey"] = pub_key_str[pub_key_str.index("(")+1:pub_key_str.index(")")]
        keyMap["privateKey"] = priv_key_str[priv_key_str.index("(")+1:priv_key_str.index(")")]
        return json.dumps(keyMap, indent=2), 201


    """
    This endpoint is called when a new transaction is added to the blockchain. If the transaction is valid, it is propogated to all the nodes in the network.
    """
    @app.route('/new/signedTransaction', methods=['POST'])
    def addNewSignedTransaction():
        data = request.get_json()
        transaction = deconstructTransactionFromJson(data)
        blockchainNetwork.blockchain.addTransaction(transaction)
        return "Success!", 201

    @app.route('/new/transaction', methods=['POST'])
    def addTransaction():
        data = request.get_json()
        try:
            valid, messageResponse = isDataValid(data)

            if valid:
                transaction = Transaction(fromAddress=convertToPubKey(data["FromAddress"]), toAddress=convertToPubKey(data["ToAddress"]), amount=int(data["Amount"]))
                signature = rsa.sign(str(transaction).encode(encoding='utf_8'), convertToPrivKey(data["priv_key"]), "SHA-256")
                transaction.addSignature(signature=signature.hex())

                result, message = blockchainNetwork.blockchain.addTransaction(transaction=transaction)

                if result:
                    finalMessage = message + " " + getBalance(data["FromAddress"])[0]
                    writeBlockchainToDb(blockchainNetwork=blockchainNetwork)
                    propagateTransactionToAllNodes(blockchainNetwork=blockchainNetwork, transaction=transaction)
                    return finalMessage, 201

                return message, 400

            else:
                return messageResponse, 500
        except ValueError as e:
            print(e)
            return "Invalid json!", 500
        except OverflowError as e:
            print(e)
            return "Invalid key! Please check both public and private keys", 500
        except KeyError as e:
            print(e)
            return "Missing a field! Please check all required fields are present", 500
        except Exception as e:
            print(e)
            return "Server error!", 500

    return app

if __name__ == '__main__':
    createApp()
