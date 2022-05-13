# imports
from flask import Flask, url_for, render_template, redirect, request, json, make_response # more imports can be added 
import pymongo
import random
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
    #result = rpc_connection.batch_([["listassets"]])
    assets = json.load(open('trade.json', "r"))
    result = assets["assets"]
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
    return render_template("index.html", assets=result, lenassets=len(result), lenwall=len_bg)
# Command Section (TESTING, DELETE ONCE SEND WORKS!) - Deleted
# @app.route('/command/<command>')
# def cmd(command):
#     try:
#         result = rpc_connection.batch_([[command]])
#     except:
#         return {"error":"command not found"}
#     return {"success": True, "data":result}
@app.route('/send', methods=["GET", "POST"])
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
    tradedb.insert_one({"uid":uid(), "pair":pair, "type":"trade", "amount":tradep1_amt})
            
if __name__ == "__main__":
    app.run(debug=True)

