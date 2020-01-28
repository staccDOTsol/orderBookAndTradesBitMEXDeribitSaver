import os


USER = os.getenv('API_USER')
PASSWORD = os.environ.get('API_PASSWORD')


api_key	 = os.getenv('api_key')
api_secret  = os.getenv('api_secret')
import pymongo
data = None

pyclient = pymongo.MongoClient("mongodb://coindex:" + os.getenv('db_pass') + "@localhost:27017/")

pydb = pyclient["deribit"]
from bitmex_websocket import BitMEXWebsocket
from time import sleep
first = True
import calendar;
import time
trdMatchIDs = []
while True:
	ws = BitMEXWebsocket(endpoint="https://www.bitmex.com/api/v1", symbol="XBTUSD", api_key=api_key, api_secret=api_secret)

	try:
		while(ws.ws.sock.connected):

			depth = (ws.market_depth())
			asks = []
			bids = []
			for bidask in depth:
				if bidask['side'] == 'Buy':
					bids.append(bidask)
				else:
					asks.append(bidask)
			bidsnew = sorted(bids, key=lambda k: k['price']) 
			asksnew = sorted(asks, key=lambda k: k['price']) 
			bidsarr = []
			asksarr = []

			for i in range(0, 9):
				bidsarr.append(bidsnew[(i +1 ) *-1])
				asksarr.append(asksnew[i])
	
			ts = calendar.timegm(time.gmtime())
			result = {}
			result['bids'] = bidsarr
			result['asks'] = asksarr
			result['timeStamp'] = ts
			
			col = pydb["mex_order_book"]
			try:
				col.insert_one(result)
			except Exception as e:
				print(e)
			trades = (ws.recent_trades())
			tradesnew = []
			for t in trades:
				if t['trdMatchID'] not in trdMatchIDs:
					trdMatchIDs.append(t['trdMatchID'])
					tradesnew.append(t)
			#print(tradesnew)
			col = pydb["mex_trade"]
			try:
				col.insert_many(tradesnew)
			except Exception as e:
				print(e)
			
			sleep(1/2.5)
	except Exception as e:
		print(e)

ws.market_depth()
ws.recent_trades()

