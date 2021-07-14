
from binanceApi import binanceLib
from binance_f import RequestClient
from binance_f.constant.test import *
from binance_f.base.printobject import *
from binance_f.model.constant import *
from datetime import datetime
from decimal import *
from decimal import Decimal
from flask import Flask
from flask_cors import CORS
from multiprocessing import Process, Value
import math
import time
import sys, os
import logging
import json
# from bot import BinanceApi
from bot_v2 import *
import csv

app = Flask(__name__)
cors = CORS(app, resource={r"/*":{"origins": "*"}})

key = os.environ.get('API_KEY')
secret = os.environ.get('API_SECRET')
coin = os.environ.get('COIN')
minimalQtd = os.environ.get('MINIMAL_COIN_BUY')
# minimalProfit = os.environ.get('MINIMAL_PROFIT_USD')
# leverage = os.environ.get('COIN_LEVERAGE')
minimalMove = os.environ.get('COIN_MIN_MOVE')
# status = BotStatus.SELL
#
# if status == BotStatus.BUY:
#     print(status)

# --------------------------- Tesnet API Keys -------------------------------------------

g_api_key = '9ed2810f070aa3c9378af0a828cdc46c6a20a347f9c80004e37a26f5d373e3b5'
g_secret_key = 'c2340bebf086e113b6e3bd52f5bd17ccb201649a8f2b82804dec531a7fb16b0f'

# --------------------------- Init Client -------------------------------------------
try:
    # request_client = RequestClient(api_key=key, secret_key=secret, url='https://testnet.binancefuture.com/')
    request_client = RequestClient(api_key=key, secret_key=secret,  url='https://fapi.binance.com')
    # request_client = RequestClient(api_key=g_api_key, secret_key=g_secret_key, url='https://testnet.binancefuture.com/')
except Exception as e:
    print("ERROR: Connecting to client")
else:
    print("INFO: Connected to client")

api = binanceLib(client = request_client)

balance = api.get_usdt_balance()
balance = balance * 0.035
print(balance)
bot = Strategy(name=coin, percentage=0.005 , balance=balance,minTradeAmount=minimalQtd, minPriceMove=minimalMove,binanceApi = api)


# try:
#
#     close = numpy.random.random(100)
#     print(close)
#     moving_average = talib.RSI(close)
#
#     print(moving_average)
# except Exception as e:
#     print("EROOR")

# This function provides utility functions to work with Strings
# 1. reverse(s): returns the reverse of the input string
# 2. print(s): prints the string representation of the input object
def get_data_to_backtest():
    data = []
    #
    # with open('ADAUSDT-1m-2021-05.csv', newline='') as csvfile:
    #     spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    #     for row in spamreader:
    #         teste = str(row).split(",")
    #         data.append(teste[2])

    # print(lists_from_csv)
    sys.stdout = open(os.devnull, 'w')
    data = request_client.get_candlestick_data(symbol='BTCUSDT', interval=CandlestickInterval.MIN1, startTime=None,endTime=None,limit=1000)
    sys.stdout = sys.__stdout__
    return data

def record_loop_v2():
    global api,bot

    lastTime = 0
    while (True):
        try:
            currentTime = datetime.now().minute
            if currentTime != lastTime:
                if (currentTime % 1) == 0:
                    # get server time to check if server is connected
                    serverTime =  api.get_server_time()
                    if serverTime != 0:
                        lastTime = currentTime

                        # check if are open positions
                        position = api.get_open_positions(bot.name)
                        # if positio is equal to zero we need to init bot
                        if position[0] == 0:
                            # clear all open orders
                            api.cancel_all_orders(bot.name)
                            # init bot status
                            if bot.status == BotStatus.PLACEORDERBUY:
                                bot.status = BotStatus.PLACEORDERFIRSTBUY
                            elif bot.status == BotStatus.PLACEORDERSELL:
                                bot.status = BotStatus.PLACEORDERFIRSTSELL
                            else:
                                bot.status = BotStatus.NOTDEFINED

                        else:
                            #check all open orders
                            orders = api.get_open_orders(bot.name)
                            #check profit open positons
                            if orders[0] == 0:
                                api.cancel_all_orders(bot.name)
                                # check if is a sell or buy position
                                if position[0] > 0:
                                    bot.status = BotStatus.ORDERBUYCONTROL
                                    #buy position
                                    profit = Decimal(position[1] * (1+0.005))
                                    profit = Decimal(profit.quantize(Decimal(str(bot.minPriceMove)), rounding=ROUND_HALF_UP))
                                    api.post_buy_order_profit(bot.name,position[0],profit)
                                else:
                                    bot.status = BotStatus.ORDERSELLCONTROL
                                    #sell position
                                    profit = Decimal(position[1] * (1-0.005))
                                    profit = Decimal(profit.quantize(Decimal(str(bot.minPriceMove)), rounding=ROUND_HALF_UP))
                                    api.post_sell_order_profit(bot.name, position[0] * (-1), profit)


                        price = api.get_price_min1(bot.name)
                        # check if there is no open positions
                        bot.process_coin_price_V2(price = price)

                    else:
                        try:
                            request_client = RequestClient(api_key=g_api_key, secret_key=g_secret_key,
                                                           url='https://testnet.binancefuture.com/')
                        except Exception as e:
                            print(e)
                            print("ERROR: restarting client")
                        else:
                            print("INFO: Cient restarted")
                        #
                        # process_coin_price

        except Exception as e:
            print(e)

# def record_loop():
#     global request_client
#
#     backtest.init_strategy()
#
#     current = 0
#     while (True):
#         try:
#             dataNow = datetime.now().minute
#             # check the server connection
#             if dataNow != current:
#                 if (dataNow % 5) == 0:
#                     result = backtest.get_servertime()
#
#                     if result != 0:
#                         current = dataNow
#
#                         backtest.positionSize = 0
#
#                         backtest.get_open_positions(backtest.coin)
#                         backtest.get_open_orders()
#
#                         if backtest.positionSize == 0:
#                             backtest.buyStatus = 0
#                         backtest.process_Price()
#                         print("INFO: Bot -> ON ")
#
#                     else:
#                         try:
#                             request_client = RequestClient(api_key=g_api_key, secret_key=g_secret_key,
#                                                        url='https://testnet.binancefuture.com/')
#                         except Exception as e:
#                             print(e)
#                             print("ERROR: restarting client")
#                         else:
#                             print("INFO: Cient restarted")
#
#         except Exception as e:
#             print(e)
#
#     # This function provides utility functions to work with Strings
#     # 1. reverse(s): returns the reverse of the input string
#     # 2. print(s): prints the string representation of the input object



@app.route("/", methods=['GET'])
def index():
    return "<h1>Hello World!</h1>"

    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object
def main():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object


if __name__ == '__main__':

    # binLib = binanceLib(client = request_client)
    # teste = 1.3
    # teste = Decimal(teste)
    #
    # teste = Decimal(teste.quantize(Decimal('0'), rounding=ROUND_HALF_UP))

    # print(teste)
  # data = get_data_to_backtest()
  #   teste = request_client.get_balance_v2()
    # coin =
    # result = request_client.get_position()
    # position = binLib.get_open_positions('BTCUSDT')
    # price = api.get_price_min1(cryptoCoin='BTCUSDT')


    # orders = api.get_open_orders(bot.name)
    # print(orders)
    # res = binLib.set_leverage("ALPHAUSDT",15)
    #
    # if res:
    #     print("OK")
    # else:
    #     print("NOK")
    # result = binLib.get_usdt_balance()
    # print(orders)
    # for()
    #
    # strategy = Strategy(name='ALPHAUSDT',data=data,balance=1.0, percentage=0.005,minTradeAmount=1.0,minPriceMove=0.001)

    # strategy.status = BotStatus.NOTDEFINED
    # print(vars(teste))
    #  print(vars(data[0]))
    # print(result)

    #     # strategy.process_coin_price(dt.close)
    #     strategy.process_coin_price(dt.close)
    #     # strategy.process_coin_price_V2(dt)

    p = Process(target=record_loop_v2)
    p.start()
    main()
    p.join()
    # p = Process(target=record_loop)
    # p.start()
    # main()
    # p.join()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
