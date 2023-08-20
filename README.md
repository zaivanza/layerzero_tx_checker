[![Typing SVG](https://readme-typing-svg.herokuapp.com?color=%2336BCF7&lines=LayerZero+:+tx_checker)](https://git.io/typing-svg)

Скрипт парсит все транзакции через сканы, ищет совпадения по контракту из модулей (ниже) и выписывает в csv файл результат.

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
- ethereum  => aptos (eth / usdc / usdt)
5. bitcoin bridge :
- avalanche, arbitrum, optimism, bsc, polygon
6. holograph :
- avalanche => chain (nft)
- polygon   => chain (nft)
7. harmony :
- bsc       => harmony (bnb)
8. core :
- bsc       => core (usdt / usdc)
9. angle :
- bsc       => chain (agEUR)
- polygon   => chain (agEUR)
- celo      => chain (agEUR)
- gnosis    => chain (agEUR)
10. zkbridge :
- bsc       => chain 
- polygon   => chain 
11. merkly gas refuel :
- arbitrum  => chain 
- optimism  => chain 
- polygon   => chain 
- bsc       => chain
- fantom    => chain 
- avalanche => chain 
- celo      => chain 
- gnosis    => chain 


# Настройка :

Создаем виртуальное окружение :
`python3 -m venv .venv`

Активируем :
`.venv\Scripts\activate.bat` or `.venv\Scripts\activate.ps1` - для Windows.
`source .venv/bin/activate` - для Linux и MacOS.

Устанавливаем библиотеки :
`pip3 install -r requirements.txt`

Накидали статью для маленьких, где все объясняется на картинках : https://teletype.in/@hodlmod.eth_kids/layerzero_tx_checker

# Настройка config.py и данных :
1. В файл `wallets.txt` выписываем адреса кошельков построчно.
2. В папке data в текстовые файлы выписываем апи ключи от сканов. Для этого нужно зарегистрироваться (ссылки ниже) и создать ключ. Одного ключа на каждый скан хватит. Ключи вписывать построчно. Увеличение кол-ва ключей лишь увеличит скорость парсинга :
- `arb_api.txt` : https://arbiscan.io/myapikey
- `avax_api.txt` : https://snowtrace.io/myapikey
- `bsc_api.txt` : https://bscscan.com/myapikey
- `opt_api.txt` : https://optimistic.etherscan.io/myapikey
- `eth_api.txt` : https://etherscan.io/myapikey
- `polygon_api.txt` : https://polygonscan.com/myapikey
- `ftm_api.txt` : https://ftmscan.com/myapikey
3. В файле `setting.py` меняем значения переменных под себя :
- `CSV_WRITE_CHAINS` - True если нужно записывать в csv информацию о кол-ве транзакций в каждой сети.
- `CSV_WRITE_PROTOCOLS` - True если нужно записывать в csv информацию о кол-ве транзакций в каждом протоколе.
- `MIN_VALUE_ERC20` - если объем в erc20 токенах будет меньше этого числа, кошелек выделяется.
- `MIN_VALUE_ETH` - если объем в нативных (eth) токенах будет меньше этого числа, кошелек выделяется.
- `MIN_TX_AMOUNT` - если кол-во транзакций в layerzero меньше этого числа, кошелек выделяется.
- `LAST_DATE_TX` - если последняя транзакция была сделана позже этой даты, кошелек выделяется. 
- `MIN_AMOUNT_CHAINS` - если кол-во заюзанных сетей будет меньше этого числа, кошелек выделяется.
- `DAYS_AMOUNT` - если кол-во дней между первой и последней транзакцией меньше этого числа, кошелек выделяется.
- `chains` - какие сети оставляем включенными. Если хочешь выключить сеть, закомментируй ее.
- `MIN_TX_AMOUNT_CHAINS` - если кол-во транзакций в сети будет меньше назначенного числа, кошелек выделяется.
- `MIN_TX_AMOUNT_PROTOCOLS` - если кол-во транзакций в протоколе (смотрит во всех сетях) будет меньше назначенного числа, кошелек выделяется.
- `FILE_NAME` - как назвать csv файл с результатом.

# Результат :
После выполнения скрипта, данные будут записаны в csv файл. Теперь его нужно импортировать в гугл таблицу. Как это сделать : https://topgoogle.ru/kak-importirovat-i-otkryt-csv-fajl-v-google-tablicax/

Паблик : https://t.me/hodlmodeth. [ code ] чат : https://t.me/code_hodlmodeth
