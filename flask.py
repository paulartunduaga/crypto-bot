import json
from flask import Flask, Response
from flask import request
import buy_script
import sell_script

app = Flask(__name__)

SSL_DISABLE = True


@app.route('/buy', methods=['POST'])
def buy():
    if request.json == None:
        return 'NO SIGNAL'
    else:
        return buy_script.auth_and_buy()

@app.route('/sell', methods=['POST'])
def sell():
    if request.json == None:
        return 'NO SIGNAL'
    else:
        return sell_script.auth_and_sell()


if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0", port=xxxx)