if [ -e ngrok ]
then
    echo "ngrok already installed. Running ..."
else
  curl https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-darwin-amd64.zip --output ngrok.zip
  unzip ngrok.zip
  rm ngrok.zip
fi

./ngrok http 8001
