api_secret = input ('input your api secret: ')
api_key = input ('input your api key: ')

from binance.client import Client
import numpy as np
import datetime
import math
from binance.exceptions import BinanceAPIException
import time
from Test2 import simple_get
from bs4 import BeautifulSoup
from threading import Thread
from prettytable import PrettyTable as tb
from os import system, name

recvWindow = 1000000  # the number of milliseconds the request is valid for
basket = float (input ('Your Trading Asset (%): '))  # درصدی از سرمایه تان را که می خواهید با آن خرید و فروش کنید
profitex = float (input ('profit you need for each trade (%): '))  # حد سود (برحسب درصد) که مایلید در آن، ارز خود را بفروشید
sl = float (input ('stoploss at each trade (%): '))  # حد ضرر (برحسب سود) که مایلید در آن ارز خود را بفروشید
wtime = int (input ('input the time(in minuts) you want to wait for selling: ')) * 60
market = input ('Market: ').upper ()  # در اینجا مارکت خودتون رو مشخص کنید و داحل '' قرار بدید

def clprint(strs, table) :
    # for windows
    if name == 'nt' :
        _ = system ('cls')

        # for mac and linux(here, os.name is 'posix')
    else :
        _ = system ('clear')
    # table.sortby = table.field_names[0]
    table.del_row (0)
    table.add_row (strs)
    # table.sortby = table.field_names[0]
    print (table.get_string (title="coins" + str (syms[0 :divider])))
def Trade(sym) :
    table = tb ()
    table.field_names = ['No', 'pair', 'buy order', 'buy status', 'sell order', 'sell status', 'last price',
                         'stoploss or time limit', 'profit %']
    num = syms.index (sym)
    table.add_row ([str (num), sym, '', '', '', '', '', '', ''])
    buy_order = str (last_price (sym, pr=0))
    number_of_coins = num_coin (half_bitcoins, buy_order, sym)

    try :
        now = datetime.datetime.now ()
        buy_time = time.ctime (time.time ())
        client.order_market_buy (symbol=sym, quantity=number_of_coins, recvWindow=recvWindow)
        bought_price = client.get_my_trades (symbol=sym, limit=1)[0]['price']
        (ncoins, profit, tdigits, digits) = find_quantity (half_bitcoins, bought_price, sym)
        tdigits = int (tdigits)
        digits = int (digits)
        time.sleep (1)
        clprint ([str (num), sym, 'placed', 'completed', '', '', '', '', ''], table)
        sell_quantity = round_down ((0.9995 * number_of_coins), digits)
        condition = False
        n = 0
        while not condition :
            try :
                sell_quantity = sell_quantity - n * (10.0 ** (-digits))
                client.order_limit_sell (symbol=sym, quantity=sell_quantity, price=str (profit), recvWindow=recvWindow)
                condition = True
            except :
                n += 1
                pass
        time.sleep (1)
        clprint ([str (num), sym, 'placed', 'completed', 'palced', '', '', '', ''], table)
        seconds = time.time ()
        percentage = order_confirm_sell (sym, bought_price, tdigits, seconds,profit, num, table)
        return percentage

    except BinanceAPIException as e :
        print (e.status_code)
        print (e.message)
        percentage = 'interruptions'
        winstatus = 'interrputions'
def select_pair(pair_order) :
    candidates = []
    interval2 = Client.KLINE_INTERVAL_1MINUTE
    etime2 = now
    stime2 = etime2 - datetime.timedelta (minutes=mins)
    etime2 = str (etime2)
    stime2 = str (stime2)
    for pair in pair_order :
        try :
            A = client.get_historical_klines_generator (pair, interval2, stime2, etime2)
            A = list (A)
            A = list (map (list, zip (*A)))
            [open, high, low, close] = [A[1], A[2], A[3], A[4]]
            open = list (map (lambda x : float (x), open))
            high = list (map (lambda x : float (x), high))
            low = list (map (lambda x : float (x), low))
            close = list (map (lambda x : float (x), close))
            open = np.array (open)
            high = np.array (high)
            low = np.array (low)
            close = np.array (close)
            if (close[-1] - close[0]) / close[0] >= rise / 100 :
                candidates.append (pair)
            else :
                pass
        except :
            pass
    return candidates
def unselect_pair(syms) :
    symbols = []
    for sym in syms :
        buy_order = last_price (sym, pr=0)
        tdigits = find_digits (client.get_symbol_info (sym)['filters'][0]['tickSize'])
        sprice = stop_loss (buy_order, tdigits)
        buy_order = float(buy_order)
        sprice = float (sprice)
        print(sym , sprice , buy_order)
        if  sprice >= buy_order or abs((sprice - buy_order)/buy_order) > sl:
            pass
        else :
            symbols.append(sym)
    return symbols
def topcoins(n) :
    # get the top n coins at the current moment
    rank_info = simple_get ('https://coinmarketcap.com/all/views/all/')
    rank_soup = BeautifulSoup (rank_info, 'html.parser')
    All_pairs = rank_soup.find ("tbody").find_all ("td", {"class" : "text-left col-symbol"})[:n]
    pair_order = []
    for sym in All_pairs :
        pair_order.append (sym.getText () + market)
    return pair_order
def assetbalance(asset) :
    balance = client.get_asset_balance (asset=asset, recvWindow=recvWindow)
    asset_balance = float (balance['free'])
    return (asset_balance)
def find_quantity(total, price, sym) :
    # find an acceptable value for number of coins
    quantity = float (total) / float (price)
    info = client.get_symbol_info (sym)['filters'][2]['minQty']  # find minQty for sym trade. for ex. min amount of BNB coins for BTC trade is 1.0
    digits = find_digits (info)  # find the number of digits after decimal points that is allowed for trading (find the limit of number of coins fot the trade)
    quantity = round_down (quantity,digits)  # for ex. 1.2356 -->1.23 coins because we might not afford 1.24 (if we use format(qunatity,'.2f')

    percentage = profitex / 100
    tinfo = client.get_symbol_info (sym)['filters'][0]['tickSize']
    tdigits = find_digits (tinfo)
    target = percentage * float (price) + float (price)
    target = round_up (target,
                       tdigits)  # for ex. profit= 0.0000001809 -->0.00000019 because we are allowed to place orders at the maximum of 8 digits
    # if we use format(target,'.8f') we get 0.00000018 and we get no profit
    # in this case we might get more than 0.5% profit in each trade
    tdigits = str (tdigits)
    ndigits = '.' + tdigits + 'f'
    target = format (target, ndigits)

    return (quantity, target, tdigits, digits)
def num_coin(total, price, sym) :
    quantity = float (total) / float (price)
    info = client.get_symbol_info (sym)['filters'][2][
        'minQty']  # find minQty for sym trade. for ex. min amount of BNB coins for BTC trade is 1.0
    digits = find_digits (
        info)  # find the number of digits after decimal points that is allowed for trading (find the limit of number of coins fot the trade)
    quantity = round_down (quantity,
                           digits)  # for ex. 1.2356 -->1.23 coins because we might not afford 1.24 (if we use format(qunatity,'.2f')
    return quantity
def decimal_formatter(number, digits) :
    return format (number, '.' + str (digits) + 'f')
def round_down(num, digits) :
    factor = 10.0 ** digits
    return math.floor (num * factor) / factor
def round_up(num, digits) :
    factor = 10 ** digits
    return math.ceil (num * factor) / factor
def find_digits(info) :
    dig = float (info)
    x = dig - int (dig)
    if x == 0 :
        digits = 0
    else :
        y = str (x)
        if 'e' in y :
            digits = int (y[len (y) - 1])
        else :
            digits = len (y) - 2
    return digits
def last_price(sym, pr) :
    con = True
    while con :
        try :
            klines = client.get_klines (symbol=sym, interval=Client.KLINE_INTERVAL_1MINUTE)
            most_recent = klines.pop ()
            last_closing = most_recent[4]
            if pr == 1 :
                print ("Last close price for {} was {}".format (sym, last_closing))
            else :
                pass
            con = False
            break
        except :
            time.sleep (10)
            continue
    return last_closing
def stop_loss(b_order, tdigits) :
    stop_price = float (b_order) - (sl * float (b_order) / 100)
    target = round_up (stop_price, tdigits)
    tdigits = str (tdigits)
    ndigits = '.' + tdigits + 'f'
    stop_price = format (target, ndigits)
    return stop_price
def calculate_profit_percentage(initial, final) :
    percent = (float (final) - float (initial)) / float (initial) * 100
    return format (percent, '.2f')
def order_confirm_buy(symbol) :
    confirm = False
    buy_status = 1
    while not confirm :
        orders = client.get_open_orders (symbol=symbol, recvWindow=recvWindow)
        time.sleep (1)
        if not orders :
            confirm = True
        else :
            confirm = False
            pass
    print ("The coin {} was bought successfully".format (symbol))
    return buy_status
def order_confirm_sell(symbol, bought_price, tdigits, seconds,profit, num=0, table=tb ()) :
    confirm = False
    stop_limit = stop_loss (bought_price, tdigits)
    while not confirm :
        orders = client.get_open_orders (symbol=symbol, recvWindow=recvWindow)
        time.sleep (1)
        current_price = last_price (symbol, pr=0)
        clprint ([str (num), symbol, 'placed', 'completed', 'palced', '', str (current_price), '', ''], table)
        if not orders :
            confirm = True
        if int (time.time () - seconds) >= wtime or current_price <= stop_limit :
            slstatus = 'Reached'
            clprint (
                [str (num), symbol, 'placed', 'completed', 'palced', 'completed', str (current_price), slstatus, ''],
                table)
            orderId = orders[0]['orderId']
            client.cancel_order (symbol=symbol, orderId=orderId, recvWindow=recvWindow)
            client.order_market_sell (symbol=symbol, quantity=sell_quantity, recvWindow=recvWindow)
            confirm = True
        else :
            slstatus = '-'
    percentage = calculate_profit_percentage (bought_price, profit)
    clprint ([str (num), symbol, 'placed', 'completed', 'palced', 'completed', str (current_price), slstatus,
              str (percentage)], table)
    return percentage

client = Client (api_key, api_secret, {"timeout" : 30})
process1 = True
process2 = True
try :
    while process2 :

        q = input (
            'Do you want to place a buy & sell order manually (m) or do you prefer to let the bot do the job (b)? ').upper ()
        if q == 'M' :
            pair = input ('input your pair like ETHBTC : ').upper ()
            sym = pair
            buy_order = float (input ('Buy price (input 0 to just sell): '))
            tinfo = client.get_symbol_info (pair)['filters'][0]['tickSize']
            tdigits = find_digits (tinfo)
            sell_order = float (input ('Sell price: '))
            if buy_order == 0 :
                price = sell_order
            else :
                price = buy_order
            if pair[-4 :] == 'USDT' :
                price = 1 / price
            else :
                price = decimal_formatter (price, tdigits)

            buy_order = decimal_formatter (buy_order, tdigits)
            sell_order = decimal_formatter (sell_order, tdigits)
            asset = assetbalance (market)
            half_bitcoins = format (asset * basket / 100, '.8f')
            (number_of_coins, profit, tdigits, digits) = find_quantity (half_bitcoins, price, pair)
            tdigits = int (tdigits)
            digits = int (digits)
            if float (buy_order) != 0 :
                client.order_limit_buy (symbol=pair, quantity=number_of_coins, price=buy_order, recvWindow=recvWindow)
                print ('Your buy order is placed. please wait till the bot buy the coin at your price ...')
                order_confirm_buy (pair)
            else :
                pass
            print ("Selling... Please wait...")
            if float (buy_order) != 0 :
                sell_quantity = round_down ((0.9995 * number_of_coins), digits)
                condition = False
                n = 0
                while not condition :
                    try :
                        sell_quantity = sell_quantity - n * (10.0 ** (-digits))
                        client.order_limit_sell (symbol=pair, quantity=sell_quantity, price=str (sell_order),
                                                 recvWindow=recvWindow)
                        condition = True
                    except :
                        n += 1
                        pass
            else :
                sell_quantity = round_down ((0.9995 * float (half_bitcoins)), digits)
                print (sell_quantity)
                client.order_limit_sell (symbol=pair, quantity=sell_quantity, price=str (sell_order),
                                         recvWindow=recvWindow)
            time.sleep (1)
            print (
                'Your sell order is placed. please wait till the bot sell the coin at your price or at stoploss price... ')
            seconds = time.time ()
            order_confirm_sell (pair, buy_order, tdigits, seconds,profit = profit)
            print ("Your trade is done. Let's go for the next trade")
        elif q == 'B' :
            no = int (input ('No of Top Coins: '))  # در اینجا مشخص میکنید که ربات چند ارز بالای جدول را بررسی کند
            mins = int (input (
                'input the time(in minutes) period you want to asses the price rising: '))  # در این جا مدت زمانی که انتظار دارید ارز مورد نظر در آن مدت زمان به اندازه دلخواه رشد کرده باشد را مشخص کنید
            rise = float (input (
                'Rise(%) during the past to trigger the buy: '))  # در اینجا درصدی که یک ارز باید طی مدت زمان تعیین شده در مرحله قبل رشد کرده باشد تا ربات آن را بخرد، مشخص می کنید
            yn = input ('Do you want to buy only the top coin (t) or all potential coins (a): ').upper ()

            while process1 :
                print ('Please wait...')
                pair_order = topcoins (no)
                now = datetime.datetime.now ()
                syms = select_pair (pair_order)
                syms = unselect_pair (syms)

                if syms != [] :
                    print ('coins having potential for growth: ', '\n', syms)
                    asset = assetbalance (market)
                    if yn == 'A' :
                        divider = len (syms)
                    else :
                        divider = 1

                    half_bitcoins = format ((asset * basket / 100) / divider, '.8f')
                    # trades=['Trade({})'.format(x) for x in syms]
                    if __name__ == '__main__' :
                        # pool = Pool (processes=len(trades))
                        # pool.map (goparallel, trades)
                        ths = [Thread (target=Trade, args=(str (x),)) for x in syms[0 :divider]]
                        [process.start () for process in ths]
                        [process.join () for process in ths]
                else :
                    print ('Based on your strategy, No coin is good for buying. please wait ...')
                    pass
            process1 = True
        else :
            print ('Please Type m (Manual trading) or b (Bot trading)')
    process2 = True
except KeyboardInterrupt :
    print ('You wanted to exit. All orders will be cancelled')
    #orders = client.get_open_orders (symbol=sym, recvWindow=recvWindow)
    #orderId = orders[0]['orderId']
    #client.cancel_order (symbol=sym, orderId=orderId, recvWindow=recvWindow)
    raise