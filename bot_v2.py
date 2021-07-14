from enum import Enum
from decimal import *


class BotStatus(Enum):
    NOTDEFINED = 0
    PLACEORDERFIRSTBUY = 1
    PLACEORDERFIRSTSELL = 2
    ORDERBUYCONTROL = 3
    ORDERSELLCONTROL = 4
    PLACEORDERBUY = 5
    PLACEORDERSELL = 6



class Strategy:
    def __init__(self,**kwargs):
        # self.client = kwargs["client"]
        self.name = kwargs["name"]
        # self.data = kwargs['data']
        self.cash = kwargs["balance"]
        self.percentage = kwargs["percentage"]
        self.minTradeAmount = kwargs["minTradeAmount"]
        self.minPriceMove = kwargs["minPriceMove"]
        self.binanceApi = kwargs["binanceApi"]
        # non editable varibles
        # self.cash = None
        self.percentageAux = None
        self.orderPrice = None
        self.profitPrice = None
        self.lossPrice = None
        self.numberTries = None
        self.status = None
        self.lastOrderPrice = None
        self.desireProfit = None
        self.investUSDT = None
        self.binanceMinQuantity = None
        self.orderSize = None
        self.leverage = None
        self.numberTries = None
        self.numberTriesBigger = 0


    def process_coin_price(self,price:'float' = None):

                if self.status == BotStatus.NOTDEFINED:
                    self.status = BotStatus.PLACEORDERFIRSTSELL

                if self.status ==  BotStatus.PLACEORDERFIRSTBUY:
                    self.numberTries = 1
                    self.percentageAux = self.percentage
                    #calculate the ordersize
                    self.desireProfit = self.cash
                    self.investUSDT = self.desireProfit * self.percentageAux

                    #calculate binance min quantity
                    self.binanceMinOrder = 5.0 / float(price)

                    # calculate the leverage
                    self.leverage = (self.binanceMinOrder * float(price)) / self.desireProfit
                    if self.leverage < 1.0:
                        self.leverage = 1.0

                    self.leverage = Decimal(self.leverage)
                    self.leverage = Decimal(self.leverage.quantize(Decimal('0'), rounding=ROUND_HALF_UP))

                    #calculate again de order size
                    # self.binanceMinOrder =
                    self.orderSize = Decimal(self.desireProfit) * self.leverage / Decimal(price)
                    self.orderSize = Decimal(self.orderSize.quantize(Decimal(self.minTradeAmount), rounding=ROUND_HALF_UP))

                    self.orderPrice = float(price)
                    self.profitPrice = (1.0 + self.percentageAux) * self.orderPrice
                    self.profitPrice = Decimal(self.profitPrice)
                    self.profitPrice = Decimal(self.profitPrice.quantize(Decimal(str(self.minPriceMove)), rounding=ROUND_HALF_UP))

                    self.lossPrice = 0.92 * self.orderPrice
                    self.lossPrice = Decimal(self.lossPrice)
                    self.lossPrice = Decimal(self.lossPrice.quantize(Decimal(str(self.minPriceMove)), rounding=ROUND_HALF_UP))


                    self.status = BotStatus.ORDERBUYCONTROL

                    # place a buy order
                    self.binanceApi.post_buy_order(self.name,self.orderSize)
                    self.binanceApi.post_buy_order_profit(self.name,self.orderSize,self.profitPrice)
                    # self.binanceApi.post_buy_order_take_loss(self.name,self.orderSize,self.lossPrice)

                    print("----------- Buy Order ------------")
                    print("-- Desire profit:", self.desireProfit)
                    print("-- Leverage:", self.leverage)
                    print("-- Order size:", self.orderSize)
                    print("-- Buy at:",    self.orderPrice)
                    print("-- Profit at:", self.profitPrice)
                    print("-----------------------------------")

                if self.status ==  BotStatus.PLACEORDERFIRSTSELL:

                    self.numberTries = 1
                    self.percentageAux = self.percentage

                    # calculate the ordersize
                    self.desireProfit =  self.cash
                    self.investUSDT = self.desireProfit * self.percentageAux

                    # calculate binance min quantity
                    self.binanceMinOrder = 5.0 / float(price)

                    # calculate the leverage
                    self.leverage = (self.binanceMinOrder * float(price)) / self.desireProfit
                    if self.leverage < 1.0:
                        self.leverage = 1.0

                    self.leverage = Decimal(self.leverage)
                    self.leverage = Decimal(self.leverage.quantize(Decimal('0'), rounding=ROUND_HALF_UP))

                    # calculate again de order size
                    # self.binanceMinOrder =
                    self.orderSize = Decimal(self.desireProfit) * self.leverage / Decimal(price)
                    self.orderSize = Decimal(self.orderSize.quantize(Decimal(str(self.minTradeAmount)), rounding=ROUND_HALF_UP))

                    self.orderPrice = float(price)
                    self.profitPrice = (1.0 - self.percentageAux) * self.orderPrice
                    self.profitPrice = Decimal(self.profitPrice)
                    self.profitPrice = Decimal(self.profitPrice.quantize(Decimal(str(self.minPriceMove)), rounding=ROUND_HALF_UP))

                    self.lossPrice = (1.0 + self.percentageAux) * self.orderPrice
                    self.lossPrice = Decimal(self.lossPrice)
                    self.lossPrice = Decimal(self.lossPrice.quantize(Decimal(str(self.minPriceMove)), rounding=ROUND_HALF_UP))

                    self.status = BotStatus.ORDERSELLCONTROL

                    # place a sell order
                    self.binanceApi.post_sell_order(self.name,self.orderSize)
                    self.binanceApi.post_sell_order_profit(self.name,self.orderSize,self.profitPrice)
                    # self.binanceApi.post_sell_order_take_loss(self.name,self.orderSize,self.lossPrice)

                    print("----------- Sell Order ------------")
                    print("-- Desire profit:", self.desireProfit)
                    print("-- Leverage:",self.leverage)
                    print("-- Order size:", self.orderSize)
                    print("-- Sell at:", self.orderPrice)
                    print("-- Profit at:", self.profitPrice)
                    print("-----------------------------------")

                if self.status == BotStatus.ORDERBUYCONTROL:
                    if float(price) >= self.profitPrice:
                        self.cash += self.investUSDT

                        if self.numberTriesBigger < self.numberTries:
                            self.numberTriesBigger = self.numberTries

                        print("-- Nmb tries:",self.numberTries)
                        print("-- Cash:", self.cash)
                        print("-- Nmb trades:", self.numberTries)
                        print("-- Nmb trades max:", self.numberTriesBigger)
                        print("----------- Trade ended ------------")
                        self.status = BotStatus.PLACEORDERFIRSTBUY
                    elif float(price) <= (self.orderPrice * (1.0 - self.percentageAux)):
                        self.status = BotStatus.PLACEORDERSELL

                if self.status == BotStatus.ORDERSELLCONTROL:
                    if float(price) <= self.profitPrice:
                        self.cash += self.investUSDT

                        if self.numberTriesBigger < self.numberTries:
                            self.numberTriesBigger = self.numberTries

                        print("-- Nmb tries:",self.numberTries)
                        print("-- Cash:", self.cash)
                        print("-- Nmb trades:", self.numberTries)
                        print("-- Nmb trades max:", self.numberTriesBigger)
                        print("----------- Trade ended ------------")
                        self.status = BotStatus.PLACEORDERFIRSTSELL
                    elif float(price) >= (self.orderPrice * (1.0 + self.percentageAux)):
                        self.status = BotStatus.PLACEORDERBUY

                if self.status == BotStatus.PLACEORDERBUY:
                    # self.numberTries += 1
                    self.numberTries +=1

                    self.percentageAux = (float(price) / self.orderPrice) - 1.0
                    self.orderPrice = float(price)

                    self.orderSize =  self.orderSize * Decimal(2.0)

                    self.lossPrice = 0.95 * self.orderPrice
                    self.lossPrice = Decimal(self.lossPrice)
                    self.lossPrice = Decimal(self.lossPrice.quantize(Decimal(str(self.minPriceMove)), rounding=ROUND_HALF_UP))

                    self.status = BotStatus.ORDERBUYCONTROL

                    self.profitPrice = (1.0 + self.percentageAux) * self.orderPrice
                    self.profitPrice = Decimal(self.profitPrice)
                    self.profitPrice = Decimal(self.profitPrice.quantize(Decimal(str(self.minPriceMove)), rounding=ROUND_HALF_UP))

                    # place a buy order
                    self.binanceApi.post_buy_order(self.name,self.orderSize)
                    self.binanceApi.post_buy_order_profit(self.name,self.orderSize,self.profitPrice)
                    # self.binanceApi.post_buy_order_take_loss(self.name,self.orderSize,self.lossPrice)

                    print("-- Buy at", self.orderPrice)
                    print("-- Order Size:", self.orderSize)
                    print("-- Buy at",self.orderPrice)
                    print("-- Profit at:", self.profitPrice)
                    print("-----------------------------------")

                if self.status == BotStatus.PLACEORDERSELL:
                    # self.numberTries += 1
                    self.numberTries += 1

                    self.percentageAux = 1.0 - (float(price)/self.orderPrice)
                    self.orderPrice = float(price)

                    self.profitPrice = (1.0- self.percentageAux) * self.orderPrice
                    self.orderSize = self.orderSize * Decimal(2.0)
                    self.lossPrice = 1.05 * self.orderPrice
                    self.lossPrice = Decimal(self.lossPrice)
                    self.lossPrice = Decimal(self.lossPrice.quantize(Decimal(str(self.minPriceMove)), rounding=ROUND_HALF_UP))

                    self.status = BotStatus.ORDERSELLCONTROL

                    self.profitPrice = Decimal(self.profitPrice)
                    self.profitPrice = Decimal(self.profitPrice.quantize(Decimal(str(self.minPriceMove)), rounding=ROUND_HALF_UP))

                    # place a sell order
                    self.binanceApi.post_sell_order(self.name,self.orderSize)
                    self.binanceApi.post_sell_order_profit(self.name,self.orderSize,self.profitPrice)
                    # self.binanceApi.post_sell_order_take_loss(self.name,self.orderSize,self.lossPrice)


                    print("-- Sell at", self.orderPrice)
                    print("-- Order Size:", self.orderSize)
                    print("-- Profit at:", self.profitPrice)
                    print("-----------------------------------")

    def process_coin_price_V2(self,price:'float' = None):

                if self.status == BotStatus.NOTDEFINED:
                    self.status = BotStatus.PLACEORDERFIRSTSELL

                if self.status ==  BotStatus.PLACEORDERFIRSTBUY:
                    self.numberTries = 1
                    self.percentageAux = self.percentage
                    #calculate the ordersize
                    self.desireProfit = 0.1 * self.cash
                    self.investUSDT = self.desireProfit / self.percentageAux

                    #calculate binance min quantity
                    self.binanceMinOrder = 5.0 / float(price)

                    # calculate the leverage
                    self.leverage = (self.binanceMinOrder * float(price)) / self.investUSDT
                    if self.leverage < 1.0:
                        self.leverage = 1.0

                    self.leverage = Decimal(self.leverage)
                    self.leverage = Decimal(self.leverage.quantize(Decimal('0'), rounding=ROUND_HALF_UP))

                    #calculate again de order size
                    # self.binanceMinOrder =
                    self.orderSize = Decimal(self.investUSDT) * self.leverage / Decimal(price)
                    self.orderSize = Decimal(self.orderSize.quantize(Decimal(self.minTradeAmount), rounding=ROUND_HALF_UP))

                    self.orderPrice = float(price)
                    self.profitPrice = (1.0 + self.percentageAux) * self.orderPrice
                    self.profitPrice = Decimal(self.profitPrice)
                    self.profitPrice = Decimal(self.profitPrice.quantize(Decimal(str(self.minPriceMove)), rounding=ROUND_HALF_UP))

                    self.lossPrice = 0.92 * self.orderPrice
                    self.status = BotStatus.ORDERBUYCONTROL

                    self.binanceApi.post_buy_order(self.name, self.orderSize)
                    self.binanceApi.post_buy_order_profit(self.name, self.orderSize, self.profitPrice)

                    print("----------- Buy Order ------------")
                    print("-- Desire profit:", self.desireProfit)
                    print("-- Leverage:", self.leverage)
                    print("-- Order size:", self.orderSize)
                    print("-- Buy at:",    self.orderPrice)
                    print("-- Profit at:", self.profitPrice)
                    print("-----------------------------------")

                if self.status ==  BotStatus.PLACEORDERFIRSTSELL:

                    self.numberTries = 1
                    self.percentageAux = self.percentage

                    # calculate the ordersize
                    self.desireProfit = 0.1 * self.cash
                    self.investUSDT = self.desireProfit / self.percentageAux

                    # calculate binance min quantity
                    self.binanceMinOrder = 5.0 / float(price)

                    # calculate the leverage
                    self.leverage = (self.binanceMinOrder * float(price)) / self.investUSDT
                    if self.leverage < 1.0:
                        self.leverage = 1.0

                    self.leverage = Decimal(self.leverage)
                    self.leverage = Decimal(self.leverage.quantize(Decimal('0'), rounding=ROUND_HALF_UP))

                    # calculate again de order size
                    # self.binanceMinOrder =
                    self.orderSize = Decimal(self.investUSDT) * self.leverage / Decimal(price)
                    self.orderSize = Decimal(self.orderSize.quantize(Decimal(self.minTradeAmount), rounding=ROUND_HALF_UP))

                    self.orderPrice = float(price)
                    self.profitPrice = (1.0 - self.percentageAux) * self.orderPrice
                    self.profitPrice = Decimal(self.profitPrice)
                    self.profitPrice = Decimal(self.profitPrice.quantize(Decimal(str(self.minPriceMove)), rounding=ROUND_HALF_UP))

                    self.lossPrice = (1.0 + self.percentageAux) * self.orderPrice
                    self.status = BotStatus.ORDERSELLCONTROL

                    self.binanceApi.post_sell_order(self.name, self.orderSize)
                    self.binanceApi.post_sell_order_profit(self.name, self.orderSize, self.profitPrice)

                    print("----------- Sell Order ------------")
                    print("-- Desire profit:", self.desireProfit)
                    print("-- Leverage:",self.leverage)
                    print("-- Order size:", self.orderSize)
                    print("-- Sell at:", self.orderPrice)
                    print("-- Profit at:", self.profitPrice)
                    print("-----------------------------------")

                if self.status == BotStatus.ORDERBUYCONTROL:
                    if float(price) >= self.profitPrice:
                        self.cash += self.desireProfit

                        if self.numberTriesBigger < self.numberTries:
                            self.numberTriesBigger = self.numberTries

                        print("-- Nmb tries:",self.numberTries)
                        print("-- Cash:", self.cash)
                        print("-- Nmb trades:", self.numberTries)
                        print("-- Nmb trades max:", self.numberTriesBigger)
                        print("----------- Trade ended ------------")
                        self.status = BotStatus.PLACEORDERFIRSTBUY
                    elif float(price) <= (self.orderPrice * (1.0 - self.percentageAux)):
                        self.status = BotStatus.PLACEORDERSELL

                if self.status == BotStatus.ORDERSELLCONTROL:
                    if float(price) <= self.profitPrice:
                        self.cash += self.desireProfit

                        if self.numberTriesBigger < self.numberTries:
                            self.numberTriesBigger = self.numberTries

                        print("-- Nmb tries:",self.numberTries)
                        print("-- Cash:", self.cash)
                        print("-- Nmb trades:", self.numberTries)
                        print("-- Nmb trades max:", self.numberTriesBigger)
                        print("----------- Trade ended ------------")
                        self.status = BotStatus.PLACEORDERFIRSTSELL
                    elif float(price) >= (self.orderPrice * (1.0 + self.percentageAux)):
                        self.status = BotStatus.PLACEORDERBUY

                if self.status == BotStatus.PLACEORDERBUY:
                    # self.numberTries += 1
                    self.numberTries +=1
                    self.percentageAux = (float(price)/self.orderPrice ) - 1.0
                    self.percentageAux = self.percentageAux * 2.0
                    self.orderPrice = float(price)
                    # self.orderSize =  self.orderSize * Decimal(2.0)

                    self.lossPrice = 0.95 * self.orderPrice
                    self.status = BotStatus.ORDERBUYCONTROL

                    self.profitPrice = (1.0 + self.percentageAux) * self.orderPrice
                    self.profitPrice = Decimal(self.profitPrice)
                    self.profitPrice = Decimal(self.profitPrice.quantize(Decimal(str(self.minPriceMove)), rounding=ROUND_HALF_UP))

                    self.binanceApi.post_buy_order(self.name, self.orderSize)
                    self.binanceApi.post_buy_order_profit(self.name, self.orderSize, self.profitPrice)

                    print("-- Buy at", self.orderPrice)
                    print("-- Order Size:", self.orderSize)
                    print("-- Buy at",self.orderPrice)
                    print("-- Profit at:", self.profitPrice)
                    print("-----------------------------------")

                if self.status == BotStatus.PLACEORDERSELL:
                    # self.numberTries += 1
                    self.numberTries += 1
                    self.percentageAux = 1.0 - (float(price)/self.orderPrice)
                    self.percentageAux = self.percentageAux * 2.0
                    self.orderPrice = float(price)

                    # self.orderSize = self.orderSize * Decimal(2.0)

                    self.lossPrice = 1.05 * self.orderPrice
                    self.status = BotStatus.ORDERSELLCONTROL

                    self.profitPrice = (1.0 - self.percentageAux) * self.orderPrice
                    self.profitPrice = Decimal(self.profitPrice)
                    self.profitPrice = Decimal(self.profitPrice.quantize(Decimal(str(self.minPriceMove)), rounding=ROUND_HALF_UP))

                    self.binanceApi.post_buy_order(self.name, self.orderSize)
                    self.binanceApi.post_buy_order_profit(self.name, self.orderSize, self.profitPrice)

                    print("-- Sell at", self.orderPrice)
                    print("-- Order Size:", self.orderSize)
                    print("-- Sell at", self.orderPrice)
                    print("-- Profit at:", self.profitPrice)
                    print("-----------------------------------")


        # print(float(dt.close))

