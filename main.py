from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import time

# initializers

#rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8000"%("username", "password"))

#result = rpc_connection.batch_([["listassets"]])
i = 0
#print(len(result[0]))
# print(result[0])
# for results in range(len(result[0])):
#     print(result[0][i])
#     i+=1
import random
uid_string = ""
for i in range(0, 16):
    # pick a random letter from the array
    letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u",
               "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    b = random.randint(0, len(letters))
    try:
        letter = letters[b]
        print(letter)
        uid_string += letter
    except:
        pass
print(uid_string)