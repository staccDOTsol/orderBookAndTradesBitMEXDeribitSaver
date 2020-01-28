URL	 = 'https://www.deribit.com'#ctrl+h!!!!!
import os
KEY	 = os.getenv('KEY')
SECRET  = os.getenv('SECRET')
from deribit_api	import RestClient

client = RestClient( KEY, SECRET, URL )
import json
import websocket
try:
	import thread
except ImportError:
	import _thread as thread
import time
from datetime import datetime
import pymongo

pyclient = pymongo.MongoClient("mongodb://coindex:" + os.getenv('db_pass') + "@localhost:27017/")

pydb = pyclient["deribit"]
import calendar;

def on_message(ws, message):
	mJson = json.loads(message)

	if 'notifications' in mJson:
		
		if mJson['notifications'][0]['message'] == 'order_book_event':
			
			result=(mJson['notifications'][0]['result'])
			
			ts = calendar.timegm(time.gmtime())
			result['timeStamp'] = ts
			
			col = pydb["order_book"]
			col.insert_one(result)
			#print(mJson['notifications'][0]['message'])

		if mJson['notifications'][0]['message'] == 'trade_event':
			trades = mJson['notifications'][0]['result']
			now = datetime.now()
			col = pydb["trade"]
			col.insert_many(trades)
			print(mJson['notifications'][0]['message'])

		
	else:
		print(mJson)
	
def on_error(ws, error):
	print(error)

def on_close(ws):
	print("### closed ###")
		
def on_open(ws):
	def run(*args):
		global sendCount
		
		args = {
			"instrument": ["BTC-PERPETUAL"],
			"event": ["trade", "order_book"]
		};
		obj = { 
			"id": str(sendCount),
			"action": "/api/v1/private/subscribe",
			"arguments": args,
			"sig": client.generate_signature("/api/v1/private/subscribe", args) 
		};
		ws.send(json.dumps(obj))
		sendCount = sendCount + 1
		time.sleep(5)
		#ws.close()
		#print("thread terminating...")
	thread.start_new_thread(run, ())



sendCount = 0
import threading
from time import sleep
if __name__ == "__main__":
	websocket.enableTrace(True)
	ws = websocket.WebSocketApp("wss://www.deribit.com/ws/api/v1/",
							  on_message = on_message,
							  on_error = on_error,
							  on_close = on_close)
	ws.on_open = on_open
	ws.run_forever()
