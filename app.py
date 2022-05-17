# imports
from flask import Flask, url_for, render_template, redirect, request, make_response # more imports can be added 
import pymongo
import random
import requests
import time
# from bitcoin import * 
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import json
# initializers
app = Flask(__name__)
rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8000"%("username", "password")) 
def get_database():
    from pymongo import MongoClient

    CONNECTION_STRING = "mongodb+srv://primitt:1016@primittdb.mvkeq.mongodb.net/"

    client = MongoClient(CONNECTION_STRING)

    return client['aviandex']
dbname = get_database()
tradedb = dbname["trades"]
def price(pair):
    pass
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
            blockcount = rpc_connection.batch_([["blockcount"]])
            break
        except:
            pass
    while True:
        try:
            assets = rpc_connection.batch_([["listmyassets"]])[0]
            break
        except:
            pass
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
    #     i+=1
    return render_template("index.html", assets=assets, lenassets=len(result), lenwall=len_bg, blockcount=blockcount)
# Command Section (TESTING, DELETE ONCE SEND WORKS!) - Deleted
# @app.route('/command/<command>')
# def cmd(command):
#     try:
#         result = rpc_connection.batch_([[command]])
#     except:
#         return {"error":"command not found"}
#     return {"success": True, "data":result}
#@app.route('/send', methods=["GET", "POST"])
def send():
    if request.method == "POST":
        addr = request.form["addr"]
        if addr == "":
            return redirect(url_for("index", message="Unable to send because no address", type="error"))
        else:
            try:
                result = rpc_connection.batch_([["sendtoaddress", addr, 5]])
            except Exception as e:
                return redirect(url_for("index", message="Unable to send because it was an invalid address" , type="error"))
            return redirect(url_for("index", message="Sent 5 Testnet Avian to <b>" + addr + "</b>", type="success"))
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
    uids = uid()
    while True:
        try:
            new_addr = rpc_connection.batch_([["getnewaddress", uids]])
            break
        except:
            pass
    while True:
        try:
            assets = rpc_connection.batch_([["listmyassets", tradep2]])
            break
        except:
            pass
    tradedb.insert_one({"uid":uids, "pair":pair, "type":"trade", "amountp1":tradep1_amt, "amountp2":tradep1_amt*price, "txid":"-", "txidaddress":new_addr, "address":request.cookies.get('wallet'), "status":"pending", "time":time.time()})
    return redirect(url_for("payment", uid=uids))
@app.route('/trade/<uid>', methods=["GET", "POST"])
def payment(uid):
    finds = tradedb.find({"uid":uid})
    finders = []
    for find in finds:
        finders.append(find)
    if finders == []:
        return redirect(url_for("index", message="Unable to find trade", type="error"))
    else:
        return render_template("trade.html", msgtype="incompletetx", uid=uid, pair=(finders[0]["pair"]).split("-"), amount=finders[0]["amount"], find=finders[0])
@app.route('/price/<pair>')
def price(pair):
    assets = json.load(open('trade.json', "r"))
    result = assets["assets"]
    all_assets = ''
    i = 0
    for i in range(len(result)): 
        if pair == result[i][0]:
            return result[i][2]
        i+=1
    return "Not Found"
@app.route('/get/status/<uid>', methods=["GET"])
def gettx(uid):
    # file = open("test.txt", "r")
    # contents = file.read()
    
    get_uid = tradedb.find({"uid":uid})
    get_ui = []
    for uids in get_uid:
        get_ui.append(uids)
    if get_ui == []:
        return {"error":"Unable to find trade"}
    else:
        result = requests.get("https://testnet.avn.network/ext/getaddress/" + get_ui[0]["txidaddress"][0]).json()
        try:
            txid = result["error"]
            return {"status":"pending"}
        except:
                txid_arr = result["last_txs"]
                txid = []
                for txids in txid_arr:
                    if txids["type"] == "vout":
                        txid.append(txids["addresses"])
                    else:
                        pass
                if txid == []:
                    return {"status":"pending"}
                else:
                    if get_ui[0]["status"] == "pending":
                                send_coin = rpc_connection.batch_([["sendfrom", "", get_ui[0]["address"], get_ui[0]["amount"]]])
                                print(send_coin)
                                tradedb.update_one({"uid":uid}, {"$set":{"txid":txid[0], "status":"complete"}})
                        #return {"status":"complete", "txid":txid[0], "balance":result["received"]}
            # except: 
            #     return {"error":"Unable to find TX"}
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)

