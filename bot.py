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

    def __init__(self,requestClient, coin, minimalcoinbuy , minimalprofit, leverage, minimalMove):

        self.nmbOpenOrders = 0
        # --- Initial variables  -----
        self.client = requestClient
        self.coin = coin
        self.minimalCoinBuy = minimalcoinbuy
        self.minimalProfit  = minimalprofit
        self.minimalMove = minimalMove
        self.minimalBuy = 0
        self.leverage = leverage
        self.sellIncrement = 0

        self.buyPrice = 0
        self.buyStatus = 0
        self.tradeState = 1

        self.lastTradeState = 1

        self.aux = 0
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
                                return self.buyPrice
                        if member_def == 'entryPrice':
                            self.buyPrice = float(val_str)



    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object
    def init_strategy(self):
        try:
            self.get_open_positions(self.coin)
            self.get_balance()
            self.change_leverage(self.coin,self.leverage)

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
            self.client.change_initial_leverage(symbol=symbol, leverage=leverage)
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
    def get_open_orders(self):
        try:
            sys.stdout = open(os.devnull, 'w')
            data = self.client.get_open_orders(symbol=self.coin)

            sys.stdout = sys.__stdout__
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)
        else:
            if self.positionSize != 0:
                self.nmbOpenOrders = 0
                for idx, row in enumerate(data):
                        members = [attr for attr in dir(row) if not callable(attr) and not attr.startswith("__")]
                        for member_def in members:
                            self.nmbOpenOrders = idx + 1



    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object


    def set_sell_profit_and_stop_loss(self,entryPrice,quantity):

        stprice = Decimal(entryPrice * (1.0 - (100 / (self.leverage * 100))))
        stprice = Decimal(stprice.quantize(Decimal(str(0.001)), rounding=ROUND_HALF_UP))
        # stprice = Decimal(stprice.quantize(Decimal(str(self.minimalMove)), rounding=ROUND_HALF_UP))

        print("INFO: Profit:", quantity, stprice)
        self.set_sell_order_profit(quantity, stprice)

        # ---------- Set take loss -------------
        time.sleep(2)
        stprice = Decimal(entryPrice * 1.15)
        stprice = Decimal(stprice.quantize(Decimal(str(0.001)), rounding=ROUND_HALF_UP))
        # stprice = Decimal(stprice.quantize(Decimal(str(self.minimalMove)), rounding=ROUND_HALF_UP))

        print("INFO: Loss:", quantity, stprice)
        self.set_sell_order_take_loss(quantity, stprice)

        # This function provides utility functions to work with Strings
        # 1. reverse(s): returns the reverse of the input string
        # 2. print(s): prints the string representation of the input object

    def set_buy_profit_and_stop_loss(self, entryPrice, quantity):

        stprice = Decimal(entryPrice * (1.0 + (100 / (self.leverage * 100))))
        stprice = Decimal(stprice.quantize(Decimal(str(0.001)), rounding=ROUND_HALF_UP))
        # stprice = Decimal(stprice.quantize(Decimal(str(self.minimalMove)), rounding=ROUND_HALF_UP))

        print("INFO: Profit:", quantity, stprice)
        self.set_buy_order_profit(quantity, stprice)

        # ---------- Set take loss -------------
        time.sleep(2)
        stprice = Decimal(entryPrice * 0.85)
        stprice = Decimal(stprice.quantize(Decimal(str(0.001)), rounding=ROUND_HALF_UP))
        # stprice = Decimal(stprice.quantize(Decimal(str(self.minimalMove)), rounding=ROUND_HALF_UP))

        print("INFO: Loss:", quantity, stprice)
        self.set_buy_order_take_loss(quantity, stprice)

    # This function provides utility functions to work with Strings
    # 1. reverse(s): returns the reverse of the input string
    # 2. print(s): prints the string representation of the input object

    def post_order(self,type,quantity):
        try:
            if type == 0:

                self.aux = self.buyPrice

                self.cancel_all_orders()
                self.post_sell_order(quantity)

                entryPrice = self.get_position_entry_price()

                time.sleep(1)

                self.set_sell_profit_and_stop_loss(entryPrice,quantity)

            else:
                # self.post_single_order(type, quantity)
                self.aux = self.buyPrice

                self.cancel_all_orders()
                self.post_buy_order(quantity)

                # ---- get the current mark price and them apply the stop and profit ---

                entryPrice = self.get_position_entry_price()

                time.sleep(1)
                self.set_buy_profit_and_stop_loss(entryPrice, quantity)



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


            # ------ Get the current coin price -----------
            self.get_price()

            # ------ Get the order price -----------
            self.get_position_entry_price()

            if self.nmbOpenOrders != 2:
                self.cancel_all_orders()
                time.sleep(1)
                if self.tradeState == 1:
                    self.set_buy_profit_and_stop_loss(self.buyPrice, self.positionSize)
                else:
                    self.set_sell_profit_and_stop_loss(self.buyPrice, self.positionSize)

            # ---------- Continue with the current opened position  -------------
            if self.buyStatus == 1:

                if self.tradeState == 0:
                    print("---------------------------------------------")
                    print("INFO: Next buy at: :", (self.buyPrice * (1.0 + (100 / (self.leverage * 100)))))
                    print("---------------------------------------------")
                elif self.tradeState == 1:
                    print("---------------------------------------------")
                    print("INFO: Next sell at: :", (self.buyPrice * (1.0 - (100 / (self.leverage * 100)))))
                    print("---------------------------------------------")

                if self.price >= (self.buyPrice * (1.0 + (100 / (self.leverage * 100)))) and self.tradeState == 0:

                    self.positionSize = ((((self.price / self.buyPrice) - 1.025)*self.leverage) + 1.0) * abs(self.positionSize)



                    calculation = (2 * abs(self.positionSize)) + abs(self.positionSize)

                    self.minimalBuy = Decimal(calculation)

                    if self.minimalCoinBuy > 0.1:
                        self.minimalBuy = Decimal(self.minimalBuy.quantize(Decimal(str(0)), rounding=ROUND_HALF_UP))
                    else:
                        self.minimalBuy = Decimal(self.minimalBuy.quantize(Decimal(str(self.minimalCoinBuy)), rounding=ROUND_HALF_UP))

                    if self.post_order(1, self.minimalBuy):
                        self.tradeState = 1

                    print("---------------------------------------------")
                    print("INFO: Long at:", self.price, " Current balance:", self.available)
                    print("INFO: Quantity:", (2 * abs(self.positionSize)) + abs(self.positionSize))
                    print("---------------------------------------------")

                elif self.price <= (self.buyPrice * (1.0 - (100 / (self.leverage * 100)))) and self.tradeState == 1:

                    self.positionSize = (((0.975 - (self.price / self.buyPrice)) * self.leverage)+1.0) * abs(self.positionSize)

                    # self.get_balance()
                    calculation = (2 * abs(self.positionSize)) + abs(self.positionSize)

                    self.minimalBuy = Decimal(calculation)

                    if self.minimalCoinBuy > 0.1:
                        self.minimalBuy = Decimal(self.minimalBuy.quantize(Decimal(str(0)), rounding=ROUND_HALF_UP))
                    else:
                        self.minimalBuy = Decimal(self.minimalBuy.quantize(Decimal(str(self.minimalCoinBuy)), rounding=ROUND_HALF_UP))

                    if self.post_order(0, self.minimalBuy):
                        self.tradeState = 0

                    print("---------------------------------------------")
                    print("INFO: short at:", self.price, " Current balance:", self.available)
                    print("INFO: Quantity:", (2 * abs(self.positionSize)) + abs(self.positionSize))
                    print("---------------------------------------------")

            # ---------- Sell the first time position -------------
            if self.buyStatus == 0:
                # ---------------------------------------------------------
                # ---- sell the first order with the minimal buy order ----

                # ---------------------------------------------------------------
                # calculate if the investiment is bigger than minimal investiment
                if ((self.minimalProfit * self.leverage) / self.price) > self.minimalCoinBuy:
                    calculation = (self.minimalProfit * self.leverage) / self.price
                    self.minimalBuy = Decimal(calculation)

                    if self.minimalCoinBuy > 0.1:
                        self.minimalBuy = Decimal(self.minimalBuy.quantize(Decimal(str(0)), rounding=ROUND_HALF_UP))
                    else:
                        self.minimalBuy = Decimal(self.minimalBuy.quantize(Decimal(str(self.minimalCoinBuy)), rounding=ROUND_HALF_UP))

                else:
                    self.minimalBuy = Decimal(self.minimalCoinBuy)

                self.buyPrice = 0
                # self.sellIncrement = 0

                # try to place order

                # check last order

                if self.tradeState == 1 :
                    if self.post_order(1, self.minimalBuy):

                        self.positionSize = self.minimalBuy
                        self.buyStatus = 1

                        self.buyPrice = self.get_position_entry_price()

                        self.tradeState = 1
                    else:
                        self.buyStatus = 0
                else:
                    if self.post_order(0, self.minimalBuy):

                        self.positionSize = self.minimalBuy
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
