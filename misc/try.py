
# coding: utf-8

# In[1]:

import shelve
import rsa
from core import Blockchain, Transaction


# ### First step, let's create the blockchain object

# In[2]:

def convertToPubKey(pub_key_str):
    pubKeyStr = pub_key_str[pub_key_str.index("(")+1:pub_key_str.index(")")]
    n, e = [int(key.strip()) for key in pubKeyStr.split(",")]
    return rsa.PublicKey(n=n, e=e)

def convertToPrivKey(priv_key_str):
    privKeyStr = priv_key_str[priv_key_str.index("(")+1:priv_key_str.index(")")]
    n, e, d, p, q = [int(key.strip()) for key in privKeyStr.split(",")]
    return rsa.PrivateKey(n=n, e=e, d=d, p=p, q=q)

blockchainDb = shelve.open("blockchainDb")

if 'blockchain' in blockchainDb:
    myBlockchain = blockchainDb['blockchain']
else:
    myBlockchain = Blockchain()


# ### Next, let's add a few transactions to the blockchain

# In[3]:

#print(myBlockchain)
[pub_arya, priv_arya]=rsa.newkeys(512)
[pub_bran, priv_bran]=rsa.newkeys(512)
[pub_cersei, priv_cersei]=rsa.newkeys(512)
[pub_davos, priv_davos]=rsa.newkeys(512)
[pub_elia, priv_elia]=rsa.newkeys(512)

nameMap = {"arya":pub_arya, "bran":pub_bran, "cersei":pub_cersei, "davos":pub_davos, "elia":pub_elia}

# myBlockchain.mineBlock(pub_arya)
#
# transaction = Transaction(fromAddress=convertToPubKey(str(pub_arya)), toAddress=convertToPubKey(str(pub_bran)), amount=30)
# signature = rsa.sign(str(transaction).encode(encoding='utf_8'), convertToPrivKey(str(priv_arya)), "SHA-256")
# transaction.addSignature(signature=signature)
# result, message = myBlockchain.addTransaction(transaction=transaction)
#
# print(message)
#
# transaction = Transaction(fromAddress=convertToPubKey(str(pub_arya)), toAddress=convertToPubKey(str(pub_bran)), amount=10)
# signature = rsa.sign(str(transaction).encode(encoding='utf_8'), convertToPrivKey(str(priv_arya)), "SHA-256")
# transaction.addSignature(signature=signature)
# result, message = myBlockchain.addTransaction(transaction=transaction)
#
# print(message)
#
# result, message = myBlockchain.addTransaction(transaction=transaction)
#
# print(message)
#
# myBlockchain.mineBlock(pub_davos)
# myBlockchain.mineBlock(pub_elia)

print(myBlockchain)

for name in nameMap:
    print(f"\nBalance for name {name} : {nameMap.get(name)} is {myBlockchain.getBalance(user=nameMap.get(name))}")


#same timestamp, same transaction
# myBlockchain.addTransaction(transaction=transaction)
# myBlockchain.addTransaction(transaction=transaction)
#
# #same timestamp, same transaction
# transactions = list(myBlockchain.chain[1].transactions)
# transaction = transactions[0]
# transactions.append(transaction)
# transactions.append(transaction)
# transactions.append(transaction)
#myBlockchain.chain[1].hashVal = myBlockchain.chain[1].calculateHash()


#^^ this works, no way of preventing adding multiple transactions with exact same values. (probably unique timestamp should take care, but then the same transaction can be added to different blocks, specially the last block)
#   - Unique timestamp transactions only for a block(set implementation)

# can block hashing propagation work? change block 1, recalculate hash, save it, update b2.prev hash = hash1, recalculate hash of block 2, etc etc? -> will break with POW

# issue where in validating chain, final balance is checked to see if transaction1 was valid. It might result in incorrect result since at that moment in the chain, the transaction might be valid
    # Solution might be to create a temp chain, and check if the transaction1 was valid at that time.

# myBlockchain.mineBlock(pub_bran)
#
# transaction = Transaction(fromAddress=pub_bran, toAddress=pub_davos, amount=5)
# signature = rsa.sign(str(transaction).encode(encoding='utf_8'), priv_bran, "SHA-256")
# transaction.addSignature(signature=signature)
# myBlockchain.addTransaction(transaction=transaction)
#
# myBlockchain.mineBlock(pub_cersei)
#
# transaction = Transaction(fromAddress=pub_cersei, toAddress=pub_arya, amount=40)
# signature = rsa.sign(str(transaction).encode(encoding='utf_8'), priv_cersei, "SHA-256")
# transaction.addSignature(signature=signature)
# myBlockchain.addTransaction(transaction=transaction)

# transaction = Transaction(fromAddress=pub_bran, toAddress=pub_elia, amount=25)
# signature = rsa.sign(str(transaction).encode(encoding='utf_8'), priv_bran, "SHA-256")
# transaction.addSignature(signature=signature)
# myBlockchain.addTransaction(transaction=transaction)

# myBlockchain.chain[1].transactions[0].amount=230
# myBlockchain.chain[1].hashVal = myBlockchain.chain[2].calculateHash()






#signature = rsa.sign(encMessage, priv, "SHA-256")
# encMessage=str(t).encode(encoding='utf_8')
# print(encMessage)
#
#
# signature = rsa.sign(encMessage, priv, "SHA-256")
# print(rsa.verify(str(t).encode(encoding='utf_8'), signature, pub))
# myBlockchain.addTransaction(t, signature=signature)
# myBlockchain.mineBlock("Brian")
# print(myBlockchain)
# print(myBlockchain.getBalance(user='Andrew'))
# print(myBlockchain.getBalance(user='Brian'))
# myBlockchain.addTransaction(Transaction(fromAddress="Brian", toAddress="Andrew", amount=50))
# myBlockchain.addTransaction(Transaction(fromAddress="Chris", toAddress="Don", amount=200))
# myBlockchain.addTransaction(Transaction(fromAddress="Don", toAddress="Andrew", amount=50))
#
#
# # ### As soon as we mine for a block, all the above transactions are saved onto the new block mined.
#
# # In[4]:
#
#
# myBlockchain.mineBlock()
#
#
# # In[5]:
#
#
# myBlockchain.addTransaction(Transaction(fromAddress="Eli", toAddress="Fisher", amount=50))
# myBlockchain.addTransaction(Transaction(fromAddress="Fisher", toAddress="Brian", amount=400))
#
#
# # ### Mined another block, which adds the above 2 transactions to it
#
# # In[6]:
#
#
# myBlockchain.mineBlock()
#
#
# # ### Let's print out the whole blockchain as of this moment, with each block and transaction.
#
# # In[7]:
#
#
# print(myBlockchain)
#
#
# # ### Checks whether the blockchain is valid, it is for now since we have not made any changes to it.
#
# # In[8]:
#
#
# print(myBlockchain.isChainValid())
#
#
# # ### We can check for Brian's balance, which is correct if you look at all transactions involving Brian
# #
# # ```
# # Transaction(fromAddress="Andrew", toAddress="Brian", amount=100)
# # Transaction(fromAddress="Brian", toAddress="Andrew", amount=50)
# # Transaction(fromAddress="Fisher", toAddress="Brian", amount=400)
# # ```
# #
# # *Brian's a rich guy!*
#
# # In[9]:
#
#
# print(f"Brian's balance is {myBlockchain.getBalance(user='Brian')}")
#
#
# # ### But here comes Dr. Nefario...
#
# # ### He changes the transaction involving Brian for an amount greater than the original, and being as smart as he is, he re-calculates the hash to trick the blockchain.
#
# # In[10]:
#
#
# myBlockchain.chain[1].transactions[0] = Transaction("Andrew", "Brian", 500)
# myBlockchain.chain[1].hashVal = myBlockchain.chain[1].calculateHash()
# print(f"hashval for block 1 is now {myBlockchain.chain[1].hashVal}")
# print(myBlockchain.chain[1].transactions[0])
#
#
# # ### But alas! The validation code sniffs out the discrepancy and marks the blockchain invalid!
#
# # In[11]:
#
#
# print(myBlockchain.isChainValid())
