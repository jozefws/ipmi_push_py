#!/bin/sh
sudo python3 -m pip install -r requirements.txt
sudo cp .env.example .env
echo Enter influx write token:
read token
printf '\nINFLUX_TOKEN="$token"' >> .env
(sudo crontab -l 2>/dev/null; echo "* * * * * /usr/bin/python3 /home/roottsg/ipmi_push_py/py_ipmi_influx.py") | crontab -