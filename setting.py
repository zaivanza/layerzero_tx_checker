MIN_VALUE_ERC20 = 0 # $
MIN_VALUE_ETH   = 0 # eth
MIN_TX_AMOUNT   = 5
LAST_DATE_TX    = '20-04-2023' # d-m-y

# если кол-во дней между первой и последней транзакцией меньше этого числа, кошелек выделяется
DAYS_AMOUNT     = 30

# чтобы отключить сеть, закомментируй ее
chains = [
    'arbitrum',
    'optimism',
    'avalanche',
    'bsc',
    'polygon',
    'fantom',
    # 'ethereum',
]

FILE_NAME = 'layerzero' # имя файла csv, который скрипт создаст сам

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
- avalanche, arbitrum, optimism, bsc, polygon
6. holograph :
- avalanche => chain (nft)
- polygon => chain (nft)
7. harmony :
- bsc => harmony (bnb)
8. core :
- bsc => core (usdt / usdc)

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
    },
    'polygon': {
        'USDT': '0xc2132D05D31c914a87C6611C10748AEb04B58e8F',
        'USDC': '0x2791bca1f2de4661ed88a30c99a7a9449aa84174',
        'BTCB': '0x2297aEbD383787A160DD0d9F71508148769342E3',
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
        token_contracts['polygon']['BTCB'] : 
            {
                'bitcoinbridge': '0x0000000000000000000000000000000000000000',
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
    'avalanche': {
        token_contracts['avalanche']['BTCB'] : 
            {
                'bitcoinbridge': '0x2297aEbD383787A160DD0d9F71508148769342E3',
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
    },
    'ethereum': {
        'stargate': '0x150f94B44927F078737562f0fcF3C95c01Cc2376',
    },
    'polygon': {
        'holograph': '0xd85b5e176a30edd1915d6728faebd25669b60d8b',
    },
    'bsc': {
        'harmony': '0x128AEdC7f41ffb82131215e1722D8366faaD0CD4',
    },
}
