import rsa

def convertToPubKey(pubKeyStr):
    n, e = [int(key.strip()) for key in pubKeyStr.split(",")]
    return rsa.PublicKey(n=n, e=e)

def convertToPrivKey(privKeyStr):
    n, e, d, p, q = [int(key.strip()) for key in privKeyStr.split(",")]
    return rsa.PrivateKey(n=n, e=e, d=d, p=p, q=q)
