import shelve
import json
import rsa
import requests
from flask import Flask, request, send_file
from core import Blockchain, Transaction, convertToPubKey, convertToPrivKey

app = Flask(__name__)

blockchainDb = shelve.open("blockchainDb")

if 'blockchain' in blockchainDb:
    try:
        blockchain = blockchainDb['blockchain']
    except Exception:
        blockchain = Blockchain()
else:
    blockchain = Blockchain()

@app.route('/blockchain', methods=['GET'])
def getBlockchain():
    requestHost = str(request.host)
    if requestHost.find("localhost") == -1 and request.host not in blockchain.nodes:
        blockchain.nodes.add(request.host)
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
    blockchainDb['blockchain'] = blockchain
    return "Block mined!", 201

@app.route('/blockchain/new/node', methods=['POST'])
def addNewNode():
    try:
        # nodes = data["nodes"]
        # for node in nodes:
        #     print(node)
        #print(request.remote_addr)
        #print(request.host)

        # masterNode = data["Master"]
        # data = requests.get(f'http://{masterNode}/blockchain').json()
        # blockchain.nodes = data["nodes"]

        r = requests.get(f'http://localhost:8000/blockchain/db').content
        filename = open("temp.db", "wb")
        filename.write(r)
        filename.close()
        # with open(filename, 'wb') as fd:
        #     for chunk in r.iter_content(chunk_size=128):
        #         fd.write(chunk)

        print(f"dir  {dir(r)}")

        tempDb = shelve.open("temp")
        if 'blockchain' in blockchainDb:
            bb = tempDb['blockchain']
        print(bb)
    except KeyError as e:
        print(e)
        return "Missing a field! Please check all required fields are present", 500
    except Exception as e:
        raise e
        return "Invalid", 500

    return "Nodes were updated!", 201

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
            transaction.addSignature(signature=signature)
            result, message = blockchain.addTransaction(transaction=transaction)

            if result:
                finalMessage = message + " " + getBalance(data["fromAddress"])[0]
                blockchainDb['blockchain'] = blockchain
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
            else:
                return "Consensus completed! You have the longest chain", 200

    except KeyError as e:
        print(e)
        return "Invalid json returned from a node", 500
    except Exception:
        return "Could not complete consensus!", 500

def isDataValid(jsonStr):

    pubKey = jsonStr["fromAddress"]
    if pubKey.count(",") != 1:
        return False, "Invalid sender public key!"

    pubKey = jsonStr["toAddress"]
    if pubKey.count(",") != 1:
        return False, "Invalid receiver public key!"

    privKey = jsonStr["priv_key"]
    if privKey.count(",") != 4:
        return False, "Invalid private key!"

    if not str.isdigit(jsonStr["amount"]) or int(jsonStr["amount"]) <= 0:
        return False, "Invalid amount"

    return True, "Valid"
