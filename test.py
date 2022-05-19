from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import time
import json

# initializers

rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8000"%("username", "password"), timeout=200)
file1 = open("balance.txt", "r")
while True:
        with open('balance.txt', "r") as f:
            intof_currentid = rpc_connection.batch_([["getbalance"]])
        with open('balance.txt', "w") as f:
            f.write(str(intof_currentid[0]))
        time.sleep(60)
    
