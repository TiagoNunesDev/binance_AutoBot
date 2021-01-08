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
import  math
import time

import logging

app = Flask(__name__)

cors = CORS(app, resource={r"/*":{"origins": "*"}})

@app.route("/", methods=['GET'])
def index():
    return "<h1>Hello World!</h1>"

def main():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
    print("ola")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
