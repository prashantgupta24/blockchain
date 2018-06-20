## A POC (proof of concept) of cryptocurrency using blockchains implemented using REST

This is a fully working prototype for a crypto-currency using the basic blockchain mechanisms, which include:

- Signed transactions
- Consensus algorithm within a multi-node architecture
- Authenticity checks at every level, so that malicious changes are caught

## Example blockchain

This is how the blockchain looks like after mining a few blocks:

```
{
  "LengthOfChain": 3,
  "Nodes": [],
  "Blocks": {
    "Block 0": {
      "Transactions": [],
      "PreviousHash": 0,
      "MyHash": "000008e692dc8d22eee877ca66cc0c9e3f03ad6eaca8b90dd28eba8dcc961533",
      "Nonce": 5825589
    },
    "Block 1": {
      "Transactions": [
        {
          "Timestamp": 1529393411.164873,
          "FromAddress": "PublicKey(7289290174783177859017599388737467880747005533966265778785676318148168280546133970438727920736726881577622565899914946214651583846486672174287802399726317, 65537)",
          "ToAddress": "PublicKey(9576807642881441086254282488765809802083570013226262763404999483407654844252379777521217015135551815412113377828748011551310107843549235729821817086202443, 65537)",
          "Amount": 50,
          "Signature": "456fa43528b4c1826a6e91b5fb0c0e95c905ae58a2663c74dcfe3545af50b0bda6bb8634347077b25aedf5552251e635b17e19b8dfb13f552919def3749fe69a"
        }
      ],
      "PreviousHash": "000008e692dc8d22eee877ca66cc0c9e3f03ad6eaca8b90dd28eba8dcc961533",
      "MyHash": "000000326406dac3c68b9c52d99c98bd5774d98d7300b5dfbeb939bce1e5dac5",
      "Nonce": 162861
    },
    "Block 2": {
      "Transactions": [
        {
          "Timestamp": 1529393424.405997,
          "FromAddress": "PublicKey(7289290174783177859017599388737467880747005533966265778785676318148168280546133970438727920736726881577622565899914946214651583846486672174287802399726317, 65537)",
          "ToAddress": "PublicKey(9576807642881441086254282488765809802083570013226262763404999483407654844252379777521217015135551815412113377828748011551310107843549235729821817086202443, 65537)",
          "Amount": 50,
          "Signature": "549c1220443cedeb5730ebf22c8f935a826641cb31b5b3e2fe943d32100c8abf8b104ff0888dc7688fb26b4eea3ebd67b8e2b0461835d913b783936776af28e6"
        }
      ],
      "PreviousHash": "000000326406dac3c68b9c52d99c98bd5774d98d7300b5dfbeb939bce1e5dac5",
      "MyHash": "0000046d6d11e55acd590e0ffc1337b0ef5c53b2a1a532893ebee95c31702911",
      "Nonce": 394663
    }
  },
  "PendingTransactions": [
    {
      "Timestamp": 1529393447.8317492,
      "FromAddress": "PublicKey(9576807642881441086254282488765809802083570013226262763404999483407654844252379777521217015135551815412113377828748011551310107843549235729821817086202443, 65537)",
      "ToAddress": "PublicKey(8024173072611768281890562796537338844054517977333742470675108124898894059558483400388226481532776898122217832360846126868846621161946108442297427698027337, 65537)",
      "Amount": 10,
      "Signature": "51ee7c04546506dc85e5d0f2a1d3f52ce2529e1e51bd43f609c49c74888bd259a2aa8f65f6b636fd43a67b1cea6e4a2d0f367b3f30bd382800a2f285e8945263"
    }
  ]
}
```


## Installation

Clone the repo, and then run `install.sh`. Once it is finished, run `flask run`. It will start the Blockchain REST app on your local machine on `localhost:8001`.

### Making it public

Once that is done, you can run the `public.sh` on another terminal window, which exposes your `localhost:8001` port to the outside world, and you can talk to the main blockchain node and be a part of the consensus!

**NOTE:** If you face any issues with the above script, please refer to the [detailed](https://github.com/prashantgupta24/blockchain/blob/master/detailed_Readme.md) readme, which has manual instructions for you to follow to install the app.

## REST API documentation

You can find the documentation for the different REST endpoints [here](https://documenter.getpostman.com/view/2104227/RWEdt1Cb).

If you already have `Postman`, you can directly import the whole collection from the above link to your `Postman ` app.

## Initial steps

Once you've gone through the REST documentation, I would like to outline the initial steps for configuring the blockchain:

1. Generate a public and private key pair (and keep it safe with you) `/new/keys`

2. Register your node with the master node in the blockchain. As mentioned in the REST documentation, you need to send the following payload to your endpoint `/new/node`

		{
			"Master":"<Master address>",
			"MyAddress":"<Your address>"
		}

	where the master address is the master node address, and your address is the address that you see when you run `public.sh`

3. Once that is done, you will get a copy of the entire blockchain that's in the network. Hopefully the rest of the REST endpoints should be intuitive enough. Feel free to mine!
