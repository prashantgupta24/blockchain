# from dotenv import load_dotenv
# load_dotenv()
import json
import rsa
from flask import Flask, request
from core import Blockchain, Transaction

app = Flask(__name__)

blockchain = Blockchain()

@app.route('/blockchain', methods=['GET'])
def getBlockchain():
    return str(blockchain), 200


@app.route('/balance/<pubKeyStr>', methods=['GET'])
def getBalance(pubKeyStr):
    return "Coins left: " + str(blockchain.getBalance(user=convertToPubKey(pubKeyStr))), 200

@app.route('/new/keys', methods=['GET'])
def getKeys():
    keyMap = {}
    [pub_key, priv_key]=rsa.newkeys(512)
    pub_key_str = str(pub_key)
    priv_key_str = str(priv_key)
    keyMap["publicKey"] = pub_key_str[pub_key_str.index("(")+1:pub_key_str.index(")")]
    keyMap["privateKey"] = priv_key_str[priv_key_str.index("(")+1:priv_key_str.index(")")]
    return json.dumps(keyMap, indent=2), 201

@app.route('/mine/<pubKeyStr>', methods=['GET'])
def mineBlock(pubKeyStr):
    blockchain.mineBlock(user=convertToPubKey(pubKeyStr))
    #return redirect(url_for('getBlockchain'))
    return "Block mined!", 201

@app.route('/new/transaction', methods=['POST'])
def addTransaction():
    data = request.get_json()
    result, messageResponse = isDataValid(data)
    if result:
        try:
            transaction = Transaction(fromAddress=convertToPubKey(data["fromAddress"]), toAddress=convertToPubKey(data["toAddress"]), amount=int(data["amount"]))
            signature = rsa.sign(str(transaction).encode(encoding='utf_8'), convertToPrivKey(data["priv_key"]), "SHA-256")
            transaction.addSignature(signature=signature)
            result, message = blockchain.addTransaction(transaction=transaction)

            if result:
                finalMessage = message + " " + getBalance(data["fromAddress"])[0]
                return finalMessage, 201

            return message, 400

        except ValueError as e:
            print(e)
            return "Invalid json!", 500
        except OverflowError as e:
            print(e)
            return "Invalid key! Please check both public and private keys", 500
    else:
        return messageResponse, 500

def convertToPubKey(pubKeyStr):
    n, e = [int(key.strip()) for key in pubKeyStr.split(",")]
    return rsa.PublicKey(n=n, e=e)

def convertToPrivKey(privKeyStr):
    n, e, d, p, q = [int(key.strip()) for key in privKeyStr.split(",")]
    return rsa.PrivateKey(n=n, e=e, d=d, p=p, q=q)

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
