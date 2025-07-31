#!/bin/bash

RED="\033[91m"
GREEN="\033[92m"
YELLOW="\033[93m"
BLUE="\033[94m"
CYAN="\033[96m"
RESET="\033[0m"

apt update -y
apt install wget -y
echo -e "${GREEN}Downloading logo ...${RESET}"
wget -O /etc/logo2.sh https://github.com/Azumi67/UDP2RAW_FEC/raw/main/logo2.sh
chmod +x /etc/logo2.sh
if [ -f "dns.py" ]; then
    echo -e "${YELLOW}Removing existing dns.py ...${RESET}"
    rm dns.py
fi
echo -e "${YELLOW}Downloading dns.py...${RESET}"
wget https://github.com/Azumi67/DNS_tun/releases/download/V1.0/dns.py
echo -e "${GREEN}Launching dns.py...${RESET}"
python3 dns.py
