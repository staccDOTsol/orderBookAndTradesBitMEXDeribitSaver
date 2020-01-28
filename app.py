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
def on_message2(ws, message):
	mJson = json.loads(message)

	if 'notifications' in mJson:

		if mJson['notifications'][0]['message'] == 'order_book_event':
			
			result=(mJson['notifications'][0]['result'])
			
			ts = calendar.timegm(time.gmtime())
			result['timeStamp'] = ts
			
			col = pydb["order_book"]
			col.insert_one(result)
			print(mJson['notifications'][0]['message'])


def on_message(ws, message):
	mJson = json.loads(message)

	if 'notifications' in mJson:
		
		if mJson['notifications'][0]['message'] == 'trade_event':
			trades = mJson['notifications'][0]['result']
			now = datetime.now()
			col = pydb["trade"]
			col.insert_many(trades)
			print(mJson['notifications'][0]['message'])

		else:
			print(mJson['notifications'][0]['message'])
	else:
		print(mJson)
	
def on_error(ws, error):
	print(error)

def on_close(ws):
	print("### closed ###")
	
 
	

def on_error2(ws, error):
	print(error)

def on_close2(ws):
	print("### closed ###")
def on_open(ws):
	def run(*args):
		global sendCount
		
		args = {
			"instrument": ["BTC-PERPETUAL"],
			"event": ["trade"]
		};
		obj = { 
			"id": str(sendCount),
			"action": "/api/v1/private/subscribe",
			"arguments": args,
			"sig": client.generate_signature("/api/v1/private/subscribe", args) 
		};
		ws.send(json.dumps(obj))
		sendCount = sendCount + 1
		time.sleep(1)
		#ws.close()
		#print("thread terminating...")
	thread.start_new_thread(run, ())


def on_open2(ws):
	def run(*args):
		global sendCount
		args = {
			"instrument": ["BTC-PERPETUAL"],
			"event": ["order_book"],
			"depth": 10
		};

		obj = { 
			"id": str(sendCount),
			"action": "/api/v1/private/subscribe",
			"arguments": args,
			"sig": client.generate_signature("/api/v1/private/subscribe", args) 
		};

		ws.send(json.dumps(obj))
		sendCount = sendCount + 1
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
	wst = threading.Thread(target=ws.run_forever)
	wst.daemon = True
	wst.start()

 
	ws2 = websocket.WebSocketApp("wss://www.deribit.com/ws/api/v1/",
							  on_message = on_message2,
							  on_error = on_error2,
							  on_close = on_close2)
	ws2.on_open = on_open2
	wst2 = threading.Thread(target=ws2.run_forever)
	wst2.daemon = True
	wst2.start()
	conn_timeout = 5
	
		

	msg_counter = 0
	while True:
		while not ws.sock.connected:
			sleep(1)
		while ws.sock.connected:
			sleep(1)
			msg_counter += 1
		ws.close()
		ws.on_open = None
		del ws


		ws = websocket.WebSocketApp("wss://www.deribit.com/ws/api/v1/",
								  on_message = on_message,
								  on_error = on_error,
								  on_close = on_close)
		ws.on_open = on_open
		wst = threading.Thread(target=ws.run_forever)
		wst.daemon = True
		wst.start()
		while not ws.sock.connected:
			sleep(1)
		
		msg_counter = 0

		ws2.on_open = None
		del ws2

		ws2 = websocket.WebSocketApp("wss://www.deribit.com/ws/api/v1/",
								  on_message = on_message2,
								  on_error = on_error2,
								  on_close = on_close2)
		ws2.on_open = on_open2
		wst2 = threading.Thread(target=ws2.run_forever)
		wst2.daemon = True
		wst2.start()
		while not ws2.sock.connected:
			sleep(1)
		
		msg_counter = 0

		