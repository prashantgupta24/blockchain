import shelve
import json
import rsa
import requests
from flask import Flask, request
from core import Blockchain, Transaction, Block, convertToPubKey, convertToPrivKey

class BlockchainNetwork():
    def __init__(self):
        self.blockchainDb = shelve.open("blockchainDb")
        self.blockchain = Blockchain()

        if 'blockchain.chain' in self.blockchainDb:
            try:
                self.blockchain.chain = self.blockchainDb['blockchain.chain']
                self.blockchain.nodes = self.blockchainDb['blockchain.nodes']
                self.blockchain.pendingTransactions = self.blockchainDb['blockchain.pendingTransactions']
            except Exception:
                pass


app = Flask(__name__)

blockchainNetwork = BlockchainNetwork()

@app.route('/blockchain', methods=['GET'])
def getBlockchain():
    return str(blockchainNetwork.blockchain), 200
#
# @app.route('/blockchain/db')
# def blockchainDBFile():
#     try:
#         return send_file('blockchainDb.db')
#     except Exception as e:
#         return str(e)

@app.route('/balance/<pubKeyStr>', methods=['GET'])
def getBalance(pubKeyStr):
    return "Coins left: " + str(blockchainNetwork.blockchain.getBalance(user=convertToPubKey(pubKeyStr))), 200

@app.route('/mine/<pubKeyStr>', methods=['GET'])
def mineBlock(pubKeyStr):
    blockchainNetwork.blockchain.mineBlock(user=convertToPubKey(pubKeyStr))
    writeBlockchainToDb()
    return "Block mined!", 201

# @app.route('/blockchain/new/node', methods=['POST'])
# def addNodeToBlockchain():
#     data = request.get_json()
#     nodeAddress = data["MyAddress"]
#     blockchain.nodes.add(nodeAddress)
#     runConsensusAlgorithm()
#     return "Node added!", 201

@app.route('/blockchain/internal/add/node', methods=['POST'])
def addNodeToBlockchain():
    data = request.get_json()
    nodeAddress = data["MyAddress"]
    blockchainNetwork.blockchain.nodes.add(nodeAddress)
    writeBlockchainToDb()
    #return "|".join(blockchain.nodes), 200
    return "", 201

@app.route('/blockchain/new/node', methods=['POST'])
def addNewNode():
    try:
        data = request.get_json()
        masterAddress = data["Master"]
        nodeAddress = data["MyAddress"]
        #masterNodeList = requests.post(f'http://{masterAddress}/blockchain/internal/add/node', json = {"MyAddress":nodeAddress})
        # print(masterNodeList.text.split("|"))
        # blockchain.nodes = set(masterNodeList.text.split("|"))
        requests.post(f'http://{masterAddress}/blockchain/internal/add/node', json = {"MyAddress":nodeAddress})
        result, blockchainNetwork.blockchain = getBlockchainDataFromJson(requests.get(f'http://{masterAddress}/blockchain').json())
        return result, 201

    except Exception as e:
        #print(e)
        raise e
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


@app.route('/new/signedTransaction', methods=['POST'])
def addNewSignedTransaction():
    pass

@app.route('/new/transaction', methods=['POST'])
def addTransaction():
    data = request.get_json()
    try:
        valid, messageResponse = isDataValid(data)

        if valid:
            transaction = createTransaction(fromAddress=convertToPubKey(data["FromAddress"]), toAddress=convertToPubKey(data["ToAddress"]), amount=int(data["Amount"]), privateKey=convertToPrivKey(data["priv_key"]))

            result, message = blockchainNetwork.blockchain.addTransaction(transaction=transaction)

            if result:
                finalMessage = message + " " + getBalance(data["FromAddress"])[0]
                writeBlockchainToDb()
                propagateTransactionToAllNodes()
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

#@app.route('/blockchain/consensus', methods=['GET'])
def runConsensusAlgorithm():
    try:
        #data = request.get_json()
        for node in blockchainNetwork.blockchain.nodes:
            data = requests.get(f'http://{node}/blockchain').json()
            chainLength = data["LengthOfChain"]

            if chainLength > len(blockchainNetwork.blockchain.chain):
                #blockchain = getBlockchainDataFromJson()
                return "Consensus completed! Chain updated", 201

            return "Consensus completed! You have the longest chain", 200

    except KeyError as e:
        print(e)
        return "Invalid json returned from a node", 500
    except Exception:
        return "Could not complete consensus!", 500

def isDataValid(jsonStr):

    pubKey = jsonStr["FromAddress"]
    if pubKey.count(",") != 1:
        return False, "Invalid sender public key!"

    pubKey = jsonStr["ToAddress"]
    if pubKey.count(",") != 1:
        return False, "Invalid receiver public key!"

    privKey = jsonStr["priv_key"]
    if privKey.count(",") != 4:
        return False, "Invalid private key!"

    if not str.isdigit(jsonStr["Amount"]) or int(jsonStr["Amount"]) <= 0:
        return False, "Invalid amount"

    return True, "Valid"

def writeBlockchainToDb():
    blockchainNetwork.blockchainDb = shelve.open("blockchainDb")
    blockchainNetwork.blockchainDb['blockchain.chain'] = blockchainNetwork.blockchain.chain
    blockchainNetwork.blockchainDb['blockchain.nodes'] = blockchainNetwork.blockchain.nodes
    blockchainNetwork.blockchainDb['blockchain.pendingTransactions'] = blockchainNetwork.blockchain.pendingTransactions
    blockchainNetwork.blockchainDb.close()

def getBlockchainDataFromJson(jsonData):
    newBlockChain = Blockchain()

    def deconstructTransactionFromJson(transactionData):
        fromAddress = transactionData["FromAddress"][transactionData["FromAddress"].index("(")+1:transactionData["FromAddress"].index(")")]
        toAddress = transactionData["ToAddress"][transactionData["ToAddress"].index("(")+1:transactionData["ToAddress"].index(")")]
        transaction = createTransaction(fromAddress=convertToPubKey(fromAddress), toAddress=convertToPubKey(toAddress), amount=int(transactionData["Amount"]), signature=transactionData["Signature"], timestamp=transactionData["Timestamp"])
        return transaction

    try:
        newBlockChain.chain = []
        blocks = jsonData["Blocks"]
        for blockNum in blocks:
            blockData = blocks[blockNum]
            transactionsForBlock = []
            transactionData = blockData["Transactions"]

            for transactionData in transactionData:
                transactionsForBlock.append(deconstructTransactionFromJson(transactionData))
            newBlock = Block(transactions=transactionsForBlock, previousHash=blockData["PreviousHash"], miningDifficulty=newBlockChain.miningDifficulty, nonce=blockData["Nonce"], hashVal=blockData["MyHash"])
            newBlockChain.chain.append(newBlock)

        pendingTransactions = jsonData["PendingTransactions"]
        for transactionData in pendingTransactions:
            newBlockChain.pendingTransactions.add(deconstructTransactionFromJson(transactionData))

        newBlockChain.nodes = jsonData["Nodes"]
        print(newBlockChain)

        result, blockNum = newBlockChain.isChainValid()
        if result:
            return "Your node was updated!", newBlockChain
        else:
            print(f"Chain invalid! {blockNum}")

    except Exception as e:
        raise e

    return "Error fetching from Master!", Blockchain()

def createTransaction(fromAddress, toAddress, amount, timestamp=None, signature=None, privateKey=None):
    transaction = Transaction(fromAddress=fromAddress, toAddress=toAddress, amount=amount)
    if not signature:
        signature = rsa.sign(str(transaction).encode(encoding='utf_8'), privateKey, "SHA-256")
        transaction.addSignature(signature=signature.hex())
    else:
        if isinstance(signature, str):
            transaction.addSignature(signature=signature)
        elif isinstance(signature, bytes):
            transaction.addSignature(signature=signature.hex())
    if timestamp:
        if isinstance(timestamp, str):
            transaction.timestamp = float(timestamp)
        elif isinstance(timestamp, float):
            transaction.timestamp = timestamp

    return transaction

def propagateTransactionToAllNodes():
    # Post transaction to all nodes

            # try:


            # # r = requests.get(f'http://localhost:8000/blockchain/db').content
            # filename = open("temp.db", "wb")
            # filename.write(r)
            # filename.close()
            # # with open(filename, 'wb') as fd:
            # #     for chunk in r.iter_content(chunk_size=128):
            # #         fd.write(chunk)
            #
            # print(f"dir  {dir(r)}")
            #
            # tempDb = shelve.open("temp")
            # if 'blockchain' in blockchainDb:
            #     bb = tempDb['blockchain']
            # print(bb)
            #
            # except KeyError as e:
            #     print(e)
            #     return "Missing a field! Please check all required fields are present", 500
            # except Exception as e:
            #     print(e)
            #     return "Invalid", 500
    pass
