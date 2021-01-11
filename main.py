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
import  math
import time
import sys, os
import logging
import bot

app = Flask(__name__)
cors = CORS(app, resource={r"/*":{"origins": "*"}})

key = os.environ.get('API_KEY')
secret = os.environ.get('API_SECRET')


# --------------------------- Tesnet API Keys -------------------------------------------

# g_api_key = '9ed2810f070aa3c9378af0a828cdc46c6a20a347f9c80004e37a26f5d373e3b5'
# g_secret_key = 'c2340bebf086e113b6e3bd52f5bd17ccb201649a8f2b82804dec531a7fb16b0f'

# --------------------------- Init Client -------------------------------------------
try:
    request_client = RequestClient(api_key=key, secret_key=secret,url='https://testnet.binancefuture.com/')
except Exception as e:
    print("ERROR: Connecting to client")
else:
    print("INFO: Connected to client")

# This class provides utility functions to work with Strings
# 1. reverse(s): returns the reverse of the input string
# 2. print(s): prints the string representation of the input object
class back_test_strategy:
    def __init__(self):

        # Trade strategy variables

        self.account = 0
        self.buyPrice = 0
        self.buyPriceType = 0
        self.buyStatus = 0
        self.tradeState = 0
        self.tradeCounter = 0


        # Coin for trading variables
        self.coin = 'BTCUSDT'
        self.price = 0
        self.timestamp = 0
        self.date = 0

        # Account balance variables
        self.balance = 0    #current total balance of this account
        self.available = 0  #current avaiable balance for trading
        self.minimalCoinBuy = 0.1 #62

        #initial positions
        self.positionSize = 0
        self.entryPrice   = 0
        self.markPrice    = 0

    def get_open_positions(self, symbol):
        try:
            sys.stdout = open(os.devnull, 'w')
            result = request_client.get_position()
            sys.stdout = sys.__stdout__

        except Exception as e:
            print(e)
            print("Error: Getting current open positions")
        else:
            for idx, row in enumerate(result):
                    members = [attr for attr in dir(row) if not callable(attr) and not attr.startswith("__")]
                    for member_def in members:
                        val_str = str(getattr(row, member_def))
                        if member_def == 'symbol':
                            if str(val_str) == symbol:
                                return
                        if member_def == 'positionAmt':
                            self.positionSize = float(val_str)

                        if member_def == 'entryPrice':
                            self.entryPrice = float(val_str)

                        if member_def == 'markPrice':
                            self.markPrice = float(val_str)

    def get_position_entry_price(self):
        try:
            sys.stdout = open(os.devnull, 'w')
            result = request_client.get_position()
            sys.stdout = sys.__stdout__
        except Exception as e:
            print(e)
            print("Error: Getting current open position price")
        else:
            price = 0
            for idx, row in enumerate(result):
                    members = [attr for attr in dir(row) if not callable(attr) and not attr.startswith("__")]
                    for member_def in members:
                        val_str = str(getattr(row, member_def))
                        if member_def == 'symbol':
                            if str(val_str) == self.coin:
                                return price
                        if member_def == 'entryPrice':
                            price = float(val_str)



    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object
    def init_strategy(self):
        try:
            self.get_open_positions(self.coin)
            self.get_balance()

            if self.positionSize != 0:
                self.buyStatus = 1

                if self.positionSize < 0:
                    self.tradeCounter = math.log2((abs(self.positionSize) * 0.5)/self.minimalCoinBuy) / math.log2(2)
                    self.tradeState = 0
                    self.buyPrice = self.entryPrice
                else:
                    self.tradeCounter = -1
                    self.tradeState = math.log2((self.positionSize * 0.5)/self.minimalCoinBuy) / math.log2(2)
                    self.buyPrice = self.entryPrice
        except ValueError:
            print(ValueError)
            print("Error: Strategy initialization")
        else:
            print("Strategy init successfully")

    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object
    def get_balance(self):
        try:
            sys.stdout = open(os.devnull, 'w')
            data = request_client.get_balance_v2()
            sys.stdout = sys.__stdout__
        except Exception as e:
            print(e)
            print("Error acessing balance")
        else:
            for idx, row in enumerate(data):
                if idx == 0:
                    members = [attr for attr in dir(row) if not callable(attr) and not attr.startswith("__")]
                    for member_def in members:
                        val_str = str(getattr(row, member_def))
                        if member_def == 'availableBalance':
                            self.available = float(val_str)
                        if member_def == 'balance':
                            self.balance = float(val_str)








    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object

    def change_leverage(self, symbol , leverage):
        try:
            sys.stdout = open(os.devnull, 'w')
            request_client.change_initial_leverage(symbol=symbol, leverage=2)
            sys.stdout = sys.__stdout__
        except Exception as e:
            print(e)
            print("Error: Change leverage")
        # print(result)

    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object
    def post_sell_order(self, quantity):
        try:
            sys.stdout = open(os.devnull, 'w')
            request_client.post_order(symbol=self.coin, side=OrderSide.SELL,
                                           ordertype=OrderType.MARKET, closePosition=False, quantity=quantity)
            sys.stdout = sys.__stdout__
        except Exception as e:
            print(e)
            print("Error: Open sell order")
        else:
            time.sleep(2)

    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object
    def set_sell_order_profit(self,quantity,stprice):
        try:
            sys.stdout = open(os.devnull, 'w')
            request_client.post_order(symbol=self.coin, side=OrderSide.BUY,
                                           ordertype=OrderType.TAKE_PROFIT_MARKET, closePosition=True,
                                           quantity=quantity, stopPrice=stprice)
            sys.stdout = sys.__stdout__
        except Exception as e:
            print(e)
            print("Error: Set sell order profit")
        else:
            time.sleep(2)

    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object
    def set_sell_order_take_loss(self,quantity,stprice):
        try:
            sys.stdout = open(os.devnull, 'w')
            request_client.post_order(symbol=self.coin, side=OrderSide.BUY,
                                               ordertype=OrderType.STOP_MARKET, closePosition=True,
                                               quantity=quantity, stopPrice=stprice)
            sys.stdout = sys.__stdout__
        except Exception as e:
            print(e)
            print("Error: Set sell order profit")
        else:
            time.sleep(2)

    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object
    def post_buy_order(self, quantity):
        try:
            sys.stdout = open(os.devnull, 'w')
            request_client.post_order(symbol=self.coin, side=OrderSide.BUY,
                                               ordertype=OrderType.MARKET, closePosition=False, quantity=quantity)
            sys.stdout = sys.__stdout__
        except Exception as e:
            print(e)
            print("Error:Open buy order")
        else:
            time.sleep(2)


    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object
    def set_buy_order_profit(self,quantity,stprice):
        try:
            sys.stdout = open(os.devnull, 'w')
            request_client.post_order(symbol=self.coin, side=OrderSide.SELL,
                                               ordertype=OrderType.TAKE_PROFIT_MARKET, closePosition=True,
                                               quantity=quantity, stopPrice=stprice)
            sys.stdout = sys.__stdout__
        except Exception as e:
            print(e)
            print("Error: Set sell order profit")
        else:
            time.sleep(2)


    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object
    def set_buy_order_take_loss(self,quantity,stprice):
        try:
            sys.stdout = open(os.devnull, 'w')
            request_client.post_order(symbol=self.coin, side=OrderSide.SELL,
                                               ordertype=OrderType.STOP_MARKET, closePosition=True,
                                               quantity=quantity,stopPrice=stprice)
            sys.stdout = sys.__stdout__
        except Exception as e:
            print(e)
            print("Error: Set sell order profit")
        else:
            time.sleep(2)


        # This function provides utility functions to work with Strings
        # 1. reverse(s): returns the reverse of the input string
        # 2. print(s): prints the string representation of the input object

    def cancel_all_orders(self):
        try:
            sys.stdout = open(os.devnull, 'w')
            request_client.cancel_all_orders(symbol=self.coin)
            sys.stdout = sys.__stdout__
        except Exception as e:
            print(e)
            print("Error: Set sell order profit")
        else:
            time.sleep(2)


    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object
    def post_order(self,type,quantity):
        result = 0
        entryPrice = 0
        stprice  = 0

        try:
            if type == 0:

                # self.post_single_order(type,quantity)
                self.post_sell_order(quantity)

                self.cancel_all_orders()

                time.sleep(2)

                entryPrice = self.get_position_entry_price()

                # set takeprofit
                time.sleep(2)
                stprice = Decimal(entryPrice*0.986)
                stprice = Decimal(stprice.quantize(Decimal('.01'), rounding=ROUND_HALF_UP))

                self.set_sell_order_profit(quantity,stprice)

                # set take loss
                time.sleep(2)
                stprice = Decimal(entryPrice * 1.05)
                stprice = Decimal(stprice.quantize(Decimal('.01'), rounding=ROUND_HALF_UP))

                self.set_sell_order_take_loss(quantity,stprice)

            else:
                # self.post_single_order(type, quantity)

                self.post_buy_order(quantity)

                # clean all orders
                time.sleep(2)
                self.cancel_all_orders()


                # get the current mark price and them apply the stop and profif
                time.sleep(2)
                entryPrice = self.get_position_entry_price()


                # set takeprofit
                time.sleep(2)
                stprice = Decimal(entryPrice * 1.013)
                stprice = Decimal(stprice.quantize(Decimal('.01'), rounding=ROUND_HALF_UP))

                self.set_buy_order_profit(quantity,stprice)

                # set take loss
                time.sleep(2)
                stprice = Decimal(entryPrice * 0.95)
                stprice = Decimal(stprice.quantize(Decimal('.01'), rounding=ROUND_HALF_UP))

                self.set_buy_order_take_loss(quantity,stprice)
        except ValueError:
            print(ValueError)
            print("Error: posting order")


    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object
    def get_price(self):

        try:
            sys.stdout = open(os.devnull, 'w')
            data = request_client.get_candlestick_data(symbol=self.coin, interval=CandlestickInterval.MIN5, startTime=None,endTime=None, limit=1)
            sys.stdout = sys.__stdout__
        except Exception as e:
            print(e)
            print("Error: getting Price")
        else:
            for idx, row in enumerate(data):
                if idx == 0:
                    members = [attr for attr in dir(row) if not callable(attr) and not attr.startswith("__")]
                    for member_def in members:
                        val_str = str(getattr(row, member_def))
                        if member_def == 'close':
                            self.price = float(val_str)
                        if member_def == 'openTime':
                            self.timestamp = int(val_str)
                            self.date = datetime.fromtimestamp((self.timestamp / 1000))


    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object
    def get_servertime(self):
        result = 0
        try:
            sys.stdout = open(os.devnull, 'w')
            result = request_client.get_servertime()
            sys.stdout = sys.__stdout__
        except Exception as e:
            print(e)
            print("Error: getting Price")
        else:
            return result

    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object
    def process_Price(self):
        try:
            self.get_price()
            if self.buyStatus == 1:
                if self.price >= self.buyPrice * 1.013 and self.tradeState == 0:
                    self.get_balance()
                    self.tradeCounter = self.tradeCounter + 1

                    if (self.available - pow(2, self.tradeCounter)) < 0:
                        print("NO BALANCE")
                        return

                    self.post_order(1,self.minimalCoinBuy * pow(2, self.tradeCounter) + (self.minimalCoinBuy * pow(2, self.tradeCounter -1 )))

                    self.tradeState = 1
                    print("Long at:",self.price, "current balance:", self.account)

                elif self.price <= self.buyPrice and self.tradeState == 1:

                    self.tradeCounter = self.tradeCounter + 1
                    self.get_balance()

                    if (self.available - pow(2, self.tradeCounter)) < 0:
                        print("NO BALANCE")
                        return

                    self.post_order(0, self.minimalCoinBuy * pow(2, self.tradeCounter) + (self.minimalCoinBuy * pow(2, self.tradeCounter -1 )))
                    self.tradeState = 0
                    print("Short at:", self.price, "current balance:", self.account)

            if self.buyStatus == 0:
                self.tradeCounter = -2
                self.buyStatus = 1
                self.tradeState = 0
                self.buyPrice = self.price
                self.post_order(0,(self.minimalCoinBuy * pow(2, self.tradeCounter)))
                print("---------------------------------------------")
                print("ORDER SELL :",self.coin)
                print("Quantity: ",(self.minimalCoinBuy * pow(2, self.tradeCounter)))
                print("---------------------------------------------")

        except ValueError:
            print(ValueError)
            print("Error:Strategy")



backtest = back_test_strategy()

def record_loop():
    global request_client

    backtest.init_strategy()

    current = 0
    while (True):
        try:
            dataNow = datetime.now().minute
            # check the server connection
            if dataNow != current:
                if (dataNow % 5) == 0:
                    result = backtest.get_servertime()

                    if result != 0:
                        current = dataNow

                        backtest.positionSize = 0
                        backtest.get_open_positions(backtest.coin)
                        if backtest.positionSize == 0:
                            backtest.buyStatus = 0
                        backtest.process_Price()
                        print("INFO: Bot -> ON")

                    else:
                        try:
                            request_client = RequestClient(api_key=g_api_key, secret_key=g_secret_key,
                                                       url='https://testnet.binancefuture.com/')
                        except Exception as e:
                            print(e)
                            print("ERROR: restarting client")
                        else:
                            print("INFO: Cient restarted")

        except Exception as e:
            print(e)






@app.route("/", methods=['GET'])
def index():
    return "<h1>Hello World!</h1>"

def main():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# Press the green button in the gutter to run the script.

# backtest = back_test_strategy()


if __name__ == '__main__':
    p = Process(target=record_loop)
    p.start()
    main()
    p.join()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
