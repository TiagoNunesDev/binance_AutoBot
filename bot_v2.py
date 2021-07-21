from enum import Enum
from decimal import *
from binanceApi import *

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
        self.maxLeverage = kwargs["maxLev"]
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

    def place_order_first_sell(self,price):
        self.numberTries = 1
        self.percentageAux = self.percentage

        # calculate the ordersize
        self.desireProfit = self.cash

        # self.investUSDT = self.desireProfit * self.percentageAux
        self.investUSDT = self.desireProfit

        # calculate binance min quantity
        self.binanceMinOrder = 6.0 / float(price)

        # calculate the leverage
        self.leverage = (self.binanceMinOrder * float(price)) / self.investUSDT
        if self.leverage < 1.0:
            self.leverage = 1.0

        self.leverage = Decimal(self.leverage)
        self.leverage = Decimal(self.leverage.quantize(Decimal('0'), rounding=ROUND_HALF_UP))

        self.binanceApi.set_leverage(self.name, self.leverage)

        # calculate again de order size
        self.orderSize = Decimal(self.investUSDT) * self.leverage / Decimal(price)
        self.orderSize = Decimal(self.orderSize.quantize(Decimal(str(self.minTradeAmount)), rounding=ROUND_HALF_UP))

        # place sell order
        if self.binanceApi.post_sell_order(self.name, self.orderSize):

            time.sleep(2)
            # get open position
            positions = self.binanceApi.get_open_positions(self.name)
            self.orderPrice = positions[1]

            # calculate new profit price
            self.profitPrice = (1.0 - self.percentageAux) * self.orderPrice  # OK
            self.profitPrice = Decimal(self.profitPrice)  # OK
            self.profitPrice = Decimal(self.profitPrice.quantize(Decimal(str(self.minPriceMove)), rounding=ROUND_HALF_UP))

            self.lossPrice = (1.0 + self.percentageAux) * self.orderPrice
            self.status = BotStatus.ORDERSELLCONTROL

            self.binanceApi.post_sell_order_profit(self.name, self.orderSize, self.profitPrice)

            print("DEBUG: Sell Order ")
            print("DEBUG: Desire profit:", self.desireProfit)
            print("DEBUG: Leverage:", self.leverage)
            print("DEBUG: Order size:", self.orderSize)
            print("DEBUG: Sell at:", self.orderPrice)
            print("DEBUG: Profit at:", self.profitPrice)

        else:
            print("ERROR: opening Sell order")

    def place_order_first_buy(self,price):
        self.numberTries = 1
        self.percentageAux = self.percentage
        # calculate the ordersize
        self.desireProfit = self.cash
        #  self.investUSDT = self.desireProfit * self.percentageAux
        self.investUSDT = self.desireProfit
        # calculate binance min quantity
        self.binanceMinOrder = 6 / float(price)

        # calculate the leverage
        self.leverage = (self.binanceMinOrder * float(price)) / self.investUSDT
        if self.leverage < 1.0:
            self.leverage = 1.0

        self.leverage = Decimal(self.leverage)
        self.leverage = Decimal(self.leverage.quantize(Decimal('0'), rounding=ROUND_HALF_UP))

        self.binanceApi.set_leverage(self.name, self.leverage)

        # calculate again de order size
        # self.binanceMinOrder =
        self.orderSize = Decimal(self.investUSDT) * self.leverage / Decimal(price)
        self.orderSize = Decimal(self.orderSize.quantize(Decimal(self.minTradeAmount), rounding=ROUND_HALF_UP))

        if self.binanceApi.post_buy_order(self.name, self.orderSize):
            time.sleep(2)
            # get open position
            positions = self.binanceApi.get_open_positions(self.name)
            self.orderPrice = positions[1]

            self.profitPrice = (1.0 + self.percentageAux) * self.orderPrice
            self.profitPrice = Decimal(self.profitPrice)
            self.profitPrice = Decimal(self.profitPrice.quantize(Decimal(str(self.minPriceMove)), rounding=ROUND_HALF_UP))

            self.lossPrice = 0.92 * self.orderPrice
            self.status = BotStatus.ORDERBUYCONTROL

            self.binanceApi.post_buy_order(self.name, self.orderSize)
            self.binanceApi.post_buy_order_profit(self.name, self.orderSize, self.profitPrice)

            print("DEBUG: Buy Order ")
            print("DEBUG: Desire profit:", self.desireProfit)
            print("DEBUG: Leverage:", self.leverage)
            print("DEBUG: Order size:", self.orderSize)
            print("DEBUG: Buy at:", self.orderPrice)
            print("DEBUG: Profit at:", self.profitPrice)

        else:
            print("ERROR: opening Buy order")

    def place_order_buy(self, price):
        # self.numberTries += 1
        self.numberTries += 1
        self.percentageAux = (float(price) / self.orderPrice) - 1.0
        # self.percentageAux = self.percentageAux * 2.0
        
        print("A")
        self.leverage = Decimal(self.leverage)
        self.leverage = self.leverage * Decimal(2.0)
        self.maxLeverage = Decimal(self.maxLeverage)
        
        if self.leverage > self.maxLeverage:
            self.investUSDT = self.investUSDT * 2.0
            self.leverage = (self.binanceMinOrder * Decimal(price)) / self.investUSDT
            if self.leverage < 1.0:
                self.leverage = 1.0

            self.leverage = Decimal(self.leverage)
            self.orderSize = Decimal(self.investUSDT) * self.leverage / Decimal(price)
            self.orderSize = Decimal(self.orderSize.quantize(Decimal(str(self.minTradeAmount)), rounding=ROUND_HALF_UP))
        else:
            self.orderSize = self.orderSize + self.orderSize * Decimal(2.0)

        print("B")
        # set leverage
        self.leverage = Decimal(self.leverage.quantize(Decimal('0'), rounding=ROUND_HALF_UP))
        self.binanceApi.set_leverage(self.name, self.leverage)

        # self.orderSize = self.orderSize +  self.orderSize * Decimal(2.0)
        # if self.orderSize < 0:
        #     self.orderSize = self.orderSize * Decimal(-1.0)
        print("C")
        self.lossPrice = 0.95 * self.orderPrice
        self.status = BotStatus.ORDERBUYCONTROL
        
        print("D")
        self.profitPrice = (1.0 + self.percentageAux) * self.orderPrice
        self.profitPrice = Decimal(self.profitPrice)
        self.profitPrice = Decimal(self.profitPrice.quantize(Decimal(str(self.minPriceMove)), rounding=ROUND_HALF_UP))
        
        print("E")
        self.binanceApi.post_buy_order(self.name, self.orderSize)
        self.binanceApi.post_buy_order_profit(self.name, self.orderSize, self.profitPrice)

        positions= self.binanceApi.get_open_positions(self.name)
        
        print("F")
        self.orderPrice = Decimal(positions[1])
        
        print("-- Buy at", self.orderPrice)
        print("-- Order Size:", self.orderSize)
        print("-- Buy at", self.orderPrice)
        print("-- Profit at:", self.profitPrice)
        print("-----------------------------------")

    def place_order_sell(self,price):
        # self.numberTries += 1
        self.numberTries += 1
        self.percentageAux = 1.0 - (float(price) / self.orderPrice)
        # self.percentageAux = self.percentageAux * 2.0
        self.orderPrice = float(price)

        self.leverage = Decimal(self.leverage)
        self.leverage = self.leverage * Decimal(2.0)
        self.maxLeverage = Decimal(self.maxLeverage)
        
        if self.leverage > self.maxLeverage:
            self.investUSDT = self.investUSDT * 2.0
            self.leverage = (self.binanceMinOrder * Decimal(price)) / self.investUSDT
            if self.leverage < 1.0:
                self.leverage = 1.0

            self.leverage = Decimal(self.leverage)
            self.orderSize = Decimal(self.investUSDT) * self.leverage / Decimal(price)
            self.orderSize = Decimal(self.orderSize.quantize(Decimal(str(self.minTradeAmount)), rounding=ROUND_HALF_UP))
        else:
            self.orderSize = self.orderSize + self.orderSize * Decimal(2.0)

        # set leverage
        self.leverage = Decimal(self.leverage.quantize(Decimal('0'), rounding=ROUND_HALF_UP))
        self.binanceApi.set_leverage(self.name, self.leverage)

        # if self.orderSize > 0:
        #     self.orderSize = self.orderSize * Decimal(-1.0)

        self.lossPrice = 1.05 * self.orderPrice
        self.status = BotStatus.ORDERSELLCONTROL

        self.profitPrice = (1.0 - self.percentageAux) * self.orderPrice
        self.profitPrice = Decimal(self.profitPrice)
        self.profitPrice = Decimal(self.profitPrice.quantize(Decimal(str(self.minPriceMove)), rounding=ROUND_HALF_UP))

        self.binanceApi.post_sell_order(self.name, self.orderSize)
        self.binanceApi.post_sell_order_profit(self.name, self.orderSize, self.profitPrice)

        print("-- Sell at", self.orderPrice)
        print("-- Order Size:", self.orderSize)
        print("-- Sell at", self.orderPrice)
        print("-- Profit at:", self.profitPrice)
        print("-----------------------------------")

    def process_coin_price_V2(self,price:'float' = None):

                if self.status == BotStatus.NOTDEFINED:
                    self.status = BotStatus.PLACEORDERFIRSTSELL

                if self.status ==  BotStatus.PLACEORDERFIRSTBUY:
                    self.place_order_first_buy(price)

                if self.status ==  BotStatus.PLACEORDERFIRSTSELL:
                    # place first sell order
                    self.place_order_first_sell(price)

                if self.status == BotStatus.ORDERBUYCONTROL:
                    if float(price) <= (self.orderPrice * (1.0 - self.percentageAux)):
                        self.status = BotStatus.PLACEORDERSELL

                if self.status == BotStatus.ORDERSELLCONTROL:
                    print(float(price),self.orderPrice,(self.orderPrice * (1.0 + self.percentageAux))
                    if float(price) >= (self.orderPrice * (1.0 + self.percentageAux)):
                        self.status = BotStatus.PLACEORDERBUY

                if self.status == BotStatus.PLACEORDERBUY:
                    self.place_order_buy(price)

                if self.status == BotStatus.PLACEORDERSELL:
                    self.place_order_sell(price)

        # print(float(dt.close))

