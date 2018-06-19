## A POC (proof of concept) of cryptocurrency using blockchains

This is a fully working prototype for a crypto-currency using the basic blockchain mechanisms, which include:

- Signed transactions
- Consensus algorithm within a multi-node architecture

## Installation

Clone the repo, and then run `install.sh`. It will start the Blockchain REST app on your local machine, and it will start on `localhost:8001`.

### Making it public

Once that is done, you can run the `public.sh` on another terminal window, which exposes your `localhost:8001` port to the outside world, and you can talk to the main blockchain node and be a part of the consensus!

**NOTE:** If you face any issues with the above script, please refer to the [detailed]() readme, which has manual instructions for you to follow to install the app.

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
