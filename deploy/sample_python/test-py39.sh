#!/bin/bash
echo -e "##################################################################################\n\n"
stdout=$(python3.9 -c 'import sys; print(sys.version)' 2>&1)
echo -e "TEST: Python version\n" 
echo $stdout

echo -e "\n\n##################################################################################\n\n"
stdout=$(pip3 install -r ./audio_tag/requirements.txt 2>&1)
echo -e "TEST: Dependencies installation\n" 
echo $stdout

echo -e "\n\n##################################################################################\n\n"
stdout=$(python3.9 -m compileall ./audio_tag 2>&1)
echo -e "TEST: Application compilation\n" 
echo $stdout

echo -e "\n\n##################################################################################\n\n"
cd ./audio_tag
stdout=$(pytest 2>&1)
echo -e "TEST: pytest\n" 
echo $stdout

echo -e "\n\n##################################################################################\n\n"
cd ../notebooks
stdout=$(pytest --nbmake 2>&1)
echo -e "TEST: pytest with notebooks\n" 
echo $stdout

echo -e "\n\n##################################################################################\n\n"
cd ../audio_tag
stdout=$(pylint tagreader.py 2>&1)
echo -e "TEST: pylint\n" 
echo $stdout

echo -e "\n\n##################################################################################\n\n"
cd /application
stdout=$(python3.9 setup.py sdist; pip3 install . 2>&1)
echo -e "TEST: Wheel building\n" 
echo $stdout
