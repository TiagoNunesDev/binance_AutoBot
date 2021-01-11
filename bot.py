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

class Bot:

    def __init__(self,requestClient, coin, minimalcoinbuy):

        # --- Initial variables  -----
        self.client = requestClient
        self.coin = coin
        self.minimalCoinBuy = minimalcoinbuy


        self.buyPrice = 0
        self.buyStatus = 0
        self.tradeState = 0

        # Coin for trading variables

        self.price = 0
        self.timestamp = 0
        self.date = 0

        # Account balance variables
        self.balance = 0    #current total balance of this account
        self.available = 0  #current avaiable balance for trading


        #initial positions
        self.positionSize = 0
        self.entryPrice = 0
        self.markPrice = 0

    def get_open_positions(self, symbol):
        try:
            sys.stdout = open(os.devnull, 'w')
            result = self.client.get_position()
            sys.stdout = sys.__stdout__

        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)
            return False
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
            return True

    def get_position_entry_price(self):
        try:
            sys.stdout = open(os.devnull, 'w')
            result = self.client.get_position()
            sys.stdout = sys.__stdout__
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)
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
                    self.tradeState = 0
                    self.buyPrice = self.entryPrice
                else:
                    self.tradeState = 1
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
            data = self.client.get_balance_v2()
            sys.stdout = sys.__stdout__
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)
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
            self.client.change_initial_leverage(symbol=symbol, leverage=2)
            sys.stdout = sys.__stdout__
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)


    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object
    def post_sell_order(self, quantity):
        try:
            sys.stdout = open(os.devnull, 'w')
            self.client.post_order(symbol=self.coin, side=OrderSide.SELL,
                                           ordertype=OrderType.MARKET, closePosition=False, quantity=quantity)
            sys.stdout = sys.__stdout__
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)
        else:
            time.sleep(2)

    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object
    def set_sell_order_profit(self,quantity,stprice):
        try:
            sys.stdout = open(os.devnull, 'w')
            self.client.post_order(symbol=self.coin, side=OrderSide.BUY,
                                           ordertype=OrderType.TAKE_PROFIT_MARKET, closePosition=True,
                                           quantity=quantity, stopPrice=stprice)
            sys.stdout = sys.__stdout__
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)
        else:
            time.sleep(2)

    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object
    def set_sell_order_take_loss(self,quantity,stprice):
        try:
            sys.stdout = open(os.devnull, 'w')
            self.client.post_order(symbol=self.coin, side=OrderSide.BUY,
                                               ordertype=OrderType.STOP_MARKET, closePosition=True,
                                               quantity=quantity, stopPrice=stprice)
            sys.stdout = sys.__stdout__
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)
        else:
            time.sleep(2)

    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object
    def post_buy_order(self, quantity):
        try:
            sys.stdout = open(os.devnull, 'w')
            self.client.post_order(symbol=self.coin, side=OrderSide.BUY,
                                               ordertype=OrderType.MARKET, closePosition=False, quantity=quantity)
            sys.stdout = sys.__stdout__
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)
        else:
            time.sleep(2)


    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object
    def set_buy_order_profit(self,quantity,stprice):
        try:
            sys.stdout = open(os.devnull, 'w')
            self.client.post_order(symbol=self.coin, side=OrderSide.SELL,
                                               ordertype=OrderType.TAKE_PROFIT_MARKET, closePosition=True,
                                               quantity=quantity, stopPrice=stprice)
            sys.stdout = sys.__stdout__
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)
        else:
            time.sleep(2)


    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object
    def set_buy_order_take_loss(self,quantity,stprice):
        try:
            sys.stdout = open(os.devnull, 'w')
            self.client.post_order(symbol=self.coin, side=OrderSide.SELL,
                                               ordertype=OrderType.STOP_MARKET, closePosition=True,
                                               quantity=quantity,stopPrice=stprice)
            sys.stdout = sys.__stdout__
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)
        else:
            time.sleep(2)


        # This function provides utility functions to work with Strings
        # 1. reverse(s): returns the reverse of the input string
        # 2. print(s): prints the string representation of the input object

    def cancel_all_orders(self):
        try:
            sys.stdout = open(os.devnull, 'w')
            self.client.cancel_all_orders(symbol=self.coin)
            sys.stdout = sys.__stdout__
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)
        else:
            time.sleep(1)


    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object
    def post_order(self,type,quantity):
        result = 0
        entryPrice = 0
        stprice  = 0

        try:
            if type == 0:

                self.cancel_all_orders()
                self.post_sell_order(quantity)

                entryPrice = self.get_position_entry_price()

                # ---------- Set take profit  -------------
                time.sleep(2)
                stprice = Decimal(entryPrice*0.986)
                stprice = Decimal(stprice.quantize(Decimal('.01'), rounding=ROUND_HALF_UP))

                self.set_sell_order_profit(quantity, stprice)

                # ---------- Set take loss -------------
                time.sleep(2)
                stprice = Decimal(entryPrice * 1.05)
                stprice = Decimal(stprice.quantize(Decimal('.01'), rounding=ROUND_HALF_UP))

                self.set_sell_order_take_loss(quantity, stprice)

            else:
                # self.post_single_order(type, quantity)

                self.cancel_all_orders()
                self.post_buy_order(quantity)

                # ---- get the current mark price and them apply the stop and profit ---

                entryPrice = self.get_position_entry_price()

                # ---------- Set take profit  -------------
                time.sleep(2)
                stprice = Decimal(entryPrice * 1.013)
                stprice = Decimal(stprice.quantize(Decimal('.01'), rounding=ROUND_HALF_UP))

                self.set_buy_order_profit(quantity,stprice)

                # ---------- Set take loss -------------
                time.sleep(2)
                stprice = Decimal(entryPrice * 0.95)
                stprice = Decimal(stprice.quantize(Decimal('.01'), rounding=ROUND_HALF_UP))

                self.set_buy_order_take_loss(quantity,stprice)

        except ValueError:
            print(ValueError)
            print("ERROR: Posting new order")
            return False
        else:
            return True


    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object
    def get_price(self):

        try:
            sys.stdout = open(os.devnull, 'w')
            data = self.client.get_candlestick_data(symbol=self.coin, interval=CandlestickInterval.MIN5, startTime=None,endTime=None, limit=1)
            sys.stdout = sys.__stdout__
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)
            return False
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
            return True

    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object
    def get_servertime(self):
        result = 0
        try:
            sys.stdout = open(os.devnull, 'w')
            result = self.client.get_servertime()
            sys.stdout = sys.__stdout__
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)
        else:
            return result

    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object
    def process_Price(self):
        try:
            # ---------------------------------------------------------
            # ---------- Check for current open positions -------------

            # if self.get_open_positions(self.coin):
            #     if self.positionSize == 0:
            #         self.buyStatus = 0
            #     else:
            #         self.buyStatus = 0

                # ---------- Check for current price -------------

                self.get_price()

                # ---------- Continue with the current opened position  -------------
                if self.buyStatus == 1:

                    if self.price >= self.buyPrice * 1.013 and self.tradeState == 0:
                        self.get_balance()

                        if self.post_order(1, (2 * abs(self.positionSize)) + self.minimalCoinBuy):
                           self.tradeState = 1

                        print("---------------------------------------------")
                        print("INFO: Long at:", self.price, " Current balance:", self.available)
                        print("INFO: Quantity:", (2 * abs(self.positionSize)) + self.minimalCoinBuy)
                        print("---------------------------------------------")

                    elif self.price <= self.buyPrice and self.tradeState == 1:

                        self.get_balance()

                        if self.post_order(0, (2 * abs(self.positionSize)) + self.minimalCoinBuy):
                            self.tradeState = 0
                        print("---------------------------------------------")
                        print("INFO: short at:", self.price, " Current balance:", self.available)
                        print("INFO: Quantity:", (2 * abs(self.positionSize)) + self.minimalCoinBuy)
                        print("---------------------------------------------")

                # ---------- Sell the first time position -------------
                if self.buyStatus == 0:

                    # ---------------------------------------------------------
                    # ---- sell the first order with the minimal buy order ----

                    if self.post_order(0, self.minimalCoinBuy):
                        self.positionSize = self.minimalCoinBuy
                        self.buyStatus = 1
                        self.buyPrice = self.get_position_entry_price()
                        self.tradeState = 0
                    else:
                        self.buyStatus = 0

                    print("---------------------------------------------")
                    print("ORDER SELL :", self.coin)
                    print("Quantity: ", self.positionSize)
                    print("---------------------------------------------")

        except ValueError:
            print(ValueError)
            print("Error:Strategy")