import shelve
import json
import requests

from blockchainpg.core import Blockchain, Transaction, Block
from blockchainpg.blockchain_utils import convertToPubKey

def runConsensusAlgorithm(blockchainNetwork):
    try:
        isMyChainLongest = True
        longestChainLength = len(blockchainNetwork.blockchain.chain)
        longestChainData = ""
        finalMessage = "Consensus completed!"

        for node in blockchainNetwork.blockchain.nodes:
            try:
                data = requests.get(f'http://{node}/blockchain').json()
                chainLength = data["LengthOfChain"]

                if blockchainNetwork.debug:
                    print(f"Chainlength for {node} was {chainLength}")
                if chainLength > longestChainLength:
                    (result, newBlockChain) = getBlockchainDataFromJson(data)
                    if result:
                        longestChainLength = chainLength
                        longestChainData = newBlockChain
                        isMyChainLongest = False
            except Exception:
                if blockchainNetwork.debug:
                    print(f"Node {node} not reachable...")

        if not isMyChainLongest:
            allTransactions = set()
            for block in longestChainData.chain:
                for transaction in block.transactions:
                    allTransactions.add(transaction.signature)

            transactionsNotMined = set()
            for transaction in blockchainNetwork.blockchain.pendingTransactions:
                if transaction.signature not in allTransactions:
                    transactionsNotMined.add(transaction)

            if blockchainNetwork.debug:
                print(f"All transactions not mined are {[x for x in transactionsNotMined]}")
            blockchainNetwork.blockchain = longestChainData
            blockchainNetwork.blockchain.pendingTransactions = transactionsNotMined
            return True, finalMessage + " Chain updated"

        return True, finalMessage + " You have the longest chain"

    except KeyError as e:
        print(e)
        return False, "Invalid json returned from a node"
    except Exception:
        return False, "Could not complete consensus!"

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

def writeBlockchainToDb(blockchainNetwork):
    try:
        blockchainNetwork.blockchainDb = shelve.open("blockchainDb")
        blockchainNetwork.blockchainDb['blockchain.chain'] = blockchainNetwork.blockchain.chain
        blockchainNetwork.blockchainDb['blockchain.nodes'] = blockchainNetwork.blockchain.nodes
        blockchainNetwork.blockchainDb['blockchain.pendingTransactions'] = blockchainNetwork.blockchain.pendingTransactions
        if blockchainNetwork.debug:
            print("Writing blockchain to db complete!")
    except Exception as e:
        print(e)
    finally:
        blockchainNetwork.blockchainDb.close()

def deconstructTransactionFromJson(transactionData):
    fromAddress = transactionData["FromAddress"][transactionData["FromAddress"].index("(")+1:transactionData["FromAddress"].index(")")]
    toAddress = transactionData["ToAddress"][transactionData["ToAddress"].index("(")+1:transactionData["ToAddress"].index(")")]
    transaction = Transaction(fromAddress=convertToPubKey(fromAddress), toAddress=convertToPubKey(toAddress), amount=int(transactionData["Amount"]), signature=transactionData["Signature"], timestamp=transactionData["Timestamp"])
    return transaction

def getBlockchainDataFromJson(jsonData):

    newBlockChain = Blockchain()
    try:
        newBlockChain.nodes = set(jsonData["Nodes"])

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

        result, blockNum = newBlockChain.isChainValid()
        if not result:
            raise Exception("Invalid chain in master!")

        return (True, newBlockChain)

    except Exception as e:
        #raise e
        print(e)
        newBlockChain = Blockchain()
        newBlockChain.setupGenesisBlock()
        return (False, newBlockChain)

def propagateTransactionToAllNodes(blockchainNetwork, transaction):
    for node in blockchainNetwork.blockchain.nodes:
        try:
            requests.post(f'http://{node}/new/signedTransaction', json = json.loads(json.dumps(transaction.getData())))
        except Exception:
            if blockchainNetwork.debug:
                print(f"Node {node} not reachable...")
