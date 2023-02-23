#!/bin/sh
sudo python3 -m pip install -r requirements.txt
sudo cp .env.example .env
echo -e "\n\n\n"
echo Enter influx write token:
read token
printf '\nINFLUX_TOKEN="$token"' >> .env
(sudo crontab -l 2>/dev/null; echo "* * * * * /usr/bin/python3 $pwd/py_ipmi_influx.py") | crontab -

echo -e "\nInstallation complete. Please edit .env file to change server details if needed.\n"