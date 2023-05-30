from datetime import datetime, timedelta
from mongo import *
from order import placeBuyOrderMarketNSE, orderHistory, PlaceSellOrderMarketNSE

support = [43583,44300]
resistance = [43682,44360]
expiry = "2023-06-01"
target = 10
stoppLoss = 2.5
client = ConnectDB()
db = client["algoTrading"]
orderPlaced = False

def fetchData(data):
    # print(data,'from fetch data')
    if data["instrument_token"] != 260105:
        checkTargetAndSL(data)
    if data['instrument_token'] == 260105:
        return checkCondition(support, resistance, data['last_price'], data['instrument_token'])
    return False

def checkCondition(support,resistance,tradingprice,istToken):
    for sup in support:
        # print('from support for',tradingprice,sup,(tradingprice - sup))
        if (sup <= tradingprice<=sup+100):
            return placeOrder(tradingprice, istToken, "CE")
            # return True
    
    for res in resistance:
        # print('from res for',tradingprice)
        if( res-10<=tradingprice<= res):
            print('oreder placed put',tradingprice)
            return

    return

def checkTargetAndSL(data):
    print(data,'from checkTarget and sl')
    collection = db["orders"]
    result = collection.find({"instrument_token" : 12833794})
    # print(result)
    result = list(result)
    print(result,'resultttttttt')
    if(len(result)> 1):
        print("PANIC SOMETHING HAS GONE WRONG CLOSE ALL TRADES")
    if(len(result) == 1):
        stpLss = result[0]["stopLoss"]
        target = result[0]["target"]
        purchasePrice = result[0]["price"]
        currentPrice = data["last_price"]
        print("purchase price=",purchasePrice,"current price=", data["last_price"],"stpLss=",stpLss)
        if(purchasePrice <= currentPrice):
            print("TRAIL stpLss HERE TILL PURCHASE PRICE")
            collection.update_one(
                {
                    "indexName" : "BANKNIFTY",
                    "status": "Active"
                },
                {
                    "$set":{"stopLoss":purchasePrice},
                    "status":"trailingSL"
                })
        if (stpLss >= data["last_price"] or target <= data["last_price"]):
            print("EXECUTE SELL ORDER")
            orderId = PlaceSellOrderMarketNSE("YESBANK",1)
            orderData = orderHistory(orderId)
            orderTime = orderData[len(orderData)-1]['order_timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            obj = {
                "orderId": orderId,
                "instrument_token": data["instrument_token"],
                "qty": 1,
                "price": orderData[len(orderData)-1]['average_price'],
                "executedAt": orderTime,
                "status": "Closed"
            }
            collection.update_one({
                "indexName" : "BANKNIFTY"
            }, {
                "$set": {
                    "sellOrder": obj,
                    "status": "Closed"
                    }
            })
        print(stpLss, target,'sl and targettttttttt')
    return

def placeOrder(price, token,type):
    # print("From order placed")
    collection = db["orders"]
    status = collection.find_one({"indexName" : "BANKNIFTY"},{"status":1,"_id":0})
    # print(status,'statussssssss')
    # below not is to handle syntax and not condition
    if status == None:
        # print("from status == None")
        # print('from elseeeeeeee place order')
        strike = selectStrike(token,price,type)
        # orderId = placeBuyOrderMarketNSE("YESBANK",1)
        # print(orderId,'orderIdddddd')
        # orderData = orderHistory(orderId)
        # print(orderData[len(orderData)-1]['average_price'],'orderDataaaaaaa',orderData[len(orderData)-1]['order_timestamp'].strftime("%Y-%m-%d %H:%M:%S"))
        # orderTime = orderData[len(orderData)-1]['order_timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        # purchasePrice = orderData[len(orderData)-1]['average_price']
        # sl = purchasePrice - (purchasePrice * stoppLoss)/100
        # tar = purchasePrice + (purchasePrice * target)/100
        # obj = { 
        #     "orderId":orderId,
        #     "instrument_token": strike[2],
        #     "parent_instrument_token": token,
        #     "indexAt": price,
        #     "strike": strike[0],
        #     "indexName": strike[1],
        #     "price": orderData[len(orderData)-1]['average_price'],
        #     "executedAt": orderTime,
        #     "stopLoss": sl,
        #     "target": tar,
        #     "status": "Active"
        # }
        # print(obj,'objjjjj from order',strike)
        obj = {
            "orderId" : "230529501186971",
            "instrument_token" : 12833794,
            "parent_instrument_token" : 260105,
            "indexAt" : 44429.3,
            "strike" : "BANKNIFTY2360144400CE",
            "indexName" : "BANKNIFTY",
            "price" : 16.2,
            "executedAt" : "2023-05-29 12:00:42",
            "stopLoss" : 15.795,
            "target" : 17.82,
            "status" : "Active"
        }
        collection.insert_one(obj)
        # print('after obj inserted in order collection')
        return strike[2]
    if(status["status"] == "Active" or status["status"] == "onHold"):
        print('from iffffff place order')
        if( status["status"] == "Active"):
            print("from is active")
            # checkTargetAndSL(token)
        return False
    
    

def selectStrikePrice(ltp):
        
    str = (ltp / 100)
    sel = (ltp % 100)
    str = int(str)
    if sel > 50:
        str = str + 1
    str = (str * 100)
    return str


def selectStrike(instrument_token, ltp, type):
    if instrument_token == 260105:
        name = "BANKNIFTY"
        strike = selectStrikePrice(ltp)
        collection = db["instrumentNFO"]
        query = {
            "name": name,
            "strike": strike,
            "instrument_type": type,
            "expiry": expiry
        }
        projection = {
            "instrument_token": 1,
            "tradingsymbol": 1,
            "_id": 0
        }
        # print(query)
        result = collection.find_one(query, projection)
        symbol = result["tradingsymbol"]
        strikeToken = result["instrument_token"]
        return (symbol,name,strikeToken)


# selectStrikePrice(40720)
