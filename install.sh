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
echo "Installing python libraries needed ..."
echo ""
python setup.py install
echo "####################################################"
pip list
echo "####################################################"
echo ""
echo "Done."
echo ""
echo "Please run the following commands to start the application ...
####################################################
source $MY_ENV/bin/activate
flask run
####################################################"
echo ""
echo "After that, please run the public.sh script in another terminal window to make the blockchain visible publicly"
