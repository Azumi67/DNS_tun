#!/usr/bin/env python3
#Author: https://github.com/Azumi67

import os
import subprocess
import sys
import re
import readline
import io
import shlex

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding="utf-8", errors="replace")


GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
WHITE = '\033[97m'
RESET = '\033[0m'
CLEAR = 'clear' if os.name != 'nt' else 'cls'

SERVER_SERVICE = '/etc/systemd/system/iodine-server.service'
CLIENT_SERVICE = '/etc/systemd/system/iodine-client.service'
RESET_SCRIPT = '/usr/local/bin/iodine-reset.sh'
RESET_SERVICE = '/etc/systemd/system/iodine-reset.service'

FIELD_NAMES = {
    'password': 'Secret key',
    'tunnel_ip': 'Tunnel IP',
    'domain': 'Domain'
}


def run(cmd, sudo=False):
    if sudo and os.geteuid() != 0:
        cmd.insert(0, 'sudo')
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"{RED}Command failed: {' '.join(cmd)}{RESET}")
        return False

def logo():
    logo_path = "/etc/logo2.sh"
    try:
        subprocess.run(["bash", "-c", logo_path], check=True)
    except subprocess.CalledProcessError as e:
        return e

    return None

def root():
    if os.geteuid() != 0:
        print(f"{RED}Error: this script must be run as root!{RESET}")
        sys.exit(1)
        
def serviceFile(path, content):
    print(f"{YELLOW}Writing systemd service to {path}...{RESET}")
    with open(path, 'w') as f:
        f.write(content)


def reload_enable(name):
    print(f"{YELLOW}Reloading systemd daemon and enabling service..{RESET}")
    run(['systemctl', 'daemon-reload'], sudo=True)
    run(['systemctl', 'enable', name], sudo=True)
    run(['systemctl', 'start', name], sudo=True)


def pause():
    input(f"{YELLOW}Press Enter to return to main menu...{RESET}")


def install_server():
    os.system("clear")
    print("\033[92m ^ ^\033[0m")
    print("\033[92m(\033[91mO,O\033[92m)\033[0m")
    print("\033[92m(   ) \033[92mDNS Server \033[93mMenu\033[0m")
    print('\033[92m "-"\033[93m═══════════════════════════════════════════════════\033[0m')
    print("\033[93m╭───────────────────────────────────────╮\033[0m")
    print(f"{YELLOW}Installing iodine server...{RESET}")

    run(['apt', 'update'], sudo=True)
    run(['apt', 'install', 'iodine', '-y'], sudo=True)

    print(f"{YELLOW}Enabling IPv4 forwarding...{RESET}")
    run(['sysctl', '-w', 'net.ipv4.ip_forward=1'], sudo=True)
    with open('/etc/sysctl.conf', 'r+') as f:
        content = f.read()
        if 'net.ipv4.ip_forward=1' not in content:
            f.write('\nnet.ipv4.ip_forward=1\n')

    password = input(f"{YELLOW}Enter {GREEN}shared secret {WHITE}(password): {RESET}").strip()
    tunnel_ip = input(f"{CYAN}Enter {GREEN}Tunnel IP for server {WHITE}(e.g. 192.0.0.1): {RESET}").strip()
    domain = input(f"{CYAN}Enter {GREEN}Tunnel subdomain {WHITE}(e.g. tunnel.azumi.com): {RESET}").strip()
    mtu = input(f"{CYAN}Enter {GREEN}MTU size {WHITE}(press Enter for default 1130): {RESET}").strip() or "1130"
    device = input(f"{CYAN}Enter {GREEN}Interface name {WHITE}(e.g. dns0): {RESET}").strip() or "dns0"

    content = f"""
[Unit]
Description=Iodine DNS Tunnel Server
After=network.target

[Service]
ExecStart=/usr/sbin/iodined -c -f -P {password} -d {device} -m {mtu} {tunnel_ip} {domain}
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""
    serviceFile(SERVER_SERVICE, content)
    reload_enable('iodine-server.service')
    print(f"{GREEN}Iodine server installed and running!{RESET}")
    pause()

def install_client():
    os.system("clear")
    print("\033[92m ^ ^\033[0m")
    print("\033[92m(\033[91mO,O\033[92m)\033[0m")
    print("\033[92m(   ) \033[92mDNS Client \033[93mMenu\033[0m")
    print('\033[92m "-"\033[93m═══════════════════════════════════════════════════\033[0m')
    print("\033[93m╭───────────────────────────────────────╮\033[0m")
    print(f"{YELLOW}Installing iodine client ...{RESET}")

    run(['apt', 'update'], sudo=True)
    run(['apt', 'install', 'iodine', '-y'], sudo=True)

    password = input(f"{CYAN}Enter {GREEN}shared secret {WHITE}(password): {RESET}").strip()
    server_ip = input(f"{CYAN}Enter {GREEN}Server Public IP {WHITE}: {RESET}").strip()
    domain = input(f"{CYAN}Enter {GREEN}Tunnel domain {WHITE}(e.g. tunnel.azumi.com): {RESET}").strip()
    mtu = input(f"{CYAN}Enter {GREEN}Max fragment size (-M) {WHITE}(e.g. 100): {RESET}").strip() or "100"
    dns_type = input(f"{CYAN}Enter {GREEN}DNS query type (-T) {WHITE}(null / txt / generic): {RESET}").strip() or "txt"
    interval = input(f"{CYAN}Enter {GREEN}Keepalive interval (-I) in seconds {WHITE}(e.g. 30): {RESET}").strip() or "30"
    device = input(f"{CYAN}Enter {GREEN}Interface name (-d) {WHITE}(e.g. dns0): {RESET}").strip() or "dns0"

    content = f"""
[Unit]
Description=Iodine DNS Tunnel Client
After=network.target

[Service]
ExecStart=/usr/sbin/iodine -f -P {password} -T {dns_type} -M {mtu} -I {interval} -d {device} {server_ip} {domain}
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""

    serviceFile(CLIENT_SERVICE, content)
    reload_enable('iodine-client.service')
    print(f"{GREEN}Iodine client configured and running!{RESET}")
    pause()


def setup_reset_timer():
    os.system("clear")
    print("\033[92m ^ ^\033[0m")
    print("\033[92m(\033[91mO,O\033[92m)\033[0m")
    print("\033[92m(   ) \033[92mReset Timer \033[93mMenu\033[0m")
    print(
        '\033[92m "-"\033[93m═══════════════════════════════════════════════════\033[0m'
    )
    print("\033[93m╭───────────────────────────────────────╮\033[0m")
    print(f"{CYAN}Select reset timer:{RESET}")
    print(f"{GREEN}1.{RESET} Server")
    print(f"{YELLOW}2.{RESET} Client")
    print(f"{WHITE}3.{RESET} Back to menu")
    print("\033[93m╰───────────────────────────────────────╯\033[0m")
    sel = input(f"{CYAN}Select: {RESET}").strip()
    if sel == '1': srv = 'server'
    elif sel == '2': srv = 'client'
    else: return
    target = 'iodine-server.service' if srv == 'server' else 'iodine-client.service'

    if os.path.exists(RESET_SERVICE):
        print(f"{CYAN}Reset timer exists. Choose an action:{RESET}")
        print("\033[93m╭───────────────────────────────────────╮\033[0m")
        print(f"{GREEN}1.{RESET} Setup new Timer")
        print(f"{YELLOW}2.{RESET} Edit existing Timer")
        print(f"{WHITE}3.{RESET} Back to main menu{RESET}")
        print("\033[93m╰───────────────────────────────────────╯\033[0m")
        act = input(f"{CYAN}Select: {RESET}").strip()
        if act == '3': return
        if act not in ('1','2'):
            print(f"{RED}Invalid choice.{RESET}")
            pause()
            return

    print(f"{CYAN}Select interval unit:{RESET}")
    print("\033[93m╭───────────────────────────────────────╮\033[0m")
    print(f"{GREEN}1.{RESET} Seconds")
    print(f"{YELLOW}2.{RESET} Minutes")
    print(f"{WHITE}3.{RESET} Hours")
    print("\033[93m╰───────────────────────────────────────╯\033[0m")
    unit_sel = input(f"{CYAN}Select: {RESET}").strip()
    unit_map = {'1':'seconds','2':'minutes','3':'hours'}
    if unit_sel not in unit_map:
        print(f"{RED}Invalid choice.{RESET}")
        pause()
        return
    unit = unit_map[unit_sel]

    val = input(f"{CYAN}Enter reset interval value ({unit}): {RESET}").strip()
    try:
        iv = int(val)
    except ValueError:
        print(f"{RED}Invalid number.{RESET}")
        pause()
        return
    interval = iv * (1 if unit=='seconds' else 60 if unit=='minutes' else 3600)

    script = f"""#!/bin/bash
while true; do
    sleep {interval}
    systemctl restart {target}
done
"""
    print(f"{YELLOW}Writing reset script to {RESET_SCRIPT}...{RESET}")
    with open(RESET_SCRIPT, 'w') as f:
        f.write(script)
    os.chmod(RESET_SCRIPT, 0o755)

    service = f"""
[Unit]
Description=Iodine Service Reset Timer
After=network.target

[Service]
ExecStart={RESET_SCRIPT}
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""
    serviceFile(RESET_SERVICE, service)
    reload_enable('iodine-reset.service')
    print(f"{GREEN}Reset timer configured and running!{RESET}")
    pause()


def edit_config():
    os.system("clear")
    print(f"{GREEN} ^ ^\n(\033[91mO,O{GREEN})\n(   ) \033[92mEdit Tunnel \033[93mMenu{RESET}")
    print('\033[92m "-"\033[93m═══════════════════════════════════════════════════\033[0m')
    print("\033[93m╭───────────────────────────────────────╮\033[0m")
    print(f"{CYAN}Select config to edit:{RESET}")
    print(f"{GREEN}1.{RESET} Server")
    print(f"{YELLOW}2.{RESET} Client")
    print(f"{WHITE}3.{RESET} Back to menu")
    print("\033[93m╰───────────────────────────────────────╯\033[0m")

    sel = input(f"{CYAN}Select: {RESET}").strip()
    if sel == '1':
        which = 'server'
    elif sel == '2':
        which = 'client'
    else:
        return

    path = SERVER_SERVICE if which == 'server' else CLIENT_SERVICE
    if not os.path.exists(path):
        print(f"{RED}Service file not found at {path}.{RESET}")
        pause()
        return

    with open(path) as f:
        content = f.read()

    match = re.search(r'ExecStart=(.*)', content)
    if not match:
        print(f"{RED}Couldnt find ExecStart line.{RESET}")
        pause()
        return

    args = shlex.split(match.group(1))  
    fields = {}

    if which == 'server':
        try:
            fields['password'] = args[args.index('-P') + 1]
            fields['device'] = args[args.index('-d') + 1]
            fields['mtu'] = args[args.index('-m') + 1]
            fields['tunnel_ip'] = args[-2]
            fields['domain'] = args[-1]
        except (ValueError, IndexError):
            print(f"{RED}Couldnt parse server command properly.{RESET}")
            pause()
            return
    else:
        try:
            fields['password'] = args[args.index('-P') + 1]
            fields['dns_type'] = args[args.index('-T') + 1]
            fields['mtu'] = args[args.index('-M') + 1]
            fields['interval'] = args[args.index('-I') + 1] if '-I' in args else '30'
            fields['device'] = args[args.index('-d') + 1]
            fields['server_ip'] = args[-2]
            fields['domain'] = args[-1]
        except (ValueError, IndexError):
            print(f"{RED}Couldnt parse client command properly.{RESET}")
            pause()
            return

    while True:
        print(f"\n{CYAN}Editable stuff:{RESET}")
        keys = list(fields.keys())
        for i, key in enumerate(keys, 1):
            label = FIELD_NAMES.get(key, key.replace('_', ' ').capitalize())
            current = f"{YELLOW}{fields[key]}{RESET}"
            if key == 'dns_type':
                print(f"{i}. {label} {WHITE}(current: {current}) → Options: null, txt, generic{RESET}")
            elif key == 'mtu':
                print(f"{i}. {label} {WHITE}(current: {current}) → Example: 100, 128, 150{RESET}")
            elif key == 'interval':
                print(f"{i}. {label} {WHITE}(current: {current}) → Keepalive in seconds (e.g. 30){RESET}")
            else:
                print(f"{i}. {label} {WHITE}(current: {current}){RESET}")
        print(f"{len(keys)+1}. {GREEN}Save & Exit{RESET}")

        choice = input(f"{CYAN}Select: {RESET}").strip()
        if choice == str(len(keys)+1):
            break
        if not choice.isdigit() or not (1 <= int(choice) <= len(keys)):
            print(f"{RED}Invalid choice.{RESET}")
            continue
        key = keys[int(choice) - 1]
        label = FIELD_NAMES.get(key, key.replace('_', ' ').capitalize())
        new_val = input(f"{YELLOW}Enter new {label}: {RESET}").strip()
        if new_val:
            fields[key] = new_val

    if which == 'server':
        new_exec = f"/usr/sbin/iodined -c -f -P {fields['password']} -d {fields['device']} -m {fields['mtu']} {fields['tunnel_ip']} {fields['domain']}"
    else:
        new_exec = f"/usr/sbin/iodine -f -P {fields['password']} -T {fields['dns_type']} -M {fields['mtu']} -I {fields['interval']} -d {fields['device']} {fields['server_ip']} {fields['domain']}"

    new_content = re.sub(r'ExecStart=.*', f'ExecStart={new_exec}', content)
    serviceFile(path, new_content)

    run(['systemctl', 'daemon-reload'], sudo=True)
    svc_name = 'iodine-server.service' if which == 'server' else 'iodine-client.service'
    run(['systemctl', 'restart', svc_name], sudo=True)

    print(f"{GREEN}{svc_name} updated and restarted successfully!{RESET}")
    pause()

def show_status():
    os.system("clear")
    print("\033[92m ^ ^\033[0m")
    print("\033[92m(\033[91mO,O\033[92m)\033[0m")
    print("\033[92m(   ) \033[92mStatus \033[93mMenu\033[0m")
    print(
        '\033[92m "-"\033[93m═══════════════════════════════════════════════════\033[0m'
    )
    print(f"{YELLOW}Checking available services..{RESET}\n")
    services = []
    if os.path.exists(SERVER_SERVICE): services.append('iodine-server.service')
    if os.path.exists(CLIENT_SERVICE): services.append('iodine-client.service')
    if os.path.exists(RESET_SERVICE): services.append('iodine-reset.service')
    if not services:
        print(f"{RED}No services found to display status.{RESET}")
    else:
        for svc in services:
            print(f"{CYAN}--- {svc} ---{RESET}")
            subprocess.run(['systemctl', 'status', svc, '--no-pager'])
            print()
    pause()


def uninstall():
    while True:
        os.system(CLEAR)
        print(f"{YELLOW}┌───────── Uninstall Menu ─────────┐{RESET}")
        print(f"{WHITE}1.{GREEN} Remove Server{RESET}")
        print(f"{WHITE}2.{YELLOW} Remove Client{RESET}")
        print(f"{WHITE}3.{CYAN} Remove Reset Timer{RESET}")
        print(f"{WHITE}4.{GREEN} Remove All{RESET}")
        print(f"{WHITE}5.{RED} Back to Main Menu{RESET}")
        print(f"{YELLOW}└──────────────────────────────────┘{RESET}")
        choice = input(f"{CYAN}Select an option (1-5): {RESET}").strip()

        if choice == '5':
            break
        elif choice not in ['1', '2', '3', '4']:
            print(f"{RED}Invalid choice. Please select 1-5.{RESET}")
            continue

        targets = {
            '1': ['server'],
            '2': ['client'],
            '3': ['reset'],
            '4': ['server', 'client', 'reset']
        }.get(choice, [])

        confirm = input(f"{YELLOW}Are you sure you want to uninstall {', '.join(targets)}? (y/n): {RESET}").strip().lower()
        if confirm != 'y':
            print(f"{CYAN}Uninstall canceled.{RESET}")
            pause()
            continue

        for t in targets:
            if t in ('server', 'client'):
                svc = SERVER_SERVICE if t == 'server' else CLIENT_SERVICE
                name = 'iodine-server' if t == 'server' else 'iodine-client'
                if os.path.exists(svc):
                    print(f"{YELLOW}Stopping and disabling {name}...{RESET}")
                    os.system(f"systemctl stop {name} >/dev/null 2>&1")
                    os.system(f"systemctl disable {name} >/dev/null 2>&1")
                    os.remove(svc)
                else:
                    print(f"{CYAN}{name} service not installed, skipping...{RESET}")

            if t == 'reset':
                removed_any = False
                if os.path.exists(RESET_SERVICE):
                    print(f"{YELLOW}Stopping and disabling reset timer...{RESET}")
                    os.system("systemctl stop iodine-reset >/dev/null 2>&1")
                    os.system("systemctl disable iodine-reset >/dev/null 2>&1")
                    os.remove(RESET_SERVICE)
                    removed_any = True
                if os.path.exists(RESET_SCRIPT):
                    os.remove(RESET_SCRIPT)
                    removed_any = True
                if not removed_any:
                    print(f"{CYAN}Reset timer not installed, skipping...{RESET}")

        print(f"\n{GREEN}Uninstallation complete. Reloading daemon...{RESET}")
        os.system("systemctl daemon-reexec >/dev/null 2>&1")
        pause()
        break


def main():
    root()
    os.system("clear")
    logo()
    print("\033[92m ^ ^\033[0m")
    print("\033[92m(\033[91mO,O\033[92m)\033[0m")
    print("\033[92m(   ) \033[93mMain Menu\033[0m")
    print(
        '\033[92m "-"\033[93m═══════════════════════════════════════════════════\033[0m'
    )
    
    while True:
        print("\033[93m╭───────────────────────────────────────╮\033[0m")
        print(f"0.{WHITE} Status{RESET}")
        print(f"1.{YELLOW} Install & configure Server{RESET}")
        print(f"2.{GREEN} Install & configure Client{RESET}")
        print(f"3.{CYAN} Setup/reset timer{RESET}")
        print(f"4.{YELLOW} Edit Tunnel{RESET}")
        print(f"5.{RED} Uninstall{RESET}")
        print(f"q.{WHITE} Quit{RESET}")
        print("\033[93m╰───────────────────────────────────────╯\033[0m")
        choice = input("Choose an option (0-5, q): ").strip()

        if choice == '0': show_status()
        elif choice == '1': install_server()
        elif choice == '2': install_client()
        elif choice == '3': setup_reset_timer()
        elif choice == '4': edit_config()
        elif choice == '5': uninstall()
        elif choice.lower() == 'q': sys.exit(0)
        else:
            print(f"{RED}Wrong option. Choose a valid number from 0 to 5.{RESET}")

main()
