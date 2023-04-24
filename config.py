import json, requests, time
from termcolor import cprint
from datetime import date, datetime
import datetime as date_timestamp
import math
import random
import asyncio, aiohttp
import csv
from loguru import logger

'''

ВАЖНО : скрипт парсит только первые 10.000 транзакций кошелька в каждой сети, то есть если на кошельке в сети > 10.000 транзакций, то он все что после 10.000 парсить не будет

Сейчас добавлена проверка всех транзакций в модулях :

1. testnet bridge : 
- arbitrum => goerli (eth) 
- optimism => goerli (eth) 
2. stargate : 
- arbitrum => chain (eth / usdc / usdt)
- optimism => chain (eth / usdc)
- polygon => chain (usdc / usdt)
- fantom => chain (usdc)
- ethereum => chain (eth / usdc / usdt)
3. woofi :
- arbitrum => chain (eth)
- optimism => chain (eth)
4. aptosbridge :
- arbitrum => aptos (eth)
- bsc => aptos (usdt / usdc)
5. bitcoin bridge :
- avaxc => chain (btcb)
- arbitrum => chain (btcb)
- optimism => chain (btcb)
6. holograph :
- avaxc => chain (nft)
- polygon => chain (nft)

'''


MIN_VALUE_ERC20 = 0 # $
MIN_VALUE_ETH   = 0.5 # eth
MIN_TX_AMOUNT   = 10 
LAST_DATE_TX    = '12/04/2023' # d/m/y

FILE_NAME       = 'layerzero'

# чтобы отключить сеть, закомментируй ее
chains = [
    'arbitrum',
    'optimism',
    'avaxc',
    'bsc',
    'polygon',
    'fantom',
    'ethereum',
]


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

api_keys = {
    'arbitrum'  : ARB_API_KEYS,
    'optimism'  : OPT_API_KEYS,
    'avaxc'     : AVAX_API_KEYS,
    'bsc'       : BSC_API_KEYS,
    'polygon'   : POLYGON_API_KEYS,
    'fantom'    : FTM_API_KEYS,
    'ethereum'  : ETH_API_KEYS,
}

# api urls
base_url = {
    'arbitrum'  : 'https://api.arbiscan.io',
    'optimism'  : 'https://api-optimistic.etherscan.io',
    'avaxc'     : 'https://api.snowtrace.io',
    'bsc'       : 'https://api.bscscan.com',
    'polygon'   : 'https://api.polygonscan.com',
    'fantom'    : 'https://api.ftmscan.com',
    'ethereum'  : 'https://api.etherscan.io',
}

# контракты токенов
token_contracts = {
    'arbitrum': {
        'USDT': '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9',
        'USDC': '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8'
    },
    'optimism': {
        'USDT': '0x94b008aa00579c1307b0ef2c499ad98a8ce58e58',
        'USDC': '0x7f5c764cbc14f9669b88837ca1490cca17c31607',
    },
    'bsc': {
        'USDT': '0x55d398326f99059ff775485246999027b3197955',
        'USDC': '0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d',
    },
    'polygon': {
        'USDT': '0xc2132D05D31c914a87C6611C10748AEb04B58e8F',
        'USDC': '0x2791bca1f2de4661ed88a30c99a7a9449aa84174',
    },
    'fantom': {
        'USDT': '0x049d68029688eabf473097a2fc38ef61633a3c7a',
        'USDC': '0x04068DA6C83AFCFA0e13ba15A6696662335D5B75',
    },
    'ethereum': {
        'USDT': '0xdac17f958d2ee523a2206206994597c13d831ec7',
        'USDC': '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
    },
}

# контракты протоколов с erc20
contracts_erc20 = {
    'arbitrum': {
        token_contracts['arbitrum']['USDT'] : 
            {
                'stargate': '0xb6cfcf89a7b22988bfc96632ac2a9d6dab60d641',
            },
        token_contracts['arbitrum']['USDC'] : 
            {
                'stargate': '0x892785f33cdee22a30aef750f285e18c18040c3e',
            },
    },
    'optimism': {
        token_contracts['optimism']['USDC'] : 
            {
                'stargate': '0xdecc0c09c3b5f6e92ef4184125d5648a66e35298',
            },
    },
    'bsc': {
        token_contracts['bsc']['USDT'] : 
            {
                'aptosbridge': '0x2762409Baa1804D94D8c0bCFF8400B78Bf915D5B'
            },
        token_contracts['bsc']['USDC'] : 
            {
                'aptosbridge': '0x2762409Baa1804D94D8c0bCFF8400B78Bf915D5B'
            },
    },
    'polygon': {
        token_contracts['polygon']['USDT'] : 
            {
                'stargate': '0x29e38769f23701a2e4a8ef0492e19da4604be62c',
            },
        token_contracts['polygon']['USDC'] : 
            {
                'stargate': '0x1205f31718499dbf1fca446663b532ef87481fe1',
            },
    },
    'fantom': {

        token_contracts['fantom']['USDC'] : 
            {
                'stargate': '0x12edea9cd262006cc3c4e77c90d2cd2dd4b1eb97',
            },
    },
    'ethereum': {
        token_contracts['ethereum']['USDT'] : 
            {
                'stargate': '0x38EA452219524Bb87e18dE1C24D3bB59510BD783',
            },
        token_contracts['ethereum']['USDC'] : 
            {
                'stargate': '0xdf0770dF86a8034b3EFEf0A1Bb3c889B8332FF56',
            },
    },
}

# контракты протоколов с eth
contracts_eth = {
    'arbitrum': {
        'stargate': '0xbf22f0f184bccbea268df387a49ff5238dd23e40',
        'woofi': '0x4ab421de52b3112d02442b040dd3dc73e8af63b5',
        'testnetbridge': '0x0a9f824c05a74f577a536a8a0c673183a872dff4',
        'aptosbridge': '0x1bacc2205312534375c8d1801c27d28370656cff',
        'bitcoinbridge': '0x2297aEbD383787A160DD0d9F71508148769342E3'
    },
    'optimism': {
        'stargate': '0xb49c4e680174e331cb0a7ff3ab58afc9738d5f8b',
        'woofi': '0xbeae1b06949d033da628ba3e5af267c3e740494b',
        'testnetbridge': '0x0a9f824c05a74f577a536a8a0c673183a872dff4',
        'aptosbridge': '0x86Bb63148d17d445Ed5398ef26Aa05Bf76dD5b59',
        'bitcoinbridge': '0x2297aebd383787a160dd0d9f71508148769342e3',
    },
    'avaxc': {
        'holograph': '0xd85b5e176a30edd1915d6728faebd25669b60d8b',
        'bitcoinbridge': '0x2297aebd383787a160dd0d9f71508148769342e3'
    },
    'ethereum': {
        'stargate': '0x150f94B44927F078737562f0fcF3C95c01Cc2376',
    },
    'polygon': {
        'holograph': '0xd85b5e176a30edd1915d6728faebd25669b60d8b',
    },
}

def call_json(result, outfile):
    with open(f"{outfile}.json", "w") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

def intToDecimal(qty, decimal):
    return int(qty * int("".join(["1"] + ["0"]*decimal)))

def decimalToInt(qty, decimal):
    return qty/ int("".join((["1"]+ ["0"]*decimal)))

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


