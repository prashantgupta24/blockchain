# !/bin/bash
MY_ENV="myenv"

echo "####################################################"
  echo " Setting up environment for blockchain application
        (only works with Mac for now)"
echo "####################################################"
echo ""
echo "Checking prerequisites ..."
echo ""
echo "Checking if python is installed ..."
if command -v python3 &>/dev/null; then
    echo Python 3 is installed
else
    echo Python 3 is not installed. Installing Python 3...
    brew install python
fi
echo "####################################################"
echo "Installing virtualenv ..."
echo ""
python3 -m pip install virtualenv
echo "####################################################"
echo "Activating virtualenv ..."
echo ""
virtualenv -p `which python3` $MY_ENV
source $MY_ENV/bin/activate
echo "####################################################"
echo "Python version ..."
python --version
echo "####################################################"
echo "Installing blockchain application ..."
echo ""
pip install --extra-index-url https://test.pypi.org/simple/ pgBlockchain
echo "####################################################"
pip list
echo "####################################################"
cat >> main.py <<EOL
from pgBlockchain import network
app = network.createApp()
EOL
echo "Starting application ..."
echo ""
export FLASK_APP=main.py
flask run -p 8001
