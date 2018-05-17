
# coding: utf-8

# In[1]:

import rsa
from core import Blockchain, Transaction

# ### First step, let's create the blockchain object

# In[2]:


myBlockchain = Blockchain()


# ### Next, let's add a few transactions to the blockchain

# In[3]:

#print(myBlockchain)
[pub, priv]=rsa.newkeys(512)
myBlockchain.mineBlock(pub)
#print(myBlockchain.getBalance(user=str(pub)))
transaction = Transaction(fromAddress=pub, toAddress="Brian", amount=20)
signature = rsa.sign(str(transaction).encode(encoding='utf_8'), priv, "SHA-256")
transaction.addSignature(signature=signature)
myBlockchain.addTransaction(transaction=transaction)



myBlockchain.mineBlock("Brian")
myBlockchain.chain[2].transactions[0].amount=670
myBlockchain.chain[2].hashVal = myBlockchain.chain[2].calculateHash()
myBlockchain.mineBlock("Charles")
print(myBlockchain)
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
