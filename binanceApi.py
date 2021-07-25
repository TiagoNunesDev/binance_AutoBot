from binance_f.model.constant import *
import time
import sys, os

class binanceLib:
    def __init__(self,**kwargs):
        self.client = kwargs["client"]

    def get_usdt_balance(self):
        try:
            sys.stdout = open(os.devnull, 'w')
            data = self.client.get_balance_v2()
            sys.stdout = sys.__stdout__
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)
            return False
        else:
            for dt in data:
                if(dt.asset == "USDT"):
                    return dt.balance

    def get_bnb_balance(self):
        try:
            sys.stdout = open(os.devnull, 'w')
            data = self.client.get_balance_v2()
            sys.stdout = sys.__stdout__
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)
            return False
        else:
            for dt in data:
                if(dt.asset == "BNB"):
                    return dt.balance

    def get_open_positions(self, cryptoCoin):
        try:
            sys.stdout = open(os.devnull, 'w')
            result = self.client.get_position()
            sys.stdout = sys.__stdout__

        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)
            return False
        else:
            for dt in result:
                if str(dt.symbol) == str(cryptoCoin):
                    return dt.positionAmt,dt.entryPrice,dt.markPrice,dt.leverage

    def set_leverage(self,cryptoCoin,leverage):
        try:
            sys.stdout = open(os.devnull, 'w')
            self.client.change_initial_leverage(symbol=cryptoCoin, leverage=leverage)
            sys.stdout = sys.__stdout__
            return True
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)
            return False


    def post_sell_order(self,cryptoCoin,quantity):
        try:
            sys.stdout = open(os.devnull, 'w')
            self.client.post_order(symbol=cryptoCoin, side=OrderSide.SELL,
                                           ordertype=OrderType.MARKET, closePosition=False, quantity=quantity)
            sys.stdout = sys.__stdout__
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)
            return False
        else:
            time.sleep(1)
            return True

    def post_sell_order_profit(self,cryptoCoin,quantity,price):
        try:
            sys.stdout = open(os.devnull, 'w')
            self.client.post_order(symbol=cryptoCoin, side=OrderSide.BUY,
                                           ordertype=OrderType.TAKE_PROFIT_MARKET, closePosition=True,
                                           quantity=quantity, stopPrice=price)
            sys.stdout = sys.__stdout__
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)
        else:
            time.sleep(1)
            return True

    def post_sell_order_take_loss(self,cryptoCoin,quantity,price):
        try:
            sys.stdout = open(os.devnull, 'w')
            self.client.post_order(symbol=cryptoCoin, side=OrderSide.BUY,
                                               ordertype=OrderType.STOP_MARKET, closePosition=True,
                                               quantity=quantity, stopPrice=price)
            sys.stdout = sys.__stdout__
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)
        else:
            time.sleep(1)
            return True


    def post_buy_order(self,cryptoCoin,quantity):
        try:
            sys.stdout = open(os.devnull, 'w')
            self.client.post_order(symbol=cryptoCoin, side=OrderSide.BUY,
                                               ordertype=OrderType.MARKET, closePosition=False, quantity=quantity)
            sys.stdout = sys.__stdout__
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)
        else:
            time.sleep(1)
            return True

    def post_buy_order_profit(self,cryptoCoin,quantity,price):
        try:
            sys.stdout = open(os.devnull, 'w')
            self.client.post_order(symbol=cryptoCoin, side=OrderSide.SELL,
                                               ordertype=OrderType.TAKE_PROFIT_MARKET, closePosition=True,
                                               quantity=quantity, stopPrice=price)
            sys.stdout = sys.__stdout__
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)
        else:
            time.sleep(1)
            return True

    def post_buy_order_take_loss(self,cryptoCoin,quantity,price):
        try:
            sys.stdout = open(os.devnull, 'w')
            self.client.post_order(symbol=cryptoCoin, side=OrderSide.SELL,
                                               ordertype=OrderType.STOP_MARKET, closePosition=True,
                                               quantity=quantity,stopPrice=price)
            sys.stdout = sys.__stdout__
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)
        else:
            time.sleep(1)
            return True

    def get_server_time(self):
        try:
            sys.stdout = open(os.devnull, 'w')
            result = self.client.get_servertime()
            sys.stdout = sys.__stdout__
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)
        else:
            return result

    def get_price_min1(self,cryptoCoin):
        try:
            sys.stdout = open(os.devnull, 'w')
            data = self.client.get_candlestick_data(symbol=cryptoCoin, interval=CandlestickInterval.MIN5, startTime=None,
                                                    endTime=None, limit=1)
            sys.stdout = sys.__stdout__
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)
            return False
        else:
            return data[0].close
            # for idx, row in enumerate(data):
            #     if idx == 0:
            #         members = [attr for attr in dir(row) if not callable(attr) and not attr.startswith("__")]
            #         for member_def in members:
            #             val_str = str(getattr(row, member_def))
            #             if member_def == 'close':
            #                 self.price = float(val_str)
            #             if member_def == 'openTime':
            #                 self.timestamp = int(val_str)
            #                 self.date = datetime.fromtimestamp((self.timestamp / 1000))
            # return True

    def get_open_orders(self,cryptoCoin):
        take_profit = 0
        take_loss = 0

        try:
            sys.stdout = open(os.devnull, 'w')
            data = self.client.get_open_orders(symbol=cryptoCoin)
            sys.stdout = sys.__stdout__
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)
        else:
            for orders in data:
                if orders.type == 'TAKE_PROFIT_MARKET':
                    take_profit += take_profit + 1
                if orders.type == 'STOP_MARKET':
                    take_loss += take_loss + 1

            return take_profit, take_loss

    def cancel_all_orders(self,cryptoCoin):
        try:
            sys.stdout = open(os.devnull, 'w')
            self.client.cancel_all_orders(symbol=cryptoCoin)
            sys.stdout = sys.__stdout__
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(e)
            return False
        else:
            time.sleep(1)
            return True
