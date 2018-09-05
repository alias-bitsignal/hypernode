"""
Checks the wallet, config, and tells if an hn instance is running.

"""

import argparse
import json
import subprocess
import sys
from os import path
from warnings import filterwarnings
from warnings import resetwarnings

from ipwhois import IPWhois

# custom modules
sys.path.append('../modules')
import config
import os
import poshn
import poscrypto
import psutil
import resource


__version__ = '0.0.3'


def check_os(status):
    """
    Dup from hn_client. FR: factorize
    """
    if os.name == "posix":
        process = psutil.Process()
        limit = resource.getrlimit(resource.RLIMIT_NOFILE)
        status["flimit"] = limit
        if limit[0] < 1024:
            status['errors'].append("Too small ulimit, please tune your system.")
            sys.exit()
        if limit[1] < 65000:
            status['errors'].append("ulimit shows non optimum value, consider tuning your system.")
    else:
        status["flimit"] = 'N/A'
        status['errors'].append("Non Posix system, requirements are not satisfied. Use at your own risks.")


def get_ip_provider(ip:str):
    """
    Returns thhe descriptino of the network provider for the public ip.
    Dupped code from plugin

    :param ip: str
    :return: str
    """
    filterwarnings(action="ignore")
    obj = IPWhois(ip)
    res = obj.lookup_whois()
    desc = res.get('asn_description')
    resetwarnings()
    return desc


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Bismuth HyperNode Check')
    parser.add_argument("-v", "--verbose", action="count", default=False, help='Be verbose.')
    parser.add_argument("-j", "--json", action="count", default=False, help='Return json content')
    parser.add_argument("-N", "--interface", type=str, default="", help='Use a specific network interface')
    # parser.add_argument("--action", type=str, default=None, help='Specific action. ')
    args = parser.parse_args()
    wallet_name = "poswallet.json"
    poscrypto.load_keys(wallet_name)
    status = {"address": poscrypto.ADDRESS, "errors": []}
    status['hn_lib_version'] = poshn.__version__
    status['config'] = config.load()
    check_os(status)
    # check if db exists
    if not path.isfile(config.POW_LEDGER_DB):
        status['errors'].append("Bismuth Full ledger not found at {}".format(config.POW_LEDGER_DB))
    # check if process runs
    instances = [p.info for p in psutil.process_iter(attrs=['pid', 'name', 'exe', 'cmdline']) if 'python' in p.info['name'] and 'hn_instance.py' in p.info['cmdline']]
    nb_instances = len(instances)
    python = instances[0]['exe'] if nb_instances else 'N/A'
    status['running_instances'] = nb_instances
    status['python'] = python
    status['python_version'] = subprocess.getoutput('{} --version'.format(config.PYTHON_EXECUTABLE))
    status['pwd'] = subprocess.getoutput("pwd")
    if args.interface:
        status['external_ip'] = subprocess.getoutput("curl --interface {} -4 -s ifconfig.co".format(args.interface))
        status['interface'] = args.interface
    else:
        status['external_ip'] = subprocess.getoutput("curl -4 -s ifconfig.co")
        status['interface'] = ''
    status['provider'] = get_ip_provider(status['external_ip'])
    status['default_port'] = config.DEFAULT_PORT
    with open("check.json", 'w') as f:
        json.dump(status, f)
    if args.json:
        print(json.dumps(status))
    else:
        if args.verbose:
            for var in ['address', 'hn_lib_version', 'default_port', 'external_ip', 'running_instances', 'python',
                        'python_version', 'interface', 'pwd', 'flimit']:
                print(var, ':', json.dumps(status[var]))
            print("\n== Config ==\n")
            for var, value in status['config'].items():
                print(var, ':', json.dumps(value))
        else:
            for var in ['address', 'default_port', 'external_ip', 'running_instances', 'python_version', 'pwd']:
                print(var, ':', json.dumps(status[var]))
            for var in ['POW_LEDGER_DB']:
                print(var, ':', json.dumps(status['config'][var]))
        if len(status['errors']):
            print("\n!! There are error(s) !!\n")
            for value in status['errors']:
                print("Error:", value)
