'''Step 0: test out the accounts'''

import ccxt as cx
import pandas as pd
from datetime import datetime
import json
import os
from dotenv import load_dotenv
from requests import post,Session,Request
import time
import urllib.parse
import hashlib
import hmac
import base64

load_dotenv()

def get_coinbase_transactions(market, since_date,to_date):

    #usdt_blacklist=['AAVE']
    usd_buys=[]
    usd_sells=[]
    usdt_buys = []
    usdt_sells = []
    usdc_buys = []
    usdc_sells = []



    key = os.getenv("COINBASE_API_KEY")
    secret = os.getenv("COINBASE_API_SECRET")
    passphrase = os.getenv("COINBASE_API_PASSPHRASE")


    coinbase = cx.coinbasepro({
        "apiKey": key,
        "secret": secret,
        "password": passphrase,
        "enableRateLimit": True
    })


    coin_tester= market.split('/')[1]

    # For USD
    if coin_tester=='USD':
        usd_trades = coinbase.fetch_orders(market,since=since_date)
        for trade in usd_trades:
            if trade['status']=='closed'and trade['timestamp']<=to_date :
                if trade['side'] == 'sell':
                    usd_sells.append({'amount': float(trade['amount']), 'cost': float(trade['cost']),'date':str(trade['datetime']),'price':trade['price'],'side':trade['side'],'id':trade['id'],'status':trade['status'] })

                elif trade['side'] == 'buy':
                    usd_buys.append({'amount': float(trade['amount']), 'cost': float(trade['cost']),'date':str(trade['datetime']),'price':trade['price'],'side':trade['side'],'id':trade['id'],'status':trade['status'] })

    # For USDT
    if coin_tester=='USDT':
        usdt_trades =coinbase.fetch_orders(market,since=since_date)

        for trade in usdt_trades:
            if trade['status']=='closed'and  trade['timestamp']<=to_date:
                if trade['side'] == 'sell':
                    usdt_sells.append({'amount': float(trade['amount']), 'cost': float(trade['cost']),'date':str(trade['datetime']),'price':trade['price'],'side':trade['side'],'id':trade['id'],'status':trade['status'] })

                elif trade['side'] == 'buy':
                    usdt_buys.append({'amount': float(trade['amount']), 'cost': float(trade['cost']),'date':str(trade['datetime']),'price':trade['price'],'side':trade['side'],'id':trade['id'],'status':trade['status'] })

    # For USDC
    if coin_tester=='USDC':
        usdc_trades =coinbase.fetch_orders(market,since=since_date)

        for trade in usdc_trades:
            if trade['status']=='closed'and trade['timestamp']<=to_date:
                if trade['side'] == 'sell':
                    usdc_sells.append({'amount': float(trade['amount']), 'cost': float(trade['cost']),'date':str(trade['datetime']),'price':trade['price'],'side':trade['side'],'id':trade['id'],'status':trade['status'] })

                elif trade['side'] == 'buy':
                    usdc_buys.append({'amount': float(trade['amount']), 'cost': float(trade['cost']),'date':str(trade['datetime']),'price':trade['price'],'side':trade['side'],'id':trade['id'],'status':trade['status'] })


    account_book = {'usd_sells': usd_sells,'usd_buys': usd_buys,'usdt_sells':usdt_sells,'usdt_buys':usdt_buys,'usdc_sells':usdc_sells,'usdc_buys':usdc_buys }


    return account_book


def get_kraken_signature(urlpath, data, secret):
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()


def kraken_request(uri_path, data, api_key, api_sec):
    api_url = "https://api.kraken.com"
    headers = {}
    headers['API-Key'] = api_key
    # get_kraken_signature() as defined in the 'Authentication' section
    headers['API-Sign'] = get_kraken_signature(uri_path, data, api_sec)
    req = post((api_url + uri_path), headers=headers, data=data)
    return req


def get_kraken_transactions(market, since_date,to_date):

    usd_buys = []
    usd_sells = []
    usdt_buys = []
    usdt_sells = []
    usdc_buys = []
    usdc_sells = []

    api_key = os.getenv("KRAKEN_API_KEY")
    api_sec = os.getenv("KRAKEN_API_SECRET")
    resp = kraken_request('/0/private/ClosedOrders', {"nonce": str(int(1000 * time.time()))}, api_key, api_sec)
    orders = json.loads(resp.content)

    coin_tester= market.split('/')
    if coin_tester[0]=='BTC':
        coin_tester[0]='XBT'
    ref_coin=coin_tester[0]+coin_tester[1]

    if coin_tester[1]=='USD':


        # For USD
        for entry in orders['result']['closed']:
            trade=orders['result']['closed'][entry]
            close_time=float(trade['closetm'])*1000
            descr=trade['descr']
            if close_time<=to_date and close_time>=since_date:
                if ref_coin==descr['pair'] and descr['type']=='sell':
                    usd_sells.append({'amount': float(trade['vol']), 'cost': float(trade['cost']),'id':entry,'date':str(datetime.fromtimestamp(trade['closetm'])),'side':descr['type'],'price':float(trade['price']),'status':'closed'})

                elif ref_coin==descr['pair'] and descr['type']=='buy':
                    usd_buys.append({'amount': float(trade['vol']), 'cost': float(trade['cost']),'id':entry,'date':str(datetime.fromtimestamp(trade['closetm'])),'side':descr['type'],'price':float(trade['price']),'status':'closed'})



    if coin_tester[1]=='USDT':
        for entry in orders['result']['closed']:
            trade = orders['result']['closed'][entry]
            close_time = float(trade['closetm']) * 1000
            descr = trade['descr']
            if close_time <= to_date and close_time>=since_date:
                if ref_coin == descr['pair'] and descr['type'] == 'sell':
                    usdt_sells.append({'amount': float(trade['vol']), 'cost': float(trade['cost']), 'id': entry,
                                      'date': str(datetime.fromtimestamp(trade['closetm'])), 'side': descr['type'],
                                      'price': float(trade['price']), 'status': 'closed'})

                elif ref_coin == descr['pair'] and descr['type'] == 'buy':
                    usdt_buys.append({'amount': float(trade['vol']), 'cost': float(trade['cost']), 'id': entry,
                                     'date': str(datetime.fromtimestamp(trade['closetm'])), 'side': descr['type'],
                                     'price': float(trade['price']), 'status': 'closed'})

    if coin_tester[1]=='USDC':

        for entry in orders['result']['closed']:
            trade = orders['result']['closed'][entry]
            close_time = float(trade['closetm']) * 1000
            descr = trade['descr']
            if close_time <= to_date and close_time>=since_date:
                if ref_coin == descr['pair'] and descr['type'] == 'sell':
                    usdc_sells.append({'amount': float(trade['vol']), 'cost': float(trade['cost']), 'id': entry,
                                      'date': str(datetime.fromtimestamp(trade['closetm'])), 'side': descr['type'],
                                      'price': float(trade['price']), 'status': 'closed'})

                elif ref_coin == descr['pair'] and descr['type'] == 'buy':
                    usdc_buys.append({'amount': float(trade['vol']), 'cost': float(trade['cost']), 'id': entry,
                                     'date': str(datetime.fromtimestamp(trade['closetm'])), 'side': descr['type'],
                                     'price': float(trade['price']), 'status': 'closed'})

    account_book = {'usd_sells': usd_sells, 'usd_buys': usd_buys, 'usdt_sells': usdt_sells, 'usdt_buys': usdt_buys,
                    'usdc_sells': usdc_sells, 'usdc_buys': usdc_buys}

    return account_book



def get_bitfinex_transactions(market,since_date,to_date ):



    usd_buys = []
    usd_sells = []
    usdt_buys = []
    usdt_sells = []

    api_key = os.getenv("BITFINEX_API_KEY")
    api_sec = os.getenv("BITFINEX_API_SECRET")


    bitfinex = cx.bitfinex2({
        'apiKey': api_key,
        'secret': api_sec,
    })


    coin_tester = market.split('/')[1]


    # For USD
    if coin_tester=='USD':
        usd_trades=bitfinex.fetch_closed_orders(market,since=since_date)

        for trade in usd_trades:
            if trade['status']=='closed'and  trade['timestamp'<=to_date]:
                if trade['side'] == 'sell':
                    usd_sells.append({'amount': float(trade['amount']), 'cost': float(trade['cost']),'id':trade['id'],'date':str(trade['datetime']),'side':trade['side'],'price':trade['price'],'status':trade['status'] })

                elif trade['side'] == 'buy':
                    usd_buys.append({'amount': float(trade['amount']), 'cost': float(trade['cost']),'id':trade['id'],'date':str(trade['datetime']),'side':trade['side'],'price':trade['price'],'status':trade['status'] })


    # For USDT
    if coin_tester=='USDT':
        usdt_trades=bitfinex.fetch_closed_orders(market,since=since_date)

        for trade in usdt_trades:
            if trade['status']=='closed'and  trade['timestamp'<=to_date]:
                if trade['side'] == 'sell':
                    usdt_sells.append({'amount': float(trade['amount']), 'cost': float(trade['cost']),'id':trade['id'],'date':str(trade['datetime']),'side':trade['side'],'price':trade['price'],'status':trade['status'] })

                elif trade['side'] == 'buy':
                    usdt_buys.append({'amount': float(trade['amount']), 'cost': float(trade['cost']),'id':trade['id'],'date':str(trade['datetime']),'side':trade['side'],'price':trade['price'],'status':trade['status'] })



    account_book = {'usd_sells': usd_sells, 'usd_buys': usd_buys, 'usdt_sells': usdt_sells, 'usdt_buys': usdt_buys}

    return account_book



def get_balance(market, exchange, since_date,to_date):

    coin_tester=market.split('/')[1]
    usd_balance_book=[]
    usdt_balance_book=[]
    usdc_balance_book=[]
    total_usd_sells=[]
    total_usd_buys=[]
    total_usdt_sells = []
    total_usdt_buys = []
    total_usdc_sells = []
    total_usdc_buys = []

    # Step 0: Add up all the transactions from the diffferent exchanges



    if 'coinbase' in exchange:
        try:
            coinbase=get_coinbase_transactions(market=market,since_date=since_date,to_date=to_date)
            total_usd_sells +=coinbase['usd_sells']
            total_usd_buys += coinbase['usd_buys']
            total_usdt_sells += coinbase['usdt_sells']
            total_usdt_buys += coinbase['usdt_buys']
            total_usdc_sells += coinbase['usdc_sells']
            total_usdc_buys += coinbase['usdc_buys']
        except:
            return f"{market} piyasa Coinbase'de mevcut değil"

    if 'kraken' in exchange:

        try:
            kraken=get_kraken_transactions(market=market,since_date=since_date,to_date=to_date)
            total_usd_sells +=kraken['usd_sells']
            total_usd_buys += kraken['usd_buys']
            total_usdt_sells += kraken['usdt_sells']
            total_usdt_buys += kraken['usdt_buys']
            total_usdc_sells += kraken['usdc_sells']
            total_usdc_buys += kraken['usdc_buys']
        except:
            return f"{market} piyasa Kraken'de mevcut değil"

    if 'bitfinex' in exchange:

        try:
            bitfinex=get_bitfinex_transactions(market=market,since_date=since_date,to_date=to_date)
            total_usd_sells +=bitfinex['usd_sells']
            total_usd_buys += bitfinex['usd_buys']
            total_usdt_sells += bitfinex['usdt_sells']
            total_usdt_buys += bitfinex['usdt_buys']
        except:
            return f"{market} piyasa Bitfinex'te mevcut değil"







    #Step 1: Take matching sell and buy orders and append them to a seperate list


    #USD
    if coin_tester == 'USD':
        for sell in total_usd_sells:
            for buy in total_usd_buys:
                # Get the index
                buy_index = total_usd_buys.index(buy)
                if sell['amount'] == buy['amount']:
                    proift = sell['cost'] - buy['cost']
                    # append to balance book
                    usd_balance_book.append({'sell': sell, 'buy': buy, 'profit': proift,'remaining_amount':0, 'side':None,'status':sell['status']})
                    # Delete element in the buys list
                    del total_usd_buys[buy_index]
                    break

    #USDT
    elif coin_tester == 'USDT':
        for sell in total_usdt_sells:
            for buy in total_usdt_buys:
                # Get the index
                buy_index = total_usdt_buys.index(buy)
                if sell['amount'] == buy['amount']:
                    proift = sell['cost'] - buy['cost']
                    # append to balance book
                    usdt_balance_book.append({'sell': sell, 'buy': buy, 'profit': proift,'remaining_amount':0,'side':None,'status':sell['status']})
                    # Delete element in the buys list
                    del total_usdt_buys[buy_index]
                    break

    #USDC
    elif coin_tester == 'USDC':
        if 'coinbase' in exchange or 'kraken' in exchange:

            for sell in total_usdc_sells:
                for buy in total_usdc_buys:
                    # Get the index
                    buy_index = total_usdc_buys.index(buy)
                    if sell['amount'] == buy['amount']:
                        proift = sell['cost'] - buy['cost']
                        # append to balance book
                        usdc_balance_book.append({'sell': sell, 'buy': buy, 'profit': proift,'remaining_amount':0,'side':None,'status':sell['status']})
                        # Delete the buy entry
                        del total_usdc_buys[buy_index]
                        break



    #Step 2: delete the matchig sells from the sell list

    # USD
    if coin_tester=='USD':
        for balance in usd_balance_book:
            for sell in total_usd_sells:
                # Get the index for the sell book
                sell_index = total_usd_sells.index(sell)
                if balance['sell'] == sell:
                    # Delete the sell entry
                    del total_usd_sells[sell_index]
                    break


    # USDT
    elif coin_tester == 'USDT':
        for balance in usdt_balance_book:
            for sell in total_usdt_sells:
                # Geet the index for the sell book
                sell_index = total_usdt_sells.index(sell)
                if balance['sell'] == sell:
                    # Delete the sell entry
                    del total_usdt_sells[sell_index]
                    break


    # USDC
    elif coin_tester == 'USDC':
        for balance in usdc_balance_book:
            for sell in total_usdc_sells:
                # Geet the index for the sell book
                sell_index = total_usdc_sells.index(sell)
                if balance['sell'] == sell:
                    # Delete the sell entry
                    del total_usdc_sells[sell_index]
                    break



    # Step 3: Itirate through each list and subtract common transactions forming new trnasaction in the proccess

    #USD
    if coin_tester=='USD':
        usd_loop_check = True
        while usd_loop_check == True:

            for sell in total_usd_sells:
                for buy in total_usd_buys:
                    # get the buy index
                    buy_index = total_usd_buys.index(buy)

                    if sell['amount'] > buy['amount']:
                        proift = (sell['cost'] * buy['amount']) / sell['amount'] - buy['cost']
                        # Calculate new sell transaction
                        new_sell_amount = sell['amount'] - buy['amount']
                        new_sell_cost = (sell['cost'] / sell['amount']) * new_sell_amount
                        balance_book_sell_cost = (sell['cost'] / sell['amount']) * buy['amount']

                        # Append transaction to balance book
                        usd_balance_book.append(
                            {'sell': {'amount': buy['amount'], 'cost': balance_book_sell_cost,'id':sell['id'],'date':sell['date'],'price':sell['price']},'side':sell['side'],
                             'remaining_amount':new_sell_amount,'buy': buy,'profit': proift,'status':buy['status']})

                        # Delete the buy transaction
                        del total_usd_buys[buy_index]
                        # Replace the current sell transaction with a new one
                        sell['amount'] = new_sell_amount
                        sell['cost'] = new_sell_cost
                        break


            for buy in total_usd_buys:
                for sell in total_usd_sells:
                    # Get the index
                    sell_index = total_usd_sells.index(sell)

                    if sell['amount'] < buy['amount'] :
                        profit = sell['cost'] - (buy['cost'] * sell['amount']) / buy['amount']
                        # Calculate new buy transaction
                        new_buy_amount = buy['amount'] - sell['amount']
                        new_buy_cost = (buy['cost'] / buy['amount']) * new_buy_amount
                        balance_book_buy_cost = (buy['cost'] / buy['amount']) * sell['amount']

                        # Append transaction to balance book
                        usd_balance_book.append(
                            {'sell': sell, 'buy': {'amount': sell['amount'], 'cost': balance_book_buy_cost,'id':buy['id'],'date':buy['date'],'price':buy['price']},'side':buy['side'],
                             'profit': profit,'remaining_amount':new_buy_amount,'status':buy['status']})

                        # Delete the sell transaction
                        del total_usd_sells[sell_index]
                        # Replace the current buy transaction with a new one
                        buy['amount'] = new_buy_amount
                        buy['cost'] = new_buy_cost
                        break

            if len(total_usd_sells) == 0 or len(total_usd_buys) == 0:
                usd_loop_check = False


        #append the leftover orders into the balance book

        for sell in total_usd_sells:
            usd_balance_book.append({'buy': {'amount': None, 'cost': None, 'id': None, 'date': None,'side': None,
                                             'price': None}, 'sell': sell, 'profit': 0,'remaining_amount': sell['amount'], 'side': sell['side'],'status': sell['status']})


        for buy in total_usd_buys:
            usd_balance_book.append({'sell': {'amount': None, 'cost': None, 'id': None, 'date': None,'side': None,
                                             'price': None}, 'buy': buy, 'profit': 0,'remaining_amount': buy['amount'], 'side': buy['side'],'status': buy['status']})



    #USDT
    elif coin_tester == 'USDT':
        usdt_loop_check = True
        while usdt_loop_check == True:

            for sell in total_usdt_sells:
                for buy in total_usdt_buys:
                    # get the buy index
                    buy_index = total_usdt_buys.index(buy)
                    ###########
                    if sell['amount'] > buy['amount']:
                        proift = (sell['cost'] * buy['amount']) / sell['amount'] - buy['cost']
                        # Calculate new sell transaction
                        new_sell_amount = sell['amount'] - buy['amount']
                        new_sell_cost = (sell['cost'] / sell['amount']) * new_sell_amount
                        balance_book_sell_cost = (sell['cost'] / sell['amount']) * buy['amount']

                        # Append transaction to balance book
                        usdt_balance_book.append(
                            {'sell': {'amount': buy['amount'], 'cost': balance_book_sell_cost, 'id': sell['id'],'date': sell['date'], 'price': sell['price']},'side': sell['side'],
                             'remaining_amount': new_sell_amount, 'buy': buy, 'profit': proift,'status':buy['status']})

                        # Delete the buy transaction
                        del total_usdt_buys[buy_index]
                        # Replace the current sell transaction with a new one
                        sell['amount'] = new_sell_amount
                        sell['cost'] = new_sell_cost
                        break


            for buy in total_usdt_buys:
                for sell in total_usdt_sells:
                    # Get the index
                    sell_index = total_usdt_sells.index(sell)

                    if sell['amount'] < buy['amount'] :

                        proift = sell['cost'] - (buy['cost'] * sell['amount']) / buy['amount']
                        # Calculate new buy transaction
                        new_buy_amount = buy['amount'] - sell['amount']
                        new_buy_cost = (buy['cost'] / buy['amount']) * new_buy_amount
                        balance_book_buy_cost = (buy['cost'] / buy['amount']) * sell['amount']

                        # Append transaction to balance book
                        usdt_balance_book.append(
                            {'sell': sell,'buy': {'amount': sell['amount'], 'cost': balance_book_buy_cost, 'id': buy['id'],
                            'date': buy['date'], 'price': buy['price']},'side': buy['side'],'profit': proift, 'remaining_amount': new_buy_amount,'status':sell['status'] })

                        # Delete the sell transaction
                        del total_usdt_sells[sell_index]
                        # Replace the current buy transaction with a new one
                        buy['amount'] = new_buy_amount
                        buy['cost'] = new_buy_cost
                        break

            if len(total_usdt_sells) == 0 or len(total_usdt_buys) == 0:
                usdt_loop_check = False

                # append the leftover orders into the balance book

            for sell in total_usdt_sells:
                usdt_balance_book.append({'buy': {'amount': None, 'cost': None, 'id': None, 'date': None, 'side': None,
                                                 'price': None}, 'sell': sell, 'profit': 0,
                                         'remaining_amount': sell['amount'], 'side': sell['side'],
                                         'status': sell['status']})

            for buy in total_usdt_buys:
                usdt_balance_book.append({'sell': {'amount': None, 'cost': None, 'id': None, 'date': None, 'side': None,
                                                  'price': None}, 'buy': buy, 'profit': 0,
                                         'remaining_amount': buy['amount'], 'side': buy['side'],
                                         'status': buy['status']})


    #USDC
    elif coin_tester == 'USDC':
        usdc_loop_check = True
        while usdc_loop_check == True:

            for sell in total_usdc_sells:
                for buy in total_usdc_buys:
                    # get the buy index
                    buy_index = total_usdc_buys.index(buy)
                    if sell['amount'] > buy['amount']:

                        proift = (sell['cost'] * buy['amount']) / sell['amount'] - buy['cost']
                        # Calculate new sell transaction
                        new_sell_amount = sell['amount'] - buy['amount']
                        new_sell_cost = (sell['cost'] / sell['amount']) * new_sell_amount
                        balance_book_sell_cost = (sell['cost'] / sell['amount']) * buy['amount']

                        # Append transaction to balance book
                        usdc_balance_book.append(
                            {'sell': {'amount': buy['amount'], 'cost': balance_book_sell_cost, 'id': sell['id'],'date': sell['date'], 'price': sell['price']},'side': sell['side'],
                             'remaining_amount': new_sell_amount, 'buy': buy, 'profit': proift})

                        # Delete the buy transaction
                        del total_usdc_buys[buy_index]
                        # Replace the current sell transaction with a new one
                        sell['amount'] = new_sell_amount
                        sell['cost'] = new_sell_cost
                        break

            for buy in total_usdc_buys:
                for sell in total_usdc_sells:
                    # Get the index
                    sell_index = total_usdc_sells.index(sell)

                    if sell['amount'] < buy['amount'] :

                        proift = sell['cost'] - (buy['cost'] * sell['amount']) / buy['amount']
                        # Calculate new buy transaction
                        new_buy_amount = buy['amount'] - sell['amount']
                        new_buy_cost = (buy['cost'] / buy['amount']) * new_buy_amount
                        balance_book_buy_cost = (buy['cost'] / buy['amount']) * sell['amount']

                        # Append transaction to balance book
                        usdc_balance_book.append(
                            {'sell': sell,'buy': {'amount': sell['amount'], 'cost': balance_book_buy_cost, 'id': buy['id'],
                            'date': buy['date'], 'price': buy['price'] },'side': buy['side'], 'profit': proift,'remaining_amount': new_buy_amount, })


                        # Delete the sell transaction
                        del total_usdc_sells[sell_index]
                        # Replace the current buy transaction with a new one
                        buy['amount'] = new_buy_amount
                        buy['cost'] = new_buy_cost
                        break

            if len(total_usdc_sells) == 0 or len(total_usdc_buys) == 0:
                usdc_loop_check = False


                # append the leftover orders into the balance book

            for sell in total_usdc_sells:
                usdc_balance_book.append({'buy': {'amount': None, 'cost': None, 'id': None, 'date': None, 'side': None,
                                                 'price': None}, 'sell': sell, 'profit': 0,
                                         'remaining_amount': sell['amount'], 'side': sell['side'],
                                         'status': sell['status']})

            for buy in total_usdc_buys:
                usdc_balance_book.append({'sell': {'amount': None, 'cost': None, 'id': None, 'date': None, 'side': None,
                                                  'price': None}, 'buy': buy, 'profit': 0,
                                         'remaining_amount': buy['amount'], 'side': buy['side'],
                                         'status': buy['status']})




    #Step 4: get the total profits


    # USD
    if coin_tester=='USD':
        total_usd_profits = 0
        for transaction in usd_balance_book:
            total_usd_profits += transaction['profit']

    #USDT
    if coin_tester=='USDT':
        total_usdt_profits = 0
        for transaction in usdt_balance_book:
            total_usdt_profits += transaction['profit']


    ##USDC
    if coin_tester == 'USDC':
        total_usdc_profits = 0
        for transaction in usdc_balance_book:
            total_usdc_profits += transaction['profit']


    # Step 5: Append balances to new lists


    #USD
    if coin_tester=='USD':

        usd_buy_amount = []
        usd_buy_cost = []
        usd_sell_amount = []
        usd_sell_cost = []
        usd_remaining_amount=[]
        usd_sell_date=[]
        usd_buy_date=[]
        usd_sell_price = []
        usd_buy_price = []
        usd_sell_id = []
        usd_buy_id = []
        side=[]
        status=[]
        usd_profit_balances = []


        for balance in usd_balance_book:
            usd_buy_amount.append(balance['buy']['amount'])
            usd_buy_cost.append(balance['buy']['cost'])
            usd_sell_amount.append(balance['sell']['amount'])
            usd_sell_cost.append(balance['sell']['cost'])
            usd_profit_balances.append(balance['profit'])
            usd_remaining_amount.append(balance['remaining_amount'])
            usd_sell_date.append(balance['sell']['date'])
            usd_buy_date.append(balance['buy']['date'])
            usd_sell_price.append(balance['sell']['price'])
            usd_buy_price.append(balance['buy']['price'])
            usd_sell_id.append(balance['sell']['id'])
            usd_buy_id.append(balance['buy']['id'])
            side.append(balance['side'])
            status.append(balance['status'])



        usd_buy_amount.append('')
        usd_buy_cost.append('')
        usd_sell_amount.append('')
        usd_sell_cost.append('')
        usd_remaining_amount.append('')
        usd_sell_date.append('')
        usd_buy_date.append('')
        usd_sell_price.append('')
        usd_buy_price.append('')
        usd_sell_id.append('Total Profit')
        usd_buy_id.append('')
        side.append('')
        status.append('')
        usd_profit_balances.append(total_usd_profits)

        usd_book = {' Buy amount': usd_buy_amount,'Sell amount': usd_sell_amount, ' Buy cost': usd_buy_cost,'Sell cost': usd_sell_cost,
                    'Buy price':usd_buy_price,'Sell price':usd_sell_price,'Remaining amount':usd_remaining_amount,'Side':side,'Status':status,'Buy date':usd_buy_date,
                    'Sell date':usd_sell_date,'Buy ID':usd_buy_id,'Sell ID':usd_sell_id,'Profit': usd_profit_balances}

        usd_df = pd.DataFrame(usd_book)
        return usd_df


    #USDT
    elif coin_tester=='USDT':


        usdt_buy_amount = []
        usdt_buy_cost = []
        usdt_sell_amount = []
        usdt_sell_cost = []
        usdt_remaining_amount=[]
        usdt_sell_date=[]
        usdt_buy_date=[]
        usdt_sell_price = []
        usdt_buy_price = []
        usdt_sell_id = []
        usdt_buy_id = []
        side=[]
        status=[]
        usdt_profit_balances = []


        for balance in usdt_balance_book:
            usdt_buy_amount.append(balance['buy']['amount'])
            usdt_buy_cost.append(balance['buy']['cost'])
            usdt_sell_amount.append(balance['sell']['amount'])
            usdt_sell_cost.append(balance['sell']['cost'])
            usdt_profit_balances.append(balance['profit'])
            usdt_remaining_amount.append(balance['remaining_amount'])
            usdt_sell_date.append(balance['sell']['date'])
            usdt_buy_date.append(balance['buy']['date'])
            usdt_sell_price.append(balance['sell']['price'])
            usdt_buy_price.append(balance['buy']['price'])
            usdt_sell_id.append(balance['sell']['id'])
            usdt_buy_id.append(balance['buy']['id'])
            side.append(balance['side'])
            status.append(balance['status'])



        usdt_buy_amount.append('')
        usdt_buy_cost.append('')
        usdt_sell_amount.append('')
        usdt_sell_cost.append('')
        usdt_remaining_amount.append('')
        usdt_sell_date.append('')
        usdt_buy_date.append('')
        usdt_sell_price.append('')
        usdt_buy_price.append('')
        usdt_sell_id.append('Total Profit')
        usdt_buy_id.append('')
        side.append('')
        status.append('')
        usdt_profit_balances.append(total_usdt_profits)

        usdt_book = {' Buy amount': usdt_buy_amount,'Sell amount': usdt_sell_amount, ' Buy cost': usdt_buy_cost,'Sell cost': usdt_sell_cost,
                    'Buy price':usdt_buy_price,'Sell price':usdt_sell_price,'Remaining amount':usdt_remaining_amount,'Side':side,'Status':status,'Buy date':usdt_buy_date,
                    'Sell date':usdt_sell_date,'Buy ID':usdt_buy_id,'Sell ID':usdt_sell_id,'Profit': usdt_profit_balances}

        usdt_df = pd.DataFrame(usdt_book)
        return usdt_df


    #USDC
    elif coin_tester=='USDC':


        usdc_buy_amount = []
        usdc_buy_cost = []
        usdc_sell_amount = []
        usdc_sell_cost = []
        usdc_remaining_amount=[]
        usdc_sell_date=[]
        usdc_buy_date=[]
        usdc_sell_price = []
        usdc_buy_price = []
        usdc_sell_id = []
        usdc_buy_id = []
        side=[]
        status=[]
        usdc_profit_balances = []


        for balance in usdc_balance_book:
            usdc_buy_amount.append(balance['buy']['amount'])
            usdc_buy_cost.append(balance['buy']['cost'])
            usdc_sell_amount.append(balance['sell']['amount'])
            usdc_sell_cost.append(balance['sell']['cost'])
            usdc_profit_balances.append(balance['profit'])
            usdc_remaining_amount.append(balance['remaining_amount'])
            usdc_sell_date.append(balance['sell']['date'])
            usdc_buy_date.append(balance['buy']['date'])
            usdc_sell_price.append(balance['sell']['price'])
            usdc_buy_price.append(balance['buy']['price'])
            usdc_sell_id.append(balance['sell']['id'])
            usdc_buy_id.append(balance['buy']['id'])
            side.append(balance['side'])
            status.append(balance['status'])

        usdc_buy_amount.append('')
        usdc_buy_cost.append('')
        usdc_sell_amount.append('')
        usdc_sell_cost.append('')
        usdc_remaining_amount.append('')
        usdc_sell_date.append('')
        usdc_buy_date.append('')
        usdc_sell_price.append('')
        usdc_buy_price.append('')
        usdc_sell_id.append('Total Profit')
        usdc_buy_id.append('')
        side.append('')
        status.append('')
        usdc_profit_balances.append(total_usdc_profits)

        usdc_book = {' Buy amount': usdc_buy_amount,'Sell amount': usdc_sell_amount, ' Buy cost': usdc_buy_cost,'Sell cost': usdc_sell_cost,
                    'Buy price':usdc_buy_price,'Sell price':usdc_sell_price,'Remaining amount':usdc_remaining_amount,'Side':side,'Status':status,'Buy date':usdc_buy_date,
                    'Sell date':usdc_sell_date,'Buy ID':usdc_buy_id,'Sell ID':usdc_sell_id,'Profit': usdc_profit_balances}

        usdc_df = pd.DataFrame(usdc_book)
        return usdc_df




