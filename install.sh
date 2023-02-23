#!/bin/sh
sudo python3 -m pip install -r requirements.txt
sudo cp .env.example .env
script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo -e "\n\n\n"
echo Enter influx write token:
read token
printf '\nINFLUX_TOKEN="$token"' >> .env
(sudo crontab -l 2>/dev/null; echo "* * * * * /usr/bin/python3 $script_dir/py_ipmi_influx.py") | crontab -

echo -e "\nInstallation complete. Please edit .env file to change server details if needed.\n"