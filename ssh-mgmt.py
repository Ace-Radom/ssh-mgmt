import argparse
import ipaddress
import json
import os
import subprocess
import sys

from datetime import datetime, timezone

base_dir = os.path.split(os.path.realpath(__file__))[0]
data_dir = os.path.join(os.environ['USERPROFILE'], ".ssh-mgmt")
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
if not os.path.isdir(data_dir):
    raise Exception("Data folder path is occupied by a non-folder file")

server_data = {}

parser = argparse.ArgumentParser()

def is_legal_ipv4_addr(ipaddr: str) -> bool:
    try:
        ipaddress.IPv4Address(ipaddr)
    except:
        return False
    return True

def read_server_data() -> dict:
    data_file = os.path.join(data_dir, "server_data.json")
    if not os.path.exists(data_file):
        with open(data_file, 'w', encoding='utf-8') as wfile:
            wfile.write(json.dumps({}, ensure_ascii=False, indent=4))
        return {}
    
    with open(data_file, 'r', encoding='utf-8') as rfile:
        data = json.load(rfile)

    REQUIRED_KEYS = {"ip", "username", "add_time"}

    if not isinstance(data, dict):
        raise Exception("Data is not a dict")
    
    for hostname, items in data.items():
        if not isinstance(items, dict):
            raise Exception(f"Node `{hostname}` is not a dict")
        
        keys = set(items.keys())
        if keys != REQUIRED_KEYS:
            raise Exception(f"Illegal dict on node `{hostname}`")
        
        ipaddr = items["ip"]
        if not is_legal_ipv4_addr(ipaddr):
            raise Exception(f"Illegal IPv4 address on node `{hostname}`: `{ipaddr}`")
        
        username = items["username"]
        if not isinstance(username, str) or not username:
            raise Exception(f"Illegal username on node `{hostname}`: `{username}`")
        
        add_time = items["add_time"]
        if not isinstance(add_time, int):
            raise Exception(f"Illegal add_time on node `{hostname}`: `{add_time}`")

    return data

def save_server_data() -> None:
    data_file = os.path.join(data_dir, "server_data.json")
    with open(data_file, 'w', encoding='utf-8') as wfile:
        json.dump(server_data, wfile, ensure_ascii=False, indent=4)
    return

def add_server(ipaddr: str, username: str, hostname: str) -> bool:
    if not is_legal_ipv4_addr(ipaddr):
        print(f"Error: illegal IPv4 address is given: `{ipaddr}`")
        return False
    elif has_server(hostname):
        print(f"Error: server `{hostname}` already exists")
        return False
    
    server_data[hostname] = {
        "ip": ipaddr,
        "username": username,
        "add_time": int(datetime.now(timezone.utc).timestamp())
    }

    return True

def has_server(hostname: str) -> bool:
    if hostname in server_data:
        return True
    return False

def setup_args() -> None:
    features_arg_group = parser.add_mutually_exclusive_group()
    features_arg_group.add_argument("--add", nargs=3, metavar=("IP", "USERNAME", "HOSTNAME"), type=str, help="Add new remote server")
    features_arg_group.add_argument("--list", default=False, action="store_true", help="List all remote servers")
    features_arg_group.add_argument("--login", metavar="HOSTNAME", type=str, help="Call ssh to log in to the given remote server")
    features_arg_group.add_argument("--ping", metavar="HOSTNAME", type=str, help="Ping the given remote server")
    features_arg_group.add_argument("--remove", metavar="HOSTNAME", type=str, help="Remove the given remote server")

def main() -> None:
    global server_data

    setup_args()
    args = parser.parse_args()

    server_data = read_server_data()
    ret = True
    
    if args.add:
        ipaddr = args.add[0]
        username = args.add[1]
        hostname = args.add[2]        
        ret = add_server(ipaddr, username, hostname)

    save_server_data()

    if not ret:
        exit(1)
    exit(0)

if __name__ == "__main__":
    main()
