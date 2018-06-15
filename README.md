This is a fully working prototype for a crypto-currency using the basic blockchain mechanisms, which include:

- Signed transactions
- Consensus algorithm within a multi-node architecture

## Installation

- First make sure you you have [Python3](https://www.python.org/downloads/) installed. Confirm if you can see this message when you execute:

	```
	$ python --version
	Python 3.6.4
	```
- Create a virtual Python environment called `myenv`. It is used to create an isolated Python environments so that the system's python installation is not affected in any way. Read more about `virtualenv` [here](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

	```
	$ virtualenv -p `which python3` myenv
	$ cd myenv
	$ source bin/activate
	```
	This should print something like this:

	```
	$ source bin/activate
	(myenv) ___________________________________________________________________
	
	```
	This confirms that your virtual env is now active.
	
- Install the `pgBlockchain` app using this command

	```
	$ pip install --extra-index-url https://test.pypi.org/simple/ pgBlockchain
	```
	
- Create a `python` file in your current directory

	```
	$ touch main.py
	```
	
	And copy these 2 lines in it
	
	```
	from pgBlockchain import network

	app = network.createApp()
	```

- Export this file to the flask app using this command:

	```
	$ export FLASK_APP=main.py
	```
	
- That's it! Now to start the application, just type `flask run -p <port_num>` where the port number is the port you want to run your blockchain on your local machine. 

	**Example**:
	
	```
	$ flask run -p 8001
	```
	
	You should see something like this
	
	```
	Running on http://127.0.0.1:8001/ (Press CTRL+C to quit)
	```
	
	And there you have it! Your blockchain app is now running!

## REST API documentation

You can find the documentation for the different REST endpoints [here](https://documenter.getpostman.com/view/2104227/RWEdt1Cb).

If you already have `Postman`, you can directly import the whole collection from the above link to your `Postman ` app. 
