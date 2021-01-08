# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
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

import logging

app = Flask(__name__)

cors = CORS(app, resource={r"/*":{"origins": "*"}})

def record_loop():
    while True:
        print("OK")
        time.sleep(2)

def main():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    p = Process(target=record_loop)
    p.start()
    main()
    p.join()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
