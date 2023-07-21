from config import *


def round_to(num, digits=3):
    if num == 0: return 0
    try: 
        scale = int(-math.floor(math.log10(abs(num - int(num))))) + digits - 1
        if scale < digits: scale = digits
        return round(num, scale)
    except: return num

def get_prices():

    try:

        logger.info('get prices')

        prices = {
            'ETH': 0, 
            'BNB': 0, 
            'AVAX': 0, 
            'MATIC': 0, 
            'AVAX': 0, 
            'FTM': 0,
            'BTC': 0,
            'USDT': 0,
            'USDC': 0,
            'BUSD': 0,
            'agEUR': 0
        }

        for symbol in prices:

            url =f'https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USDT'
            response = requests.get(url)

            try:
                result  = [response.json()]
                price   = result[0]['USDT']
                prices[symbol] = float(price)
            except Exception as error:
                logger.error(f'{error}. set price : 0')
                prices[symbol] = 0

        logger.info(prices)
        print()

        return prices
    
    except Exception as error:
        logger.error(f'{error}. Try again')
        time.sleep(1)
        return get_prices()
    
def get_value(token, amount):

    if token == 'BTC.b': token = 'BTC'
    if token == 'BSC-USD': token = 'USDT'
    if token == 'USDC.e': token = 'USDC'

    price = PRICES[token]
    value = amount * price
    return value

datas = {}
async def get_get(session, wallet, chain, token):

    try:

        api_key = random.choice(api_keys[chain])

        if token == 'native':
            url = f'{base_url[chain]}/api?module=account&action=txlist&address={wallet}&startblock=1&endblock=9999999999&sort=asc&apikey={api_key}'
            type_ = 'eth'

        else:
            url = f'{base_url[chain]}/api?module=account&action=tokentx&contractaddress={token}&address={wallet}&startblock=1&endblock=9999999999&sort=asc&apikey={api_key}'
            type_ = 'erc20'

        async with session.get(url, ssl=False, timeout=10) as resp:
            resp_json = await resp.json(content_type=None)
            # print(resp_json)
            datas[wallet][type_][chain][token].update(resp_json)

        if datas[wallet][type_][chain][token]['result'] in [
            "Max rate limit reached", 
            "Max rate limit reached, rate limit of 5/1sec applied", 
            "Max rate limit reached, please use API Key for higher rate limit"
            ]:
            await asyncio.sleep(1)
            return await get_get(session, wallet, chain, token)
        
        elif datas[wallet][type_][chain][token]['result'] == "Invalid API Key":
            logger.error(f'{wallet} : {chain} : Invalid API Key : {api_key}')

        else: 
            logger.success(f'{wallet} : {chain}')


    except Exception as error:

        # logger.error(f'{wallet} | error : {error}')
        time_sleep = 3
        await asyncio.sleep(time_sleep)
        return await get_get(session, wallet, chain, token)

async def main(wallet):

    tasks = []

    async with aiohttp.ClientSession() as session:
    
        datas.update({wallet: {
            "eth" : {}, "erc20" : {},
        }})

        for chain in chains:
            datas[wallet]['eth'].update({chain: {'native': {}}})
            datas[wallet]['erc20'].update({chain: {}})
            
            task = asyncio.create_task(get_get(session, wallet, chain, 'native'))
            tasks.append(task)

            try:
                for token in token_contracts[chain].items():
                    datas[wallet]['erc20'][chain].update({token[1]: {}})
                    task = asyncio.create_task(get_get(session, wallet, chain, token[1]))
                    tasks.append(task)
            except: None

        await asyncio.gather(*tasks)

def get_data_new():

    TOTAL = []

    for items_1 in datas.items():

        wallet = items_1[0]
        massive = {wallet: {}}

        for items_2 in items_1[1].items():
            type_ = items_2[0]
            

            massive[wallet].update({type_ : {}})
        
            for items_3 in items_2[1].items():

                times = []
                chain = items_3[0]

                massive[wallet][type_].update(
                    {
                        chain : {
                            "first_tx": 0,
                            "last_tx": 0,
                            "usd_value": 0,
                            "total_value": 0,
                            "total_nonce": 0,
                            "values": {
                                "aptosbridge": 0,
                                "stargate": 0,
                                "testnetbridge": 0,
                                "woofi": 0,
                                "holograph": 0,
                                "bitcoinbridge": 0,
                                "harmony": 0,
                                "core": 0,
                                "angle": 0,
                                "zkbridge": 0,
                                "merkly": 0,
                            },
                            "nonces": {
                                "aptosbridge": 0,
                                "stargate": 0,
                                "testnetbridge": 0,
                                "woofi": 0,
                                "holograph": 0,
                                "bitcoinbridge": 0,
                                "harmony": 0,
                                "core": 0,
                                "angle": 0,
                                "zkbridge": 0,
                                "merkly": 0,
                            }
                        }
                    }
                )

                for items_4 in items_3[1].items():
                    
                    address_token   = items_4[0].upper()
                    result_         = items_4[1]['result']

                    for data in result_:

                        try:
                            
                            if type_ == 'eth':
                                status_tx = int(data['isError'])
                                if status_tx == 1: continue
                        
                            contract    = data['to'].upper() # contract / address
                            value       = int(data['value'])
                            timestamp   = int(data['timeStamp'])

                            if type_ == 'eth':
                                decimals = 18
                                contracts = contracts_eth
                                symbol = native_tokens[chain]
                            elif type_ == 'erc20':
                                decimals = int(data['tokenDecimal'])
                                contracts = contracts_erc20
                                symbol = data['tokenSymbol']

                            human_value = round_to(decimalToInt(value, decimals))
                            usd_value   = get_value(symbol, human_value)

                            if type_ == 'eth':
                                for items in contracts[chain].items():
                                    name    = items[0]
                                    address = items[1].upper()

                                    if contract == address:

                                        if chain in ['polygon', 'fantom', 'bsc']:
                                            human_value = 0

                                        massive[wallet][type_][chain]['values'][name]  += human_value
                                        massive[wallet][type_][chain]['total_value']   += human_value

                                        massive[wallet][type_][chain]['nonces'][name]  += 1
                                        massive[wallet][type_][chain]['total_nonce']   += 1

                                        massive[wallet][type_][chain]['usd_value']     += usd_value

                                        times.append(timestamp)

                            elif type_ == 'erc20':

                                for items in contracts[chain].items():

                                    address_ = items[0].upper()

                                    if address_ == address_token:

                                        for _ in items[1].items():

                                            name    = _[0]
                                            address = _[1].upper()

                                            # cprint(f'{name} : {contract} : {address}', 'blue')

                                            if contract == address:

                                                massive[wallet][type_][chain]['values'][name]  += human_value
                                                massive[wallet][type_][chain]['total_value']   += human_value

                                                massive[wallet][type_][chain]['nonces'][name]  += 1
                                                massive[wallet][type_][chain]['total_nonce']   += 1

                                                massive[wallet][type_][chain]['usd_value']     += usd_value

                                                times.append(timestamp)

                        except Exception as error: 
                            # logger.error(error)
                            None

                times.sort()

                try:
                    massive[wallet][type_][chain]['first_tx']   = times[0]
                    massive[wallet][type_][chain]['last_tx']    = times[-1]
                except: None

        TOTAL.append(massive)


    return TOTAL

def get_results(TOTAL):

    results = []

    for account in TOTAL:

        for items in account.items():
                
            wallet = items[0]
            d_ = {
                'txs': [],
                'value_erc20': [],
                'value_eth': [],
                'nonce': [],
            }

            result = {
                wallet : {
                    'first_tx': 0,
                    'last_tx': 0,
                    'nonce': 0,
                    'value_erc20': 0,
                    'value_eth': 0,
                    'value': 0,
                    'nonce_chain': {
                        "arbitrum": 0,
                        "optimism": 0,
                        "avalanche": 0,
                        "bsc": 0,
                        "polygon": 0,
                        "fantom": 0,
                        "ethereum": 0,
                        "celo": 0,
                        "gnosis": 0,
                    },
                    'nonce_protocols': {
                        "aptosbridge": 0,
                        "stargate": 0,
                        "testnetbridge": 0,
                        "woofi": 0,
                        "holograph": 0,
                        "bitcoinbridge": 0,
                        "harmony": 0,
                        "core": 0,
                        "angle": 0,
                        "zkbridge": 0,
                        "merkly": 0,
                    }
                }
            }
            for items in items[1].items():
                type_ = items[0]
                
                for items in items[1].items():
                    chain       = items[0]
                    first_tx    = items[1]['first_tx']
                    last_tx     = items[1]['last_tx']
                    total_value = items[1]['total_value']
                    total_nonce = items[1]['total_nonce']
                    nonces      = items[1]['nonces']
                    value       = round_to(items[1]['usd_value'])

                    result[wallet]['nonce_chain'][chain] += total_nonce

                    result[wallet]['value'] += value

                    for protocol in nonces.items():
                        name    = protocol[0]
                        amount  = protocol[1]
                        result[wallet]['nonce_protocols'][name] += amount

                    if first_tx     != 0    : d_['txs'].append(first_tx)
                    if last_tx      != 0    : d_['txs'].append(last_tx)

                    if type_ == 'eth':
                        d_['value_eth'].append(total_value)
                    if type_ == 'erc20':
                        d_['value_erc20'].append(total_value)

                    d_['nonce'].append(total_nonce)

            d_['txs'].sort()

            if len(d_['txs']) > 0:
                result[wallet]['first_tx']  = d_['txs'][0]
                result[wallet]['last_tx']   = d_['txs'][-1]
            else:
                result[wallet]['first_tx']  = 0
                result[wallet]['last_tx']   = 0

            result[wallet]['nonce']         = sum(d_['nonce'])
            result[wallet]['value_erc20']   = sum(d_['value_erc20'])
            result[wallet]['value_eth']     = sum(d_['value_eth'])

            results.append(result)


    return results

def compare_date(date_1, date_2):

    try:
        a = date_1.split('-')
        b = date_2.split('-')

        aa = datetime(day=int(a[0]),month=int(a[1]),year=int(a[2]))
        bb = datetime(day=int(b[0]),month=int(b[1]),year=int(b[2]))
        days_amount = int(str(bb-aa).split()[0]) 

    except Exception as error:
        logger.error(error)
        days_amount = 0

    return days_amount

def send_result(results):

    time_stamp = time.mktime(date_timestamp.datetime.strptime(LAST_DATE_TX, "%d-%m-%Y").timetuple())

    w_ = {
        'date': [],
        'value': [],
        'tx_amount': [],
        'days_amount': [],
        'amount_chains': [],
        'tx_amount_chains': {
            "arbitrum"  : [],
            "optimism"  : [],
            "avalanche" : [],
            "bsc"       : [],
            "polygon"   : [],
            "fantom"    : [],
            "ethereum"  : [],
            "celo"      : [],
            "gnosis"    : [],
        },
        'tx_amount_protocols': {
            "aptosbridge"   : [],
            "stargate"      : [],
            "testnetbridge" : [],
            "woofi"         : [],
            "holograph"     : [],
            "bitcoinbridge" : [],
            "harmony"       : [],
            "core"          : [],
            "angle"         : [],
            "zkbridge"      : [],
            "merkly"        : [],
        },
    }

    with open(f'{outfile}{FILE_NAME}.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        
        csv_list = [
            ['number', 'wallet', 'tx_amount', 'amount_chains', 'value $', 'first_tx', 'last_tx', 'number_of_days_between_first_and_last_tx'],
            []
        ]

        # просто выписываем все результаты
        zero = 0
        for wallets in results:
            zero += 1
            for wallet in wallets.items():
                # zero += 1

                address     = wallet[0]

                first_tx    = wallet[1]['first_tx']
                last_tx     = wallet[1]['last_tx']
                tx_amount   = wallet[1]['nonce']
                value       = int(wallet[1]['value'])

                nonce_chains    = wallet[1]['nonce_chain']
                nonce_protocols = wallet[1]['nonce_protocols']

                amount_chains = 0
                for nonce_chain in nonce_chains.items():
                    chain = nonce_chain[0]
                    nonce = nonce_chain[1]
                    if CSV_WRITE_CHAINS == True: 
                        if chain not in csv_list[0]:
                            csv_list[0].append(chain)

                    if nonce > 0:
                        amount_chains += 1

                    if nonce < MIN_TX_AMOUNT_CHAINS[chain]:
                        w_['tx_amount_chains'][chain].append(address)

                for nonce_protocol in nonce_protocols.items():
                    name  = nonce_protocol[0]
                    nonce = nonce_protocol[1]
                    if CSV_WRITE_PROTOCOLS == True: 
                        if name not in csv_list[0]:
                            csv_list[0].append(name)

                    if nonce < MIN_TX_AMOUNT_PROTOCOLS[name]:
                        w_['tx_amount_protocols'][name].append(address)


                if first_tx != 0 and last_tx != 0:
                    first_tx_date   = datetime.fromtimestamp(first_tx).strftime('%d-%m-%y')
                    last_tx_date    = datetime.fromtimestamp(last_tx).strftime('%d-%m-%y')
                    days_amount     = compare_date(first_tx_date, last_tx_date)
                else:
                    first_tx_date   = 0
                    last_tx_date    = 0
                    days_amount     = 0

                w2_list = [zero, address, tx_amount, amount_chains, value, first_tx_date, last_tx_date, days_amount]

                if CSV_WRITE_CHAINS == True:
                    for nonce_chain in nonce_chains.items():
                        nonce = nonce_chain[1]
                        w2_list.append(nonce)

                if CSV_WRITE_PROTOCOLS == True:
                    for nonce_protocol in nonce_protocols.items():
                        nonce = nonce_protocol[1]
                        w2_list.append(nonce)

                csv_list[1].append(w2_list)

                if value < MIN_VALUE:
                    w_['value'].append(address)
                if last_tx < time_stamp:
                    w_['date'].append(address)
                if tx_amount < MIN_TX_AMOUNT:
                    w_['tx_amount'].append(address)
                if days_amount < DAYS_AMOUNT:
                    w_['days_amount'].append(address)
                if amount_chains < MIN_AMOUNT_CHAINS:
                    w_['amount_chains'].append(address)


        spamwriter.writerow(csv_list[0])
        for items in csv_list[1]:
            spamwriter.writerow(items)

        color = 'magenta'
        if len(w_['value']) > 0:
            spamwriter.writerow([])
            spamwriter.writerow(['number', f'value < {MIN_VALUE}'])
            cprint(f'\nНа этих кошельках value < {MIN_VALUE} :', color)

            zero = 0
            for wallet in w_['value']:
                zero += 1
                cprint(wallet, 'white')
                spamwriter.writerow([zero, wallet])


        if len(w_['date']) > 0:
            spamwriter.writerow([])
            spamwriter.writerow(['number', f'last_tx_date < {LAST_DATE_TX}'])
            cprint(f'\nНа этих кошельках не было транзакций после {LAST_DATE_TX} :', color)

            zero = 0
            for wallet in w_['date']:
                zero += 1
                cprint(wallet, 'white')
                spamwriter.writerow([zero, wallet])

        if len(w_['tx_amount']) > 0:
            spamwriter.writerow([])
            spamwriter.writerow(['number', f'tx_amount < {MIN_TX_AMOUNT}'])
            cprint(f'\nНа этих кошельках кол-во транзакций < {MIN_TX_AMOUNT} :', color)

            zero = 0
            for wallet in w_['tx_amount']:
                zero += 1
                cprint(wallet, 'white')
                spamwriter.writerow([zero, wallet])

        if len(w_['amount_chains']) > 0:
            spamwriter.writerow([])
            spamwriter.writerow(['number', f'amount_chains < {MIN_AMOUNT_CHAINS}'])
            cprint(f'\nНа этих кошельках кол-во заюзанных сетей < {MIN_AMOUNT_CHAINS} :', color)

            zero = 0
            for wallet in w_['amount_chains']:
                zero += 1
                cprint(wallet, 'white')
                spamwriter.writerow([zero, wallet])

        if len(w_['days_amount']) > 0:
            spamwriter.writerow([])
            spamwriter.writerow(['number', f'days_amount < {DAYS_AMOUNT}'])
            cprint(f'\nНа этих кошельках кол-во дней между первой и последней транзакцией < {DAYS_AMOUNT} :', color)

            zero = 0
            for wallet in w_['days_amount']:
                zero += 1
                cprint(wallet, 'white')
                spamwriter.writerow([zero, wallet])


        for items in w_['tx_amount_chains'].items():
            chain   = items[0]
            wallets = items[1]
            if len(wallets) > 0:
                spamwriter.writerow([])
                spamwriter.writerow(['number', f'tx_amount in {chain} < {MIN_TX_AMOUNT_CHAINS[chain]}'])
                cprint(f'\nНа этих кошельках кол-во транзакций в {chain} < {MIN_TX_AMOUNT_CHAINS[chain]} :', color)

                zero = 0
                for wallet in wallets:
                    zero += 1
                    cprint(wallet, 'white')
                    spamwriter.writerow([zero, wallet])

        for items in w_['tx_amount_protocols'].items():
            name    = items[0]
            wallets = items[1]
            if len(wallets) > 0:
                spamwriter.writerow([])
                spamwriter.writerow(['number', f'tx_amount in {name} < {MIN_TX_AMOUNT_PROTOCOLS[name]}'])
                cprint(f'\nНа этих кошельках кол-во транзакций в {name} < {MIN_TX_AMOUNT_PROTOCOLS[name]} :', color)

                zero = 0
                for wallet in wallets:
                    zero += 1
                    cprint(wallet, 'white')
                    spamwriter.writerow([zero, wallet])



        cprint(f'\nРезультаты записаны в файл : {outfile}{FILE_NAME}.csv\n', 'blue')


async def run():

    wallets_list = (list(func_chunks_generators(WALLETS, 50)))

    lens = 0
    for wallets in wallets_list:

        lens = len(wallets) + lens

        tasks = []
        for wallet in wallets:
            tasks.append(asyncio.create_task(main(wallet)))


        await asyncio.gather(*tasks)
        time.sleep(3)
    

if __name__ == "__main__":

    cprint(RUN_TEXT, RUN_COLOR)
    cprint(f'\nsubscribe to us : https://t.me/hodlmodeth\n', RUN_COLOR)

    start = time.perf_counter()

    PRICES = get_prices()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())

    TOTAL = get_data_new()
    results = get_results(TOTAL)

    send_result(results)

    fin = round((time.perf_counter() - start), 1)
    cprint(f'finish : {fin}', 'blue')

    # call_json(datas, 'datas')
    # call_json(TOTAL, 'total')
    # call_json(results, 'results')





