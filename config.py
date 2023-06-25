import json, requests, time
from termcolor import cprint
from datetime import date, datetime
import datetime as date_timestamp
import math
import random
import asyncio, aiohttp
import csv
from loguru import logger
from setting import *


outfile = ''
with open(f"{outfile}wallets.txt", "r") as f:
    WALLETS = [row.strip() for row in f]

with open(f"{outfile}data/arb_api.txt", "r") as f:
    ARB_API_KEYS = [row.strip() for row in f]

with open(f"{outfile}data/opt_api.txt", "r") as f:
    OPT_API_KEYS = [row.strip() for row in f]

with open(f"{outfile}data/avax_api.txt", "r") as f:
    AVAX_API_KEYS = [row.strip() for row in f]

with open(f"{outfile}data/bsc_api.txt", "r") as f:
    BSC_API_KEYS = [row.strip() for row in f]

with open(f"{outfile}data/eth_api.txt", "r") as f:
    ETH_API_KEYS = [row.strip() for row in f]

with open(f"{outfile}data/polygon_api.txt", "r") as f:
    POLYGON_API_KEYS = [row.strip() for row in f]

with open(f"{outfile}data/ftm_api.txt", "r") as f:
    FTM_API_KEYS = [row.strip() for row in f]

with open(f"{outfile}data/celo_api.txt", "r") as f:
    CELO_API_KEYS = [row.strip() for row in f]

with open(f"{outfile}data/gnosis_api.txt", "r") as f:
    GNOSIS_API_KEYS = [row.strip() for row in f]

api_keys = {
    'arbitrum'  : ARB_API_KEYS,
    'optimism'  : OPT_API_KEYS,
    'avalanche' : AVAX_API_KEYS,
    'bsc'       : BSC_API_KEYS,
    'polygon'   : POLYGON_API_KEYS,
    'fantom'    : FTM_API_KEYS,
    'ethereum'  : ETH_API_KEYS,
    'celo'      : CELO_API_KEYS,
    'gnosis'    : GNOSIS_API_KEYS,
}

# api urls
base_url = {
    'arbitrum'  : 'https://api.arbiscan.io',
    'optimism'  : 'https://api-optimistic.etherscan.io',
    'avalanche' : 'https://api.snowtrace.io',
    'bsc'       : 'https://api.bscscan.com',
    'polygon'   : 'https://api.polygonscan.com',
    'fantom'    : 'https://api.ftmscan.com',
    'ethereum'  : 'https://api.etherscan.io',
    'celo'      : 'https://api.celoscan.io',
    'gnosis'    : 'https://api.gnosisscan.io',
}

native_tokens = {
    'arbitrum'  : 'ETH',
    'optimism'  : 'ETH',
    'avalanche' : 'AVAX',
    'bsc'       : 'BNB',
    'polygon'   : 'MATIC',
    'fantom'    : 'FTM',
    'ethereum'  : 'ETH',
}


def call_json(result, outfile):
    with open(f"{outfile}.json", "w") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

def intToDecimal(qty, decimal):
    return int(qty * int("".join(["1"] + ["0"]*decimal)))

def decimalToInt(qty, decimal):
    return qty/ int("".join((["1"]+ ["0"]*decimal)))

# разбивка массива на части по кол-ву элементов
def func_chunks_generators(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i: i + n]


text1 = '''
 /$$   /$$  /$$$$$$  /$$$$$$$  /$$       /$$      /$$  /$$$$$$  /$$$$$$$ 
| $$  | $$ /$$__  $$| $$__  $$| $$      | $$$    /$$$ /$$__  $$| $$__  $$
| $$  | $$| $$  \ $$| $$  \ $$| $$      | $$$$  /$$$$| $$  \ $$| $$  \ $$
| $$$$$$$$| $$  | $$| $$  | $$| $$      | $$ $$/$$ $$| $$  | $$| $$  | $$
| $$__  $$| $$  | $$| $$  | $$| $$      | $$  $$$| $$| $$  | $$| $$  | $$
| $$  | $$| $$  | $$| $$  | $$| $$      | $$\  $ | $$| $$  | $$| $$  | $$
| $$  | $$|  $$$$$$/| $$$$$$$/| $$$$$$$$| $$ \/  | $$|  $$$$$$/| $$$$$$$/
|__/  |__/ \______/ |_______/ |________/|__/     |__/ \______/ |_______/                                                                                                                                                                                                          
'''

text2 = '''
      ___          ___                                    ___          ___                  
     /\  \        /\  \        _____                     /\  \        /\  \        _____    
     \:\  \      /::\  \      /::\  \                   |::\  \      /::\  \      /::\  \   
      \:\  \    /:/\:\  \    /:/\:\  \                  |:|:\  \    /:/\:\  \    /:/\:\  \  
  ___ /::\  \  /:/  \:\  \  /:/  \:\__\  ___     ___  __|:|\:\  \  /:/  \:\  \  /:/  \:\__\ 
 /\  /:/\:\__\/:/__/ \:\__\/:/__/ \:|__|/\  \   /\__\/::::|_\:\__\/:/__/ \:\__\/:/__/ \:|__|
 \:\/:/  \/__/\:\  \ /:/  /\:\  \ /:/  /\:\  \ /:/  /\:\~~\  \/__/\:\  \ /:/  /\:\  \ /:/  /
  \::/__/      \:\  /:/  /  \:\  /:/  /  \:\  /:/  /  \:\  \       \:\  /:/  /  \:\  /:/  / 
   \:\  \       \:\/:/  /    \:\/:/  /    \:\/:/  /    \:\  \       \:\/:/  /    \:\/:/  /  
    \:\__\       \::/  /      \::/  /      \::/  /      \:\__\       \::/  /      \::/  /   
     \/__/        \/__/        \/__/        \/__/        \/__/        \/__/        \/__/    
'''

texts = [text1, text2]
colors = ['green', 'yellow', 'blue', 'magenta', 'cyan']

RUN_TEXT = random.choice(texts)
RUN_COLOR = random.choice(colors)



