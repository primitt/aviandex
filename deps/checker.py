import pymongo
import time
import requests
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
def get_database():
    from pymongo import MongoClient

    CONNECTION_STRING = "mongodb+srv://primitt:1016@primittdb.mvkeq.mongodb.net/"

    client = MongoClient(CONNECTION_STRING)

    return client['aviandex']


dbname = get_database()
tradedb = dbname["trades"]
assetdb = dbname["assets"]
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
while True:
    get_all_pending = tradedb.find({"status": "pending"})
    pending = list(get_all_pending)
    for items in pending:
        if time.time()-int(items["time"]) > 3600:
            tradedb.update_one(
                        {"uid": items["uid"]}, {"$set": {"status": "invalid"}})
            print("Invalid " + items["uid"])
        else:
            txid_address = items["txidaddress"][0]
            result = requests.get(
                    "https://testnet.avn.network/ext/getaddress/" + txid_address).json()
            try:
                txid = result["error"]
                print("Pending " + items["uid"])
            except:
                txid_arr = result["last_txs"]
                txid = []
                for txids in txid_arr:
                    if txids["type"] == "vout":
                        get_status = check_tx(addr=items["address"], txid=txids["addresses"], amt=items["amountp1"])
                        if get_status == True:
                            txid.append(txids["addresses"])
                            break
                    else:
                        pass
                if txid == []:
                    print("Still Pending " + items["uid"])
                else:
                    if items["status"] == "pending":
                        pairs = items["pair"].split("-")
                        while True:
                            try:
                                send_coin = rpc_connection.batch_(
                                [["transfer", pairs[1], int(items["amountp2"]), items["address"]]]) # Fixed! This was our problem. 
                                break
                            except:
                                rpc_connection = AuthServiceProxy(
        "http://%s:%s@127.0.0.1:8000" % ("username", "password"), timeout=10000)
                        print(send_coin)
                        tradedb.update_one(
                            {"uid": items["uid"]}, {"$set": {"txid": txid[0], "status": "complete"}})
                        print("Complete " + items["uid"])
                    else:
                        print("Complete " + items["uid"])
    print("Pending Check Done: " + str(time.time()))
    # Check 2 - Liquidity check
    assets = list(assetdb.find({"what":"asset"}))
    for items in assets:
        what = items["name"]
        while True:
            try:
                get_liquidity = rpc_connection.batch_([["listmyassets"]])
                break
            except:
                rpc_connection = AuthServiceProxy(
        "http://%s:%s@127.0.0.1:8000" % ("username", "password"), timeout=10000)
        liq = get_liquidity[0][what]
        assetdb.update_one({"name": what}, {"$set": {"liquidity": str(int(liq))}})
        print("Set " + what + " to " + str(liq))
    time.sleep(900)