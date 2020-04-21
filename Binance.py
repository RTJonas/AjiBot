import requests
import json
import decimal
import pandas as pd 
import hmac
import time

binance_keys={
	'api_key':'publicKey',
	'secret_key':'secretKey'
}

class Binance:
	def __init__(self):

		self.base = 'https://api.binance.com'

		self.endpoints = {
		"order":'/api/v1/order',
		"testOrder":'/api/v1/order/test',
		"allOrders":'/api/v1/allOrders',
		"klines":'/api/v1/klines',
		"exchangeInfo":'/api/v1/exchangeInfo'}

	# Getting all the symbols that are currently trading	
	def GetTradingSymbols(self):
		url = self.base + self.endpoints['exchangeInfo']

		try:
			response = requests.get(url)
			data = json.loads(response.text)
		except Exception as e:
			print("Exception occured when trying to access"+url)
			print(e)
			return []

		symbols_list = []

		for pair in data['symbols']:
			if pair['status']=='TRADING':
				symbols_list.append(pair['symbol'])

		return symbols_list

	def GetSymbolData(self, symbol:str, interval:str):

		#''' Gets trading data for each symbol '''

		params = '?&symbol='+symbol+'&interval='+interval

		url = self.base+self.endpoints['klines']+params

		# download data
		data = requests.get(url)
		dictionary = json.loads(data.text)

		# put in dataframe and clean-up
		df = pd.DataFrame.from_dict(dictionary)
		df = df.drop(range(6, 12), axis=1)

		# rename columns
		col_names = ['time', 'open', 'high', 'low', 'close', 'volume']
		df.columns = col_names

		# transform values from strings to floats
		for col in col_names:
		    df[col] = df[col].astype(float)

		return df

	def PlaceOrder(self, symbol:str,side:str,type:str,quantity:float,price:float,test:bool=True):
		#''' Place an order  '''	
		params = {
			'symbol':symbol,
			'side':side,
			'type':type,
			'timeInForce':'GTC',
			'quantity':quantity,
			'price':self.floatToString(price),
			'recWindow':5000,
			'timestamp': int(round(time.time()*1000))
		}

		self.signRequest(params)

		url = ''

		if test:
			url = self.base + self.endpoints['testOrder']
		else:
			url = self.base + self.endpoints['order']

		try:
			response = requests.post(url, params=params,headers={"X-MBX-APIKEY":binance_keys['api_key']})
		except:
			print("Exception occured while trying to place an order on"+url)
			print(e)
			response = {'code':'-1','msg':e}
			return None

		return json.loads(response.text)

	def CancelOrder(self, symbol:str, orderId:str):

		#''' Cancels order on a symbol based on a orderId'''	

		params = {
			'symbol':symbol,
			'orderId':orderId,
			'recWindow':5000,
			'timeStap':int(round(time.time()*1000))
		}

		self.signRequest(params)

		url = self.base + self.endpoints['order']

		try:
			response = requests.delete(url, params=params,headers={"X-MBX-APIKEY":binance_keys['api_key']})
		except:
			print("Exception occured while trying to cancel an order on"+url)
			print(e)
			response = {'code':'-1','msg':e}
			return None

	def GetOrderInfo(self, symbol:str,orderId:str):

	#''' Gets info on a symbol based on a orderId'''	

		params = {
			'symbol':symbol,
			'orderId':orderId,
			'recWindow':5000,
			'timeStap':int(round(time.time()*1000))
		}

		self.signRequest(params)

		url = self.base + self.endpoints['order']

		try:
			response = requests.get(url, params=params,headers={"X-MBX-APIKEY":binance_keys['api_key']})
		except:
			print("Exception occured while trying to get order info on"+url)
			print(e)
			response = {'code':'-1','msg':e}
			return None

		return json.loads(response.text)


	def GetAllOrderInfo(self, symbol:str,orderId:str):

	#''' Gets info on a all orders on a symbol'''	

		params = {
			'symbol':symbol,
			'timeStap':int(round(time.time()*1000))
		}

		self.signRequest(params)

		url = self.base + self.endpoints['allOrders']

		try:
			response = requests.get(url, params=params,headers={"X-MBX-APIKEY":binance_keys['api_key']})
		except:
			print("Exception occured while trying to get info on all orders"+url)
			print(e)
			response = {'code':'-1','msg':e}
			return None

		return json.loads(response.text)	

	def floatToString(self, f:float):

	#''' Converts the given float to string, without
	#	 resorting to the cientific notation  '''

		ctx = decimal.Context()
		ctx.prec = 12
		d1 = ctx.create_decimal(repr(f))
		return format(d1,'f')

	def signRequest(self,params:dict):

	#''' Sign the request to Binance API ''' maybe error

		query_string = '&'.join(["{}={}".format(d,params[d]) for d in params])
		signature = hmac.new(binance_keys['secret_keys'].encode('urf-8'),query_string.encode('utf-8'),hashlib.sha256)
		params['signature'] = signature.hexdigest()