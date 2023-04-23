import json, requests, time
from termcolor import cprint
from datetime import date, datetime
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
2. stargate : 
- arbitrum => chain (eth / usdc / usdt)
- optimism => chain (eth / usdc)
3. woofi :
- arbitrum => chain (eth)
- optimism => chain (eth)
4. aptosbridge :
- arbitrum => aptos (eth)
- bsc => aptos (usdt / usdc)
5. bitcoin bridge :
- avaxc => chain (btcb)
6. holograph :
- avaxc => chain (nft)

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

api_keys = {
    'arbitrum'  : ARB_API_KEYS,
    'optimism'  : OPT_API_KEYS,
    'avaxc'     : AVAX_API_KEYS,
    'bsc'       : BSC_API_KEYS,
}

# api urls
base_url = {
    'arbitrum'  : 'https://api.arbiscan.io',
    'optimism'  : 'https://api-optimistic.etherscan.io',
    'avaxc'     : 'https://api.snowtrace.io',
    'bsc'       : 'https://api.bscscan.com',
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
    # 'avaxc': {
    #     'USDT': '',
    # },
}

# контракты протоколов с erc20
contracts_erc20 = {
    'arbitrum': {
        token_contracts['arbitrum']['USDT'] : 
            {
                'stargate': '0xb6cfcf89a7b22988bfc96632ac2a9d6dab60d641',
                'woofi': '',
                'testnetbridge': '',
                'aptosbridge': ''
            },
        token_contracts['arbitrum']['USDC'] : 
            {
                'stargate': '0x892785f33cdee22a30aef750f285e18c18040c3e',
                'woofi': '',
                'testnetbridge': '',
                'aptosbridge': ''
            },
    },
    'optimism': {
        token_contracts['optimism']['USDC'] : 
            {
                'stargate': '0xdecc0c09c3b5f6e92ef4184125d5648a66e35298',
                'woofi': '',
                'testnetbridge': '',
                'aptosbridge': ''
            },
    },
    'bsc': {
        token_contracts['bsc']['USDT'] : 
            {
                'stargate': '',
                'woofi': '',
                'testnetbridge': '',
                'aptosbridge': '0x2762409Baa1804D94D8c0bCFF8400B78Bf915D5B'
            },
        token_contracts['bsc']['USDC'] : 
            {
                'stargate': '',
                'woofi': '',
                'testnetbridge': '',
                'aptosbridge': '0x2762409Baa1804D94D8c0bCFF8400B78Bf915D5B'
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
    },
    'optimism': {
        'stargate': '0xb49c4e680174e331cb0a7ff3ab58afc9738d5f8b',
        'woofi': '0xbeae1b06949d033da628ba3e5af267c3e740494b',
        'testnetbridge': '',
        'aptosbridge': '0x86Bb63148d17d445Ed5398ef26Aa05Bf76dD5b59',
    },
    'avaxc': {
        'stargate': '',
        'woofi': '',

        'aptosbridge': '',
        'holograph': '0xd85b5e176a30edd1915d6728faebd25669b60d8b',
        'bitcoinbridge': '0x2297aebd383787a160dd0d9f71508148769342e3'
    },
    'bsc': {
    },
}

def call_json(result, outfile):
    with open(f"{outfile}.json", "w") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

def intToDecimal(qty, decimal):
    return int(qty * int("".join(["1"] + ["0"]*decimal)))

def decimalToInt(qty, decimal):
    return qty/ int("".join((["1"]+ ["0"]*decimal)))

