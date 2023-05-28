
# ================================ setting ================================

CSV_WRITE_CHAINS    = True # True если нужно записывать в csv информацию о кол-ве транзакций в каждой сети.         False если не нужно
CSV_WRITE_PROTOCOLS = True # True если нужно записывать в csv информацию о кол-ве транзакций в каждом протоколе.    False если не нужно

MIN_VALUE_ERC20     = 0 # $
MIN_VALUE_ETH       = 0.1 # eth
MIN_TX_AMOUNT       = 20
LAST_DATE_TX        = '15-05-2023' # d-m-y
MIN_AMOUNT_CHAINS   = 4 # сколько заюзанных сетей 

# если кол-во дней между первой и последней транзакцией меньше этого числа, кошелек выделяется
DAYS_AMOUNT     = 30

# какие сети парсим. чтобы отключить сеть, закомментируй ее
chains = [
    'arbitrum',
    'optimism',
    'avalanche',
    'bsc',
    'polygon',
    'fantom',
    'ethereum',
]

# если кол-во транзакций в сети будет меньше назначенного числа, кошелек выделяется
MIN_TX_AMOUNT_CHAINS = {
    "arbitrum"  : 0,
    "optimism"  : 0,
    "avalanche" : 0,
    "bsc"       : 10,
    "polygon"   : 0,
    "fantom"    : 0,
    "ethereum"  : 0
}

# если кол-во транзакций в протоколе (смотрит во всех сетях) будет меньше назначенного числа, кошелек выделяется
MIN_TX_AMOUNT_PROTOCOLS = {
    "aptosbridge"   : 0,
    "stargate"      : 0,
    "testnetbridge" : 0,
    "woofi"         : 0,
    "holograph"     : 1,
    "bitcoinbridge" : 0,
    "harmony"       : 0,
    "core"          : 0,
    "angle"         : 0,
}

FILE_NAME = 'layerzero' # имя файла csv, который скрипт создаст сам

# =========================================================================


'''

ВАЖНО : скрипт парсит только первые 10.000 транзакций кошелька в каждой сети, то есть если на кошельке в сети > 10.000 транзакций, то он все что после 10.000 парсить не будет

Сейчас добавлена проверка всех транзакций в модулях :

1. testnet bridge : 
- arbitrum  => goerli (eth) 
- optimism  => goerli (eth) 
2. stargate : 
- arbitrum  => chain (eth / usdc / usdt)
- optimism  => chain (eth / usdc)
- polygon   => chain (usdc / usdt)
- fantom    => chain (usdc)
- ethereum  => chain (eth / usdc / usdt)
- avalanche => chain (usdc / usdt)
- bsc       => chain (usdt)
3. woofi :
- arbitrum  => chain (eth / usdc)
- optimism  => chain (eth)
- polygon   => chain (matic / usdc)
- bsc       => chain (bnb)
- fantom    => chain (usdc)
- avalanche => chain (avax / usdc)
4. aptosbridge :
- arbitrum  => aptos (eth)
- bsc       => aptos (usdt / usdc)
- avalanche => aptos (usdc)
5. bitcoin bridge :
- avalanche, arbitrum, optimism, bsc, polygon
6. holograph :
- avalanche => chain (nft)
- polygon   => chain (nft)
7. harmony :
- bsc       => harmony (bnb)
8. core :
- bsc       => core (usdt / usdc)

'''

# контракты erc20 токенов
token_contracts = {
    'arbitrum': {
        'USDT': '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9',
        'USDC': '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8',
        'BTCB': '0x2297aEbD383787A160DD0d9F71508148769342E3',
    },
    'optimism': {
        'USDT': '0x94b008aa00579c1307b0ef2c499ad98a8ce58e58',
        'USDC': '0x7f5c764cbc14f9669b88837ca1490cca17c31607',
        'BTCB': '0x2297aEbD383787A160DD0d9F71508148769342E3',
    },
    'bsc': {
        'USDT': '0x55d398326f99059ff775485246999027b3197955',
        'USDC': '0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d',
        'BTCB': '0x2297aEbD383787A160DD0d9F71508148769342E3',
        'agEUR': '0x12f31B73D812C6Bb0d735a218c086d44D5fe5f89',
    },
    'polygon': {
        'USDT': '0xc2132D05D31c914a87C6611C10748AEb04B58e8F',
        'USDC': '0x2791bca1f2de4661ed88a30c99a7a9449aa84174',
        'BTCB': '0x2297aEbD383787A160DD0d9F71508148769342E3',
        'agEUR': '0xE0B52e49357Fd4DAf2c15e02058DCE6BC0057db4',
    },
    'fantom': {
        'USDT': '0x049d68029688eabf473097a2fc38ef61633a3c7a',
        'USDC': '0x04068DA6C83AFCFA0e13ba15A6696662335D5B75',
    },
    'ethereum': {
        'USDT': '0xdac17f958d2ee523a2206206994597c13d831ec7',
        'USDC': '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
    },
    'avalanche': {
        'BTCB': '0x152b9d0FdC40C096757F570A51E494bd4b943E50',
        'USDC': '0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E',
        'USDT': '0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7',
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
                'woofi': '0x4ab421de52b3112d02442b040dd3dc73e8af63b5',
            },
        token_contracts['arbitrum']['BTCB'] : 
            {
                'bitcoinbridge': '0x0000000000000000000000000000000000000000',
            },
    },
    'optimism': {
        token_contracts['optimism']['USDC'] : 
            {
                'stargate': '0xdecc0c09c3b5f6e92ef4184125d5648a66e35298',
            },
        token_contracts['optimism']['BTCB'] : 
            {
                'bitcoinbridge': '0x0000000000000000000000000000000000000000',
            },
    },
    'bsc': {
        token_contracts['bsc']['USDT'] : 
            {
                'aptosbridge': '0x2762409Baa1804D94D8c0bCFF8400B78Bf915D5B',
                'core': '0x52e75d318cfb31f9a2edfa2dfee26b161255b233',
                'stargate': '0x9aa83081aa06af7208dcc7a4cb72c94d057d2cda',
            },
            
        token_contracts['bsc']['USDC'] : 
            {
                'aptosbridge': '0x2762409Baa1804D94D8c0bCFF8400B78Bf915D5B',
                'core': '0x52e75d318cfb31f9a2edfa2dfee26b161255b233',
            },
        token_contracts['bsc']['BTCB'] : 
            {
                'bitcoinbridge': '0x0000000000000000000000000000000000000000',
            },
        token_contracts['bsc']['agEUR'] : 
            {
                'angle': '0xe9f183fc656656f1f17af1f2b0df79b8ff9ad8ed',
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
                'woofi': '0xaa9c15cd603428ca8ddd45e933f8efe3afbcc173',
            },
        token_contracts['polygon']['BTCB'] : 
            {
                'bitcoinbridge': '0x0000000000000000000000000000000000000000',
            },
        token_contracts['polygon']['agEUR'] : 
            {
                'angle': '0x0c1ebbb61374da1a8c57cb6681bf27178360d36f',
            },
    },
    'fantom': {

        token_contracts['fantom']['USDC'] : 
            {
                'stargate': '0x12edea9cd262006cc3c4e77c90d2cd2dd4b1eb97',
                'woofi': '0x72dc7fa5eeb901a34173c874a7333c8d1b34bca9',
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
    'avalanche': {
        token_contracts['avalanche']['BTCB'] : 
            {
                'bitcoinbridge': '0x2297aEbD383787A160DD0d9F71508148769342E3',
            },
        token_contracts['avalanche']['USDT'] : 
            {
                'stargate': '0x29e38769f23701a2e4a8ef0492e19da4604be62c',
            },
        token_contracts['avalanche']['USDC'] : 
            {
                'stargate': '0x1205f31718499dbf1fca446663b532ef87481fe1',
                'woofi': '0x51af494f1b4d3f77835951fa827d66fc4a18dae8',
                'aptosbridge': '0xa5972eee0c9b5bbb89a5b16d1d65f94c9ef25166',
            },
    },
}

# контракты протоколов с нативным токеном
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
        'testnetbridge': '0x0a9f824c05a74f577a536a8a0c673183a872dff4',
        'aptosbridge': '0x86Bb63148d17d445Ed5398ef26Aa05Bf76dD5b59',
    },
    'avalanche': {
        'holograph': '0xd85b5e176a30edd1915d6728faebd25669b60d8b',
        'woofi': '0x51AF494f1B4d3f77835951FA827D66fc4A18Dae8',
    },
    'ethereum': {
        'stargate': '0x150f94B44927F078737562f0fcF3C95c01Cc2376',
    },
    'polygon': {
        'holograph': '0xd85b5e176a30edd1915d6728faebd25669b60d8b',
        'woofi': '0xAA9c15cd603428cA8ddD45e933F8EfE3Afbcc173',
    },
    'bsc': {
        'harmony': '0x128AEdC7f41ffb82131215e1722D8366faaD0CD4',
        'woofi': '0x81004C9b697857fD54E137075b51506c739EF439',
    },
}

