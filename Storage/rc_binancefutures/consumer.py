import pika
from configparser import ConfigParser
import logging
import json
import sys
from kafka import KafkaProducer

from binance_f import RequestClient
from binance_f.model import *
from binance_f.constant.test import *
from binance_f.base.printobject import *

logging.basicConfig(format='%(asctime)s %(message)s')

def config(filename, section):
   parser = ConfigParser()
   parser.read(filename)
   rmq = {}
   if parser.has_section(section):
      params = parser.items(section)
      for param in params:
         rmq[param[0]] = param[1]
   else:
      raise Exception('Section {0} not found in the {1} file'.format(section, filename))
   return rmq

def main():
   if len(sys.argv) != 2 or sys.argv[1] != "-kp":
      logging.error("Incorrect args. Program: consumer.py -kp <ip:port>")
   
   ip_kp = sys.argv[2]
   logging.warning("IP:PORT KAFKA PRODUCER: " + ip_kp)
   producer = KafkaProducer(bootstrap_servers=ip_kp)
   params = config('config.ini', 'rabbitmq')
   connection = pika.BlockingConnection(pika.ConnectionParameters(host=params['url']))
   channel = connection.channel()
   channel.queue_declare(queue=params['queue'])

   def callback(ch, method, properties, body):
      message = json.loads(body)
      logging.warning(" [x] Received %r" % message["symbol"])
      p_binance = config('config.ini', 'apibinance')
      request_client = RequestClient(api_key=p_binance["apikey"], secret_key=p_binance["secret"])
      result = request_client.get_candlestick_data(symbol="BTCUSDT", interval=CandlestickInterval.MIN1, startTime=None, endTime=None, limit=1)
      
      future = producer.send(message["symbol"], b'example_message')
      result = future.get(timeout=10)
      logging.warning(result)

   channel.basic_consume(queue=params['queue'], on_message_callback=callback, auto_ack=True)
   channel.start_consuming()

if __name__ == '__main__':
   main()