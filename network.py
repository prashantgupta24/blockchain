import shelve
import json
import rsa
import requests
from flask import Flask, request, send_file
from core import Blockchain, Transaction, convertToPubKey, convertToPrivKey

app = Flask(__name__)

blockchainDb = shelve.open("blockchainDb")

blockchain = Blockchain()

if 'blockchain.chain' in blockchainDb:
    try:
        blockchain.chain = blockchainDb['blockchain.chain']
        blockchain.nodes = blockchainDb['blockchain.nodes']
        blockchain.pendingTransactions = blockchainDb['blockchain.pendingTransactions']
    except Exception:
        pass

@app.route('/blockchain', methods=['GET'])
def getBlockchain():
    return str(blockchain), 200

@app.route('/blockchain/db')
def blockchainDBFile():
    try:
        return send_file('blockchainDb.db')
    except Exception as e:
        return str(e)

@app.route('/balance/<pubKeyStr>', methods=['GET'])
def getBalance(pubKeyStr):
    return "Coins left: " + str(blockchain.getBalance(user=convertToPubKey(pubKeyStr))), 200

@app.route('/mine/<pubKeyStr>', methods=['GET'])
def mineBlock(pubKeyStr):
    blockchain.mineBlock(user=convertToPubKey(pubKeyStr))
    writeBlockchainToDb()
    return "Block mined!", 201

@app.route('/blockchain/add/node', methods=['POST'])
def addNodeToBlockchain():
    data = request.get_json()
    nodeAddress = data["MyAddress"]
    blockchain.nodes.add(nodeAddress)
    return "|".join(blockchain.nodes), 200

@app.route('/blockchain/new/node', methods=['POST'])
def addNewNode():
    # nodes = data["nodes"]
    # for node in nodes:
    #     print(node)
    try:

        # print(request.remote_addr)
        # print(request.host)
        data = request.get_json()
        masterAddress = data["Master"]
        nodeAddress = data["MyAddress"]
        masterNodeList = requests.post(f'http://{masterAddress}/blockchain/add/node', json = {"MyAddress":nodeAddress})
        print(masterNodeList.text.split("|"))
        # for node in masterNodeList.text:
        #     print(node)
        #     blockchain.nodes.add(node)
        blockchain.nodes = set(masterNodeList.text.split("|"))

        return "Nodes were updated!", 201

    except Exception as e:
        print(e)
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

@app.route('/new/transaction', methods=['POST'])
def addTransaction():
    data = request.get_json()
    try:
        valid, messageResponse = isDataValid(data)

        if valid:
            transaction = Transaction(fromAddress=convertToPubKey(data["FromAddress"]), toAddress=convertToPubKey(data["ToAddress"]), amount=int(data["Amount"]))
            signature = rsa.sign(str(transaction).encode(encoding='utf_8'), convertToPrivKey(data["priv_key"]), "SHA-256")
            transaction.addSignature(signature=signature.hex())
            result, message = blockchain.addTransaction(transaction=transaction)

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

@app.route('/blockchain/consensus', methods=['GET'])
def runConsensusAlgorithm():
    try:

        for node in blockchain.nodes:
            data = requests.get(f'http://{node}/blockchain').json()
            chainLength = data["LengthOfChain"]

            if chainLength > len(blockchain.chain):
                #blockchain.chain =
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
    blockchainDb = shelve.open("blockchainDb")
    blockchainDb['blockchain.chain'] = blockchain.chain
    blockchainDb['blockchain.nodes'] = blockchain.nodes
    blockchainDb['blockchain.pendingTransactions'] = blockchain.pendingTransactions
    blockchainDb.close()

def propagateTransactionToAllNodes():

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
