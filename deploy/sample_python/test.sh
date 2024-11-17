#!/bin/bash

stdout=$(python3.8 -c 'import sys; print(sys.version)' 2>&1)
echo $stdout
if echo "$stdout" | grep -q "command not found"; then
    echo "ERROR: python 3.8 is not installed."
else
    if echo "$stdout" | grep -q "3.8"; then
        echo "\n\n=> python 3.8 installed successfully.\n\n"
        ./test-py38.sh
    fi
fi

stdout=$(python3.9 -c 'import sys; print(sys.version)' 2>&1)
if echo "$stdout" | grep -q "command not found"; then
    echo "ERROR: python 3.9 is not installed."
else
    if echo "$stdout" | grep -q "3.9"; then
        echo -e "\n\n=> python 3.9 installed successfully.\n\n"
        ./test-py39.sh
    fi
fi

#echo $stdout

