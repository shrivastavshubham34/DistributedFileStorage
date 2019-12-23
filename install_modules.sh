#!/bin/bash

if ! [[ -x "$(command -v python3)" ]];
then
    echo "Error: python3 is not installed."
    exit 1
else
    echo -n "Found "
    python3 --version

    if ! [[ -x "$(command -v pip3)" ]];
    then
        echo "Error: pip3 is not installed."
        echo "Installing pip3..."
        curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        python3 get-pip.py
    fi

    echo "Installing gRPC"
    pip3 install grpcio-tools --user

    echo "Installing pyyaml"
    pip3 install pyyaml --user

    echo "Installing psutil"
    pip3 install psutil --user

    echo "Installing sortedcontainers"
    pip3 install sortedcontainers --user

    echo "Installing numpy"
    pip3 install numpy --user

    exit 0
fi

if ! [[ -x "$(command -v python)" ]];
then
    echo "Error: python is not installed."
    exit 1
else
    echo -n "Found "
    python --version

    if ! [[ -x "$(command -v pip3)" ]];
    then
        echo "Error: pip is not installed."
        echo "Installing pip..."
        curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        python get-pip.py
    fi

    echo "Installing gRPC"
    pip install grpcio-tools --user

    echo "Installing pyyaml"
    pip install pyyaml --user

    echo "Installing psutil"
    pip install psutil --user

    echo "Installing sortedcontainers"
    pip install sortedcontainers --user

    echo "Installing numpy"
    pip install numpy --user

    exit 0
fi



