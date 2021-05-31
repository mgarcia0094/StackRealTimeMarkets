import pika
from configparser import ConfigParser
import psycopg2
import logging
from datetime import datetime
import json

logging.basicConfig(format='%(asctime)s %(message)s')

def config(filename='config.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db

def get_symbols():
   """ Connect to the PostgreSQL database server """
   conn = None
   symbols = []
   try:
      params = config('config.ini', 'postgresql')
      conn = psycopg2.connect(**params)
      cur = conn.cursor()
      cur.execute('SELECT symbol from symbols')
      symbols_sql = cur.fetchall()
      symbols = [ seq[0] for seq in symbols_sql ]
      cur.close()
   except (Exception, psycopg2.DatabaseError) as error:
      logging.error(error)
   finally:
      if conn is not None:
         conn.close()
   return symbols

def main():
   paramsrmq = config('config.ini', 'rabbitmq')
   connection = pika.BlockingConnection(pika.ConnectionParameters(paramsrmq['url']))
   channel = connection.channel()
   symbols = get_symbols()
   channel.queue_declare(queue=paramsrmq['queue'])
   for symbol in symbols:
      now = datetime.now()
      timestamp = datetime.timestamp(now)
      
      dict_symbol = {}
      dict_symbol["symbol"] = symbol
      dict_symbol["timestamp"] = timestamp
      
      json_object = json.dumps(dict_symbol, indent = 4)
      logging.warning('PUSH ' + json_object)

      channel.basic_publish(exchange='', routing_key=paramsrmq['queue'], body=json_object)
   
   connection.close()

if __name__ == "__main__":
   main()
