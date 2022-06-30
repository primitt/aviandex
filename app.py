# imports
# more imports can be added
from flask import Flask, url_for, render_template, redirect, request, make_response
import pymongo
import random
import requests
import time
# from bitcoin import *
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import json
# initializers
app = Flask(__name__)
rpc_connection = AuthServiceProxy(
    "http://%s:%s@127.0.0.1:8000" % ("username", "password"), timeout=10000)


def get_database():
    from pymongo import MongoClient

    CONNECTION_STRING = "mongodb+srv://primitt:1016@primittdb.mvkeq.mongodb.net/"

    client = MongoClient(CONNECTION_STRING)

    return client['aviandex']


dbname = get_database()
tradedb = dbname["trades"]
assetdb = dbname["assets"]

def price(pair):
    pass
def check_tx(addr, txid, amt):
    tx = requests.get("https://testnet.avn.network/api/getrawtransaction?txid="+txid+"&decrypt=1").json()
    print(txid)
    vout = tx["vout"]
    for i in vout:
        if i["value"] > float(amt)-1 and i["value"] < float(amt)+1:
            print(i["scriptPubKey"]["addresses"][0])
            print(i["value"])
            addr_result = i["scriptPubKey"]["addresses"][0]
            return True
        else:
            "Wrong Amount"
    return "Idk man"
            
    

def uid():
    # make a array with all the lowercase letters of the alphabet
    uid_string = ""
    for i in range(0, 16):
        # pick a random letter from the array
        letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
                   "u",
                   "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        b = random.randint(0, len(letters))
        try:
            letter = letters[b]
            print(letter)
            uid_string += letter
        except:
            pass
    return uid_string
# dex start


@app.route('/')
def index():
    while True:
        try:
            blockcount = rpc_connection.batch_([["getblockcount"]])
            break
        except:
            rpc_connection = AuthServiceProxy(
            "http://%s:%s@127.0.0.1:8000" % ("username", "password"), timeout=10000)
                #assets = rpc_connection.batch_([["listmyassets"]])[0]
            # assets = {
            #     "DEX": 5000000.0000,
            #     "DEX!": 1
            # }
    asset = assetdb.find()
    buy_assets = []
    sell_assets = []
    for name in asset:
        if name["type"] == "buy":
            buy_assets.append(name["name"])
        if name["type"] == "sell":
            sell_assets.append(name["name"])
    #assets = json.load(open('trade.json', "r"))
    #result = assets["assets"]
    get_op = []
    i = 0
    try:
        len_bg = len(request.cookies.get("wallet"))
    except:
        len_bg = 0
    # if needed, use for now caching.
    # for results in range(len(list(result[0]))):
    #     split = result[0][i].split("/")
    #     if len(split) > 2: # no subassets for now
    #         pass
    #     else:
    #         get_op.append(result[0][i])
    #     i+=
    # key_list = [key for key in assets]
    # return "Printed"
    #return {"data":assets}
    return render_template("index.html", lenassets=len(buy_assets), lenwall=len_bg, blockcount=blockcount, assets=buy_assets, sell_assets=sell_assets, lensell=len(sell_assets))


@app.route('/connect', methods=["POST"])
def connectwallet():
    if request.method == "POST":
        wallet_addr = request.form["walletaddr"]
        if wallet_addr == "":
            return redirect("/", message="Unable to connect because no address", type="error")
        else:
            resp = make_response(redirect(url_for("index")))
            resp.set_cookie('wallet', wallet_addr)
            return resp


@app.route('/trade', methods=["POST"])
def trade():
    tradep1 = request.form["asset"]
    tradep1_amt = request.form["amount"]
    tradep2 = request.form["asset1"]
    pair = tradep1 + "-" + tradep2
    finds = assetdb.find({"pair":pair})
    time.sleep(1)
    find = []
    for foinds in finds:
        find.append(foinds)
    uids = uid()
    if find == []:
        return redirect("/", message="Not a tradable pair!", type="error")
    while True:
        try:
            new_addr = rpc_connection.batch_([["getnewaddress", uids]])
            break
        except:
            rpc_connection = AuthServiceProxy(
    "http://%s:%s@127.0.0.1:8000" % ("username", "password"), timeout=10000)
            continue
    assets = find[0]["liquidity"]
    while True:
            try:
                balance = rpc_connection.batch_([["getbalance"]])[0]
                break
            except:
                rpc_connection = AuthServiceProxy(
                "http://%s:%s@127.0.0.1:8000" % ("username", "password"), timeout=10000)
    price = float(balance)/float(assets)
    tradedb.insert_one({"uid": uids, "pair": pair, "type": "trade", "amountp1": tradep1_amt, "amountp2": float(tradep1_amt)*price,
                       "txid": "-", "txidaddress": new_addr, "address": request.cookies.get('wallet'), "status": "pending", "time": time.time()})
    return redirect(url_for("payment", uid=uids))


@app.route('/trade/<uid>', methods=["GET", "POST"])
def payment(uid):
    try:
        blockcount = rpc_connection.batch_([["getblockcount"]])[0]
        
    except:
        blockcount = "null"
    finds = tradedb.find({"uid": uid})
    finders = []
    for find in finds:
        finders.append(find)
    if finders == []:
        return redirect(url_for("index", message="Unable to find trade", type="error"))
    else:
        return render_template("trade.html", msgtype="incompletetx", uid=uid, pair=(finders[0]["pair"]).split("-"), amount=finders[0]["amountp1"], find=finders[0], amountp2=int(finders[0]["amountp2"]), blockcount=blockcount)


@app.route('/price/<pair>')
def price(pair):
    find = assetdb.find({"name":pair})
    finds = []
    for finders in find:
        finds.append(finders)
    if finds == []:
        return "Not Found"
    else:
        assets = finds[0]["liquidity"]
        while True:
            try:
                balance = rpc_connection.batch_([["getbalance"]])[0]
                break
            except:
                rpc_connection = AuthServiceProxy(
                "http://%s:%s@127.0.0.1:8000" % ("username", "password"), timeout=10000)
        pair2 = finds[0]["pair"].split("-")[1]
        pair2_liquidity = list(assetdb.find({"name":pair2}))[0]["liquidity"]
        if assets == "balance":
            price = float(balance)/float(pair2_liquidity)
        else:
            price = float(balance)/float(assets)
        return str(price)
    return "Not Found"
@app.route('/prices')
def prices():
    asset = assetdb.find()
    assets = []
    for name in asset:
        price = requests.get("http://127.0.0.1:8070/price/" + name["name"]).text
        assets.append([name["name"], price])
    return render_template("prices.html", assets=assets)

@app.route('/get/status/<uid>', methods=["GET"])
def gettx(uid):
    # file = open("test.txt", "r")
    # contents = file.read()

    get_uid = tradedb.find({"uid": uid})
    get_ui = []
    for uids in get_uid:
        get_ui.append(uids)
    if get_ui == []:
        return {"error": "Unable to find trade"}
    else:
        result = requests.get(
            "https://testnet.avn.network/ext/getaddress/" + get_ui[0]["txidaddress"][0]).json()
        try:
            txid = result["error"]
            return {"status": "pending"}
        except:
            txid_arr = result["last_txs"]
            txid = []
            for txids in txid_arr:
                if txids["type"] == "vout":
                    get_status = check_tx(addr=get_ui[0]["address"][0], txid=txids["addresses"], amt=get_ui[0]["amountp1"])
                    if get_status == True:
                        txid.append(txids["addresses"])
                        break
                else:
                    pass
            if txid == []:
                return {"status": "pending"}
            else:
                if get_ui[0]["status"] == "pending":
                    pairs = get_ui[0]["pair"].split("-")
                    while True:
                        try:
                            send_coin = rpc_connection.batch_(
                            [["transfer", pairs[1], int(get_ui[0]["amountp2"]), get_ui[0]["address"]]]) #this is our problem 
                            break
                        except:
                            rpc_connection = AuthServiceProxy(
    "http://%s:%s@127.0.0.1:8000" % ("username", "password"), timeout=10000)
                            continue
                    print(send_coin)
                    tradedb.update_one(
                        {"uid": uid}, {"$set": {"txid": txid[0], "status": "complete"}})
                    return {"status": "complete", "txid": txid[0]}
                else:
                    return {"status":"complete", "txid": get_ui[0]["txid"]}

                # return {"status":"complete", "txid":txid[0], "balance":result["received"]}
            # except:
            #     return {"error":"Unable to find TX"}
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8070)
