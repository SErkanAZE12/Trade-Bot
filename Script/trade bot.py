import telebot
from telebot import types
import hashlib
import json
import time
import hmac
from urllib.parse import urlparse
import requests


access_id = "ED0373F98215493E852C5743B523DDFC"  # Replace with your access id
secret_key = "835050EB6DA7C2A26122371F554806A3AF1ADA86E243A742"  # Replace with your secret key


class RequestsClient(object):
    HEADERS = {
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
        "X-COINEX-KEY": "",
        "X-COINEX-SIGN": "",
        "X-COINEX-TIMESTAMP": "",
    }

    def __init__(self):
        self.access_id = access_id
        self.secret_key = secret_key
        self.url = "https://api.coinex.com/v2"
        self.headers = self.HEADERS.copy()

    # Generate your signature string
    def gen_sign(self, method, request_path, body, timestamp):
        prepared_str = f"{method}{request_path}{body}{timestamp}"
        signature = hmac.new(
            bytes(self.secret_key, 'latin-1'),
            msg=bytes(prepared_str, 'latin-1'),
            digestmod=hashlib.sha256
        ).hexdigest().lower()
        return signature

    def get_common_headers(self, signed_str, timestamp):
        headers = self.HEADERS.copy()
        headers["X-COINEX-KEY"] = self.access_id
        headers["X-COINEX-SIGN"] = signed_str
        headers["X-COINEX-TIMESTAMP"] = timestamp
        headers["Content-Type"] = "application/json; charset=utf-8"
        return headers

    def request(self, method, url, params={}, data=""):
        req = urlparse(url)
        request_path = req.path

        timestamp = str(int(time.time() * 1000))
        if method.upper() == "GET":
            # If params exist, query string needs to be added to the request path
            if params:
                query_params = []
                for item in params:
                    if params[item] is None:
                        continue
                    query_params.append(item + "=" + str(params[item]))
                query_string = "?{0}".format("&".join(query_params))
                request_path = request_path + query_string

            signed_str = self.gen_sign(
                method, request_path, body="", timestamp=timestamp
            )
            response = requests.get(
                url,
                params=params,
                headers=self.get_common_headers(signed_str, timestamp),
            )

        else:
            signed_str = self.gen_sign(
                method, request_path, body=data, timestamp=timestamp
            )
            response = requests.post(
                url, data, headers=self.get_common_headers(signed_str, timestamp)
            )

        if response.status_code != 200:
            raise ValueError(response.text)
        return response


request_client = RequestsClient()


def get_spot_market(sym):
    request_path = "/spot/market"
    params = {"market": sym}
    response = request_client.request(
        "GET",
        "{url}{request_path}".format(url=request_client.url, request_path=request_path),
        params=params,
    )
    return response


def get_spot_balance():
    request_path = "/assets/spot/balance"
    response = request_client.request(
        "GET",
        "{url}{request_path}".format(url=request_client.url, request_path=request_path),
    )
    return response

def get_futures_balance():
    request_path = "/assets/futures/balance"
    response = request_client.request(
        "GET",
        "{url}{request_path}".format(url=request_client.url, request_path=request_path),
    )
    return response
def get_deposit_address(sym,sym_chain):
    request_path = "/assets/deposit-address"
    params = {"ccy": sym, "chain": sym_chain}

    response = request_client.request(
        "GET",
        "{url}{request_path}".format(url=request_client.url, request_path=request_path),
        params=params,
    )

    return response


# Function to place a limit or market order
def put_limit(symbol, side, amount, price=None):
    request_path = "/spot/order"

    # 'limit' for limit orders (when price is provided), 'market' for market orders (no price)
    data = {
        "market": symbol,
        "market_type": 'spot',
        "side": side,  # 'buy' or 'sell'
        "type": 'limit' if price else 'market',  # 'limit' or 'market' order
        "amount": amount,
        "price": price,  # Only required for limit orders
        "client_id": "user1",
        "is_hide": True,
    }
    data = json.dumps(data)
    response = request_client.request(
        "POST",
        "{url}{request_path}".format(url=request_client.url, request_path=request_path),
        data=data,
    )
    return response
def put_future_limit(crypto,side,amount,price=None):

  request_path="/futures/order"
  data={
      "market":crypto,
      "market_type":"FUTURES",
      "side":side,
      "type":'market' if not price else 'limit',
      "amount":amount,
      "price":price,
      "client_id":"user1",
      "is_hide": True,
  }
  data = json.dumps(data)
  response = request_client.request(
        "POST",
        "{url}{request_path}".format(url=request_client.url, request_path=request_path),
        data=data,
    )
  return response
def transfer(from_account_type,to_account_type,amount):
  request_url="/assets/transfer"
  data={
      "from_account_type":from_account_type.upper(),
      "to_account_type":to_account_type.upper(),
      "ccy":"USDT",
      "amount":amount
  }
  data = json.dumps(data)
  response = request_client.request(
        "POST",
        "{url}{request_path}".format(url=request_client.url, request_path=request_url),
        data=data,
    )
  return response

def cancel_all_f_orders(market,side):
  request_url="/futures/cancel-all-order"
  data={
      "market":market,
      "market_type":"FUTURES",
      "side":side.lower()
  }
  data=json.dumps(data)
  response = request_client.request(
        "POST",
        "{url}{request_path}".format(url=request_client.url, request_path=request_url),
        data=data,
    )
  return response
def cancel_order_by_id(market,order_id):
  request_url="/futures/cancel-all-order"
  data={
      "market":market,
      "market_type":"FUTURES",
      "order_id":order_id
  }
  data=json.dumps(data)
  response = request_client.request(
        "POST",
        "{url}{request_path}".format(url=request_client.url, request_path=request_url),
        data=data,
    )
  return response
def close_position(market,side,amount,price=None):
    request_urll="/futures/close-position"
    data={
        "market":market,
        "market_type":"FUTURES",
        "type":"market" if not price else "limit",
        "price":price,
        "side":side,
        "amount":amount,
        "client_id":"user1",
        "is_hide":True,

    }
    data=json.dumps(data)
    response = request_client.request(
          "POST",
          "{url}{request_path}".format(url=request_client.url, request_path=request_urll),
          data=data,
      )
    return response
def get_pending_position(market):
  request_url="/futures/pending-position"
  params={
      "market":market,
      "market_type":"FUTURES",
      "page":1,
      "limit":5
  }
  response = request_client.request(
          "GET",
          "{url}{request_path}".format(url=request_client.url, request_path=request_url),
          params=params,
      )
  return response
class BOT(RequestsClient):

  def __init__(self, token):
        super().__init__()

        self.TOKEN = token
        self.bot = telebot.TeleBot(self.TOKEN)
        self.bot.message_handler(commands=['start'])(self.hello)
        self.bot.message_handler(commands=['deposit'])(self.deposit)
        self.bot.message_handler(commands=['s_balance'])(self.get_spot_balance2)
        self.bot.message_handler(commands=['buy'])(self.order_buy)
        self.bot.message_handler(commands=['sell'])(self.order_sell)
        self.bot.message_handler(commands=['f_balance'])(self.get_future_balance2)
        self.bot.message_handler(commands=['f_buy'])(self.order_future_buy)
        self.bot.message_handler(commands=['f_sell'])(self.order_future_sell)
        self.bot.message_handler(commands=['transfer'])(self.usdt_transfer)
        self.bot.message_handler(commands=['cancel_all'])(self.cancel_all_future_orders)
        self.bot.message_handler(commands=['cancel_by_id'])(self.cancel_f_order_by_id)
        self.bot.message_handler(commands=['close_position'])(self.close_future_position)
        self.bot.message_handler(commands=['current_position'])(self.current_position)
        # self.bot.message_handler(commands=['get_info'])(self.get_info)

  def hello(self, msg):
        self.bot.send_message(msg.chat.id, 'Hello, this is a personal trade bot for @serkanAZE')
        self.show_menu(msg)

  def deposit(self, msg):
        try:
            self.bot.send_message(msg.chat.id, 'pls write crypto name ')
            self.bot.register_next_step_handler(msg,self.get_crypto)
        except Exception as e:
                  self.bot.send_message(msg.chat.id, f"Error: {e}")


  def get_crypto(self,msg,):
      try:

                  sym=msg.text

                  self.bot.send_message(msg.chat.id,'pls write chain name ')
                  self.bot.register_next_step_handler(msg, lambda msg: self.get_chain(msg, sym))


      except Exception as e:
                  self.bot.send_message(msg.chat.id, f"Error: {e}")
  def get_chain(self,msg,sym):
    try:
      sym_chain=msg.text
      response_3 = get_deposit_address(sym, sym_chain).json()

      if response_3['data']['memo'] == '':
              r_response_3 = f"Address: {response_3['data']['address']}"
              self.bot.send_message(msg.chat.id, r_response_3)
      else:
              r_response_3_with_memo = f"Address: {response_3['data']['address']} and Memo: {response_3['data']['memo']}"
              self.bot.send_message(msg.chat.id, r_response_3_with_memo)

    except Exception as e:
                  self.bot.send_message(msg.chat.id, f"Error: {e}")


  def get_spot_balance2(self, msg):
    try:
      response=get_spot_balance().json()
      # data=response['data']
      data=response.get('data',[])
      # balance_data=data[0:]
      balance=''
      for item in data:
        if isinstance(item,dict):
          balance_f=', '.join([f"{key}:{value}"for key,value in item.items()])
          balance+=f"\n{balance_f}\n"
        # balance += f"\n{item}\n"  # Show the entire item to understand its structure


      self.bot.send_message(msg.chat.id,f'Your balance:\n{balance}' )
        # self.bot.send_message(msg.chat.id, ")
    except Exception as e:
                  self.bot.send_message(msg.chat.id, f"Error: {e}")

  def get_future_balance2(self, msg):
    try:
      response=get_futures_balance().json()
      # data=response['data']
      data=response.get('data',[])
      # balance_data=data[0:]
      balance=''
      for item in data:
        if isinstance(item,dict):
          balance_f=', '.join([f"{key}:{value}"for key,value in item.items()])
          balance+=f"\n{balance_f}\n"
        # balance += f"\n{item}\n"  # Show the entire item to understand its structure


      self.bot.send_message(msg.chat.id,f'Your future balance:\n{balance}' )
        # self.bot.send_message(msg.chat.id, ")
    except Exception as e:
                  self.bot.send_message(msg.chat.id, f"Error: {e}")


  def order_buy(self,msg,):
    self.bot.send_message(msg.chat.id, 'pls write crypto name(use ex for canseling)')
    self.bot.register_next_step_handler(msg,self.get_buy_crypto)


  def get_buy_crypto(self,msg):
    try:
      if msg.text!='ex':
        crypto=msg.text
        self.bot.send_message(msg.chat.id, 'pls write amount(use ex for canseling)')
        self.bot.register_next_step_handler(msg, lambda msg: self.get_buy_amount(msg, crypto))
      else:
        self.hello(msg)
    except Exception as e:
      self.bot.send_message(msg.chat.id,f"error{e}")

  def get_buy_amount(self,msg,crypto):
    try:
      if msg.text!='ex':
        amount=float(msg.text)
        self.bot.send_message(msg.chat.id, 'pls write price(use ex for canseling)')
        self.bot.register_next_step_handler(msg, lambda msg: self.get_buy_price(msg, crypto, amount))
      else:
        self.hello(msg)
    except ValueError as ve:
      self.bot.send_message(msg.chat.id, f"Error: {ve}")


  import json

  def get_buy_price(self, msg, crypto, amount):
    try:
        # If the message text is not 'ex', proceed to get the price
        if msg.text != 'ex':
            try:
                price = float(msg.text)
                self.bot.send_message(msg.chat.id, f'You want to buy {crypto} at {price}')

                # Call to an external function 'put_limit' to place a buy order
                response = put_limit(crypto, 'buy', amount, price)
                response_data = response.json()

                if response.status_code == 200:
                    # Format the response data for better readability
                    order = json.dumps(response_data, indent=4)
                    self.bot.send_message(msg.chat.id, 'Order successfully submitted')
                    self.bot.send_message(msg.chat.id, order)
                else:
                    # Handle API error with a more detailed message
                    error_message = response.get('message', 'Unknown Error')
                    error_code = response.get('code', 'No code available')
                    self.bot.send_message(msg.chat.id, f"Error in submitting order: {error_message} (Code: {error_code})")

            except ValueError:
                # Handle cases where msg.text cannot be converted to a float
                self.bot.send_message(msg.chat.id, "Invalid price entered. Please enter a numeric value.")
            except Exception as e:
                # Handle any unexpected errors
                self.bot.send_message(msg.chat.id, f"An error occurred: {str(e)}")
        else:
            # If message text is 'ex', call another function
            self.hello(msg)

    except Exception as e:
        # Catch any unexpected errors in the outer try block
        self.bot.send_message(msg.chat.id, f"An unexpected error occurred: {str(e)}")

#for sell
  def order_sell(self,msg,):
    self.bot.send_message(msg.chat.id, 'pls write crypto name(use ex for canseling)')
    self.bot.register_next_step_handler(msg,self.get_sell_crypto)


  def get_sell_crypto(self,msg):
    try:
      if msg.text!='ex':
        crypto=msg.text
        self.bot.send_message(msg.chat.id, 'pls write amount(use ex for canseling)')
        self.bot.register_next_step_handler(msg, lambda msg: self.get_sell_amount(msg, crypto))
      else:
        self.hello(msg)
    except Exception as e:
      self.bot.send_message(msg.chat.id,f"error{e}")

  def get_sell_amount(self,msg,crypto):
    try:
      if msg.text!='ex':
        amount=float(msg.text)
        self.bot.send_message(msg.chat.id, 'pls write price(use ex for canseling)')
        self.bot.register_next_step_handler(msg, lambda msg: self.get_sell_price(msg, crypto, amount))
      else:
        self.hello(msg)
    except ValueError as ve:
      self.bot.send_message(msg.chat.id, f"Error: {ve}")


  def get_sell_price(self,msg,crypto,amount):
    try:
      if msg.text!='ex':
        try:
          price=float(msg.text)
          self.bot.send_message(msg.chat.id, f'you want to sell{crypto} at {price} ')
          response=put_limit(crypto,'sell',amount,price).json()

          if response.get('code') == 200:
              self.bot.send_message(msg.chat.id, 'your selling order submited')
          else:
              self.bot.send_message(msg.chat.id, f"error: {response.get('message', 'خطای نامشخص')}{response.get('code')}")

        except Exception as e:
          self.bot.send_message(msg.chat.id, f"Error: {e}")
      else:
        self.hello(msg)

    except Exception as e:
        self.bot.send_message(msg.chat.id, f"Error: {e}")

  #futures buy or sell
  #buy
  def order_future_buy(self,msg,):
      self.bot.send_message(msg.chat.id, 'pls write crypto name(use ex for canseling)')
      self.bot.register_next_step_handler(msg,self.get_buy_f_crypto)
  def get_buy_f_crypto(self,msg):
    try:
      if msg.text!='ex':
        try:
          crypto=msg.text
          self.bot.send_message(msg.chat.id, 'pls write amount(use ex for canseling)')
          self.bot.register_next_step_handler(msg, lambda msg: self.get_buy_f_amount(msg, crypto))
        except Exception as e:
          self.bot.send_message(msg.chat.id, f"Error: {e}")
      else:
        self.hello(msg)

    except Exception as e:
      self.bot.send_message(msg.chat.id,f"error{e}")
  def get_buy_f_amount(self,msg,crypto):
    try:
      if msg.text!='ex':
        try:
          amount=float(msg.text)
          self.bot.send_message(msg.chat.id, 'pls write price(use ex for canseling or sk for skip)')
          self.bot.register_next_step_handler(msg, lambda msg: self.get_buy_f_price(msg, crypto, amount))
        except Exception as e:
          self.bot.send_message(msg.chat.id, f"Error: {e}")
      else:
        self.hello(msg)
    except ValueError as ve:
      self.bot.send_message(msg.chat.id, f"Error: {ve}")
  def get_buy_f_price(self,msg,crypto,amount):
    try:
      if msg.text!='ex':
        if msg.text!='sk':
          price=float(msg.text)
          # self.bot.send_message(msg.chat.id, f'you want to buy{crypto} in {price}. ')
          response=put_future_limit(crypto,'buy',amount,price)
          response_data=response.json()
          if response.status_code == 200:
                self.bot.send_message(msg.chat.id, 'order sucessfully submitted')
                self.bot.send_message(msg.chat.id, json.dumps(response_data,indent=4) )
        else:
          response=put_future_limit(crypto,'buy',amount)
          response_data=response.json()
          if response.status_code == 200:
                self.bot.send_message(msg.chat.id, 'order sucessfully submitted')
                self.bot.send_message(msg.chat.id, json.dumps(response_data,indent=4) )
      else:
        self.hello(msg)
    except Exception as e:
        self.bot.send_message(msg.chat.id, f"Error: {e}")

#sell
  def order_future_sell(self,msg,):
      self.bot.send_message(msg.chat.id, 'pls write crypto name(use ex for canseling)')
      self.bot.register_next_step_handler(msg,self.get_sell_f_crypto)
  def get_sell_f_crypto(self,msg):
    try:
      if msg.text!='ex':
        try:
          crypto=msg.text
          self.bot.send_message(msg.chat.id, 'pls write amount(use ex for canseling)')
          self.bot.register_next_step_handler(msg, lambda msg: self.get_sell_f_amount(msg, crypto))
        except Exception as e:
          self.bot.send_message(msg.chat.id, f"Error: {e}")
      else:
        self.hello(msg)

    except Exception as e:
      self.bot.send_message(msg.chat.id,f"error{e}")
  def get_sell_f_amount(self,msg,crypto):
    try:
      if msg.text!='ex':
        
          amount=float(msg.text)
          self.bot.send_message(msg.chat.id, 'pls write price(use ex for canseling or use sk to skip)')
          self.bot.register_next_step_handler(msg, lambda msg: self.get_sell_f_price(msg, crypto, amount))

      else:
        self.hello(msg)
    except ValueError as ve:
      self.bot.send_message(msg.chat.id, f"Error: {ve}")
  def get_sell_f_price(self,msg,crypto,amount):
    try:
      
      if msg.text!='ex':
        
          if msg.text!='sk':
            price=float(msg.text)
            # self.bot.send_message(msg.chat.id, f'you want to buy{crypto} in {price}. ')
            response=put_future_limit(crypto,'sell',amount,price)
            response_data=response.json()
            if response.status_code == 200:
                  self.bot.send_message(msg.chat.id, 'order sucessfully submitted')
                  self.bot.send_message(msg.chat.id, json.dumps(response_data,indent=4) )
          else:
            response=put_future_limit(crypto,'sell',amount)
            response_data=response.json()
            if response.status_code == 200:
                  self.bot.send_message(msg.chat.id, 'order sucessfully submitted')
                  self.bot.send_message(msg.chat.id, json.dumps(response_data,indent=4) )
      else:
          self.hello(msg)

    except Exception as e:
        self.bot.send_message(msg.chat.id, f"Error: {e}")
  #transfer usdt between FUTURE SPOT
  def usdt_transfer(self,msg):
    self.bot.send_message(msg.chat.id, 'pls write from account type(use ex for canseling)')
    self.bot.register_next_step_handler(msg,self.get_from_account)
  def get_from_account(self,msg):
    from_account=msg.text
    if from_account!='ex':
      self.bot.send_message(msg.chat.id, 'pls write to account type(use ex for canseling)')
      self.bot.register_next_step_handler(msg, lambda msg: self.get_to_account(msg,from_account))
    else:
      self.hello(msg)
  def get_to_account(self,msg,from_account):
    to_account=msg.text
    if to_account!='ex':
      self.bot.send_message(msg.chat.id, 'pls write amount(use ex for canseling)')
      self.bot.register_next_step_handler(msg, lambda msg: self.get_amount(msg,from_account,to_account))
    else:
      self.hello(msg)
  def get_amount(self,msg,from_account,to_account):
    amount=float(msg.text)
    if amount!='ex':
      response=transfer(from_account,to_account,amount)
      response_data=response.json()
      if response.status_code == 200:
        self.bot.send_message(msg.chat.id, 'transfered')
        self.bot.send_message(msg.chat.id, json.dumps(response_data,indent=4))
      else:
        self.bot.send_message(msg.chat.id, f"error: {response.get('message', 'خطای نامشخص')}{response.get('code')}")
    else:
      self.hello(msg)

  #CANCEL ALL FUTURES ORDERS
  def cancel_all_future_orders(self,msg):
    #def cancel_all_f_orders(market,side):
    self.bot.send_message(msg.chat.id, 'pls write crypto name with pair(use ex for canseling)')
    self.bot.register_next_step_handler(msg,self.get_market)

  def get_market(self,msg):
    market=msg.text
    self.bot.send_message(msg.chat.id, 'pls write side(use ex for canseling)')
    self.bot.register_next_step_handler(msg, lambda msg: self.get_side(msg,market))

  def get_side(self,msg,market):
    side=msg.text
    if side!='ex':
      response=cancel_all_f_orders(market,side)
      if response.status_code==200:
        self.bot.send_message(msg.chat.id,json.dumps(response.json(),indent=4))
      else:
        self.bot.send_message(msg.chat.id,f"error{response.get('message','unknown error')}{response.get('code')}")
    else:
      self.hello(msg)

  #CANCEL  FUTURES ORDERS by id
  def cancel_f_order_by_id(self,msg):
    #def cancel_all_f_orders(market,side):
    self.bot.send_message(msg.chat.id, 'pls write crypto name with pair(use ex for canseling)')
    self.bot.register_next_step_handler(msg,self.get_crypto_name)

  def get_crypto_name(self,msg):
    market=msg.text
    self.bot.send_message(msg.chat.id, 'pls write order_id(use ex for canseling)')
    self.bot.register_next_step_handler(msg, lambda msg: self.get_order_id(msg,market))

  def get_order_id(self,msg,market):
    order_id=msg.text
    if order_id!='ex':
      response=cancel_order_by_id(market,order_id)
      if response.status_code==200:
        self.bot.send_message(msg.chat.id,json.dumps(response.json(),indent=4))
      else:
        self.bot.send_message(msg.chat.id,f"error{response.get('message','unknown error')}{response.get('code')}")
    else:
      self.hello(msg)
#close position
# def close_position(market,price,amount):

  def close_future_position(self,msg):
      self.bot.send_message(msg.chat.id,"crypto name(use ex for canceling):")
      self.bot.register_next_step_handler(msg,self.get_crypto_name2)

  def get_crypto_name2(self,msg):
    try:
      if msg.text!='ex':
        crypto=msg.text
        self.bot.send_message(msg.chat.id,"side(use ex for canceling):")
        self.bot.register_next_step_handler(msg,lambda msg: self.get_close_side(msg,crypto))
      else:
        self.hello(msg)
    except Exception as e:
      self.bot.send_message(msg.chat.id,f"error{e}")
  
  def get_close_side(self,msg,crypto):
    try:
      if msg.text!='ex':
        side=msg.text
        self.bot.send_message(msg.chat.id,"pls write amount(use ex for canseling)")
        self.bot.register_next_step_handler(msg,lambda msg: self.get_close_amount(msg,crypto,side))
      else:
        self.hello(msg)
    except Exception as e:
      self.bot.send_message(msg.chat.id, f"Error: {e}")

  def get_close_amount(self,msg,crypto,side):
    try:
      if msg.text!='ex':
        amount=float(msg.text)
        self.bot.send_message(msg.chat.id,"price(use ex for canceling or sk for skip):")
        self.bot.register_next_step_handler(msg,lambda msg: self.get_close_price(msg,crypto,side,amount))
      else:
          self.hello(msg)
    except Exception as e:
      self.bot.send_message(msg.chat.id, f"Error: {e}")
  def get_close_price(self,msg,crypto,side,amount):
    try:
      if msg.text!='ex':
        if msg.text!='sk':
          price=float(msg.text)
          response=close_position(crypto,side,amount,price)
          response_data=response.json()
          if response.status_code==200:
            self.bot.send_message(msg.chat.id,json.dumps(response_data,indent=4))
        else:
          response=close_position(crypto,side,amount)
          response_data=response.json()
          if response.status_code==200:
            self.bot.send_message(msg.chat.id,json.dumps(response_data,indent=4))

      else:
        self.hello(msg)
    except Exception as e:
      self.bot.send_message(msg.chat.id, f"Error: {e}")

  def current_position(self,msg):
    self.bot.send_message(msg.chat.id, 'pls write crypto name(use ex for canseling)')
    self.bot.register_next_step_handler(msg,self.get_position_crypto_name)

  def get_position_crypto_name(self,msg):
    try:
      if msg.text!='ex':
        crypto=msg.text
        response=get_pending_position(crypto)
        print(response)  # Add this line to see the full API response

        response_data=response.json()
        if response.status_code==200:

          self.bot.send_message(msg.chat.id,json.dumps(response_data,indent=4))
        else:
          self.bot.send_message(msg.chat.id,f"error{response.get('message','unknown error')}{response.get('code')}")
      else:
        self.hello(msg)
    except Exception as e:
      self.bot.send_message(msg.chat.id,f"error{e}")


  def show_menu(self, msg):
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    buttons=[
        types.KeyboardButton('/start'),
        types.KeyboardButton('/s_balance'),
        types.KeyboardButton('/buy'),
        types.KeyboardButton('/sell'),
        types.KeyboardButton('/deposit'),
        types.KeyboardButton('/f_balance'),
        types.KeyboardButton('/f_buy'),
        types.KeyboardButton('/f_sell'),
        types.KeyboardButton('/transfer'),
        types.KeyboardButton('/cancel_all'),
        types.KeyboardButton('/cancel_by_id'),
        types.KeyboardButton('/close_position'),
        types.KeyboardButton('/current_position'),
        # types.KeyboardButton('/get_info'),
    ]
    markup.add(*buttons)
    self.bot.send_message(msg.chat.id, 'Choose an option:', reply_markup=markup)
  def run(self):
        self.bot.polling()


if __name__ == '__main__':
    token='7899984092:AAGCUoGD881wKehxXKXLITv9MeyJk6RaE9E'
    test=BOT(token)
    test.run()

