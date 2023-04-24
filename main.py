from config import *

def round_to(num, digits=3):
    if num == 0: return 0
    try: 
        scale = int(-math.floor(math.log10(abs(num - int(num))))) + digits - 1
        if scale < digits: scale = digits
        return round(num, scale)
    except: return num

datas = {}
async def get_get(session, wallet, chain, token):

    try:

        api_key = random.choice(api_keys[chain])

        if token == 'native':
            url = f'{base_url[chain]}/api?module=account&action=txlist&address={wallet}&startblock=1&endblock=99999999&sort=asc&apikey={api_key}'
            type_ = 'eth'

        else:
            url = f'{base_url[chain]}/api?module=account&action=tokentx&contractaddress={token}&address={wallet}&startblock=1&endblock=99999999&sort=asc&apikey={api_key}'
            type_ = 'erc20'

        async with session.get(url, ssl=False, timeout=20) as resp:
            resp_json = await resp.json(content_type=None)
            datas[wallet][type_][chain][token].update(resp_json)

        if datas[wallet][type_][chain][token]['result'] == "Max rate limit reached":
            await asyncio.sleep(1)
            return await get_get(session, wallet, chain, token)
        
        elif datas[wallet][type_][chain][token]['result'] == "Invalid API Key":
            logger.error(f'{wallet} : {chain} : Invalid API Key')

        else:
            logger.success(f'{wallet} : {chain}')


    except Exception as error:

        # logger.error(f'{wallet} | error : {error}')
        time_sleep = 3
        await asyncio.sleep(time_sleep)
        return await get_get(session, wallet, chain, token)

async def main(wallet):

    async with aiohttp.ClientSession() as session:
        tasks = []

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
                            "total_value": 0,
                            "total_nonce": 0,
                            "values": {
                                "aptosbridge": 0,
                                "stargate": 0,
                                "testnetbridge": 0,
                                "woofi": 0,
                                "holograph": 0,
                                "bitcoinbridge": 0
                            },
                            "nonces": {
                                "aptosbridge": 0,
                                "stargate": 0,
                                "testnetbridge": 0,
                                "woofi": 0,
                                "holograph": 0,
                                "bitcoinbridge": 0
                            }
                        }
                    }
                )

                for items_4 in items_3[1].items():
                    
                    address_token   = items_4[0].upper()
                    result_         = items_4[1]['result']

                    for data in result_:

                        try:
                        
                            contract    = data['to'].upper() # contract / address
                            value       = int(data['value'])
                            timestamp   = int(data['timeStamp'])

                            if type_ == 'eth':
                                decimals = 18
                                contracts = contracts_eth
                            elif type_ == 'erc20':
                                decimals = int(data['tokenDecimal'])
                                contracts = contracts_erc20

                            human_value = round_to(decimalToInt(value, decimals))

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

                                                times.append(timestamp)

                        except Exception as error: 
                            # logger.error(error)
                            None

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

            try:
                    
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

                        if first_tx != 0: d_['txs'].append(first_tx)
                        if last_tx != 0 : d_['txs'].append(last_tx)

                        if type_ == 'eth':
                            d_['value_eth'].append(total_value)
                        if type_ == 'erc20':
                            d_['value_erc20'].append(total_value)

                        d_['nonce'].append(total_nonce)

                d_['txs'].sort()

                result[wallet]['first_tx']      = d_['txs'][0]
                result[wallet]['last_tx']       = d_['txs'][-1]
                result[wallet]['nonce']         = sum(d_['nonce'])
                result[wallet]['value_erc20']   = sum(d_['value_erc20'])
                result[wallet]['value_eth']     = sum(d_['value_eth'])

                results.append(result)

            except: None

    return results

def send_result(results):

    time_stamp = time.mktime(date_timestamp.datetime.strptime(LAST_DATE_TX, "%d/%m/%Y").timetuple())

    w_ = {
        'date': [],
        'value_erc20': [],
        'value_eth': [],
        'tx_amount': [],
    }

    with open(f'{outfile}{FILE_NAME}.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        
        spamwriter.writerow(['№', 'wallet', 'tx_amount', 'value_erc20', 'value_eth', 'first_tx', 'last_tx'])

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
                value_erc20       = wallet[1]['value_erc20']
                value_erc20       = round_to(value_erc20)
                value_eth       = wallet[1]['value_eth']
                value_eth       = round_to(value_eth)

                if value_erc20 < MIN_VALUE_ERC20:
                    w_['value_erc20'].append(address)
                if value_eth < MIN_VALUE_ETH:
                    w_['value_eth'].append(address)
                if last_tx < time_stamp:
                    w_['date'].append(address)
                if tx_amount < MIN_TX_AMOUNT:
                    w_['tx_amount'].append(address)

                first_tx_date   = datetime.fromtimestamp(first_tx).strftime('%d-%m-%y')
                last_tx_date    = datetime.fromtimestamp(last_tx).strftime('%d-%m-%y')

                spamwriter.writerow([zero, address, tx_amount, value_erc20, value_eth, first_tx_date, last_tx_date])

        color = 'magenta'
        if len(w_['value_erc20']) > 0:
            spamwriter.writerow([])
            spamwriter.writerow(['№', f'value_erc20 < {MIN_VALUE_ERC20}'])
            cprint(f'\nНа этих кошельках value_erc20 < {MIN_VALUE_ERC20} :', color)

            zero = 0
            for wallet in w_['value_erc20']:
                zero += 1
                cprint(wallet, 'white')
                spamwriter.writerow([zero, wallet])

        if len(w_['value_eth']) > 0:
            spamwriter.writerow([])
            spamwriter.writerow(['№', f'value_eth < {MIN_VALUE_ETH}'])
            cprint(f'\nНа этих кошельках value_eth < {MIN_VALUE_ETH} :', color)

            zero = 0
            for wallet in w_['value_eth']:
                zero += 1
                cprint(wallet, 'white')
                spamwriter.writerow([zero, wallet])

        if len(w_['date']) > 0:
            spamwriter.writerow([])
            spamwriter.writerow(['№', f'last_tx_date < {LAST_DATE_TX}'])
            cprint(f'\nНа этих кошельках не было транзакций после {LAST_DATE_TX} :', color)

            zero = 0
            for wallet in w_['date']:
                zero += 1
                cprint(wallet, 'white')
                spamwriter.writerow([zero, wallet])

        if len(w_['tx_amount']) > 0:
            spamwriter.writerow([])
            spamwriter.writerow(['№', f'tx_amount < {MIN_TX_AMOUNT}'])
            cprint(f'\nНа этих кошельках кол-во транзакций < {MIN_TX_AMOUNT} :', color)

            zero = 0
            for wallet in w_['tx_amount']:
                zero += 1
                cprint(wallet, 'white')
                spamwriter.writerow([zero, wallet])

        cprint(f'\nРезультаты записаны в файл : {outfile}{FILE_NAME}.csv\n', 'blue')


async def run():
    tasks = []
    for wallet in WALLETS:
        tasks.append(asyncio.create_task(main(wallet)))
    await asyncio.gather(*tasks)
    

if __name__ == "__main__":

    cprint(RUN_TEXT, RUN_COLOR)
    cprint(f'\nsubscribe to us : https://t.me/hodlmodeth\n', RUN_COLOR)


    start = time.perf_counter()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    loop.close()

    TOTAL = get_data_new()
    results = get_results(TOTAL)

    send_result(results)

    fin = round((time.perf_counter() - start), 1)
    cprint(f'finish : {fin}', 'blue')


