item_name = {
        "D": "Daily necessities",
        "F": "Food",
        "E": "Eating out",
        "T": "Transportation expenses"
        }
# i = "i"

# s = [x for x in item_name.values()]
# item_name[i]
# try:
#     item_name[i]
#     print("hello")
# except:
#     print("error")

e = {
        "type": "message",
        "message": {
            "type": "text",
            "id": "525053001958686753",
            "quoteToken": "xXMb9de9Xd08isvQt2S0k_vBDKjMuFiVW7nsQIVqPw1-6RthHeQdkVRRBQb3j1ilps0fR29TWgL7xiqstFVa3FsSH0useJ7es8NJeJu5qL0dXBKpj6BsOen5w7Pli-SnH8v5feubQMfC__QZo1Ikvg",
            "text": "h"
            },
        "webhookEventId": "01J78F05CYTZAG9ZJCV5NMDVZ2",
        "timestamp": 1725787280709,
        "source": {
            "type": "user",
            "userId": "U24c03de7282b9e69f10336a619658278"
            },
        "replyToken": "e33e3e8aa64f41638765150185d4190e",
        "mode": "active"
        }
print(e.source.userId)
