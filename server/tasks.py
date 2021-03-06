from __future__ import absolute_import, unicode_literals
import requests
import logging
import pika

from celery.decorators import task
from celery.registry import tasks
from celery.task import Task
from celery.result import AsyncResult

from rest_framework.response import Response
from rest_framework import status

from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu import Exchange, Queue
from kombu import Connection
from kombu.utils.debug import setup_logging

from .models import ServerTask

#logger = get_logger(__name__)

class Worker(ConsumerMixin):
  task_queues = [Queue('test', Exchange('default'), routing_key='test')]
  
  def check_email(email):
    return validate_email(email)
  
  def check_status(status):
    if (str(status) == 'True') or (str(status) == 'False'):
      return 1
    else:
      return 0
  def __init__(self, connection):
    self.connection = connection

  def get_consumers(self, Consumer, channel):
    return [Consumer(queues=[Queue('test', Exchange('default'), routing_key='test')], accept=['pickle','json'],callbacks=[self.process_task])]

  def process_task(self, body, message):
    try:
      print(body['args'])
      #task_status = body['args'][0]['task_status']
      data = body['args']
      gu = data[0]['guid']
      
      ServerTask.objects.filter(guid=str(gu)).update(processed=1)
      #if (task_status == 0):
      #  if (data[1] > 11):
      #    print('Task resend limit exceeded')
      #    data[1] = data[1] + 1 
      #    with Connection('amqp://guest:guest@localhost:5672//') as conn:

            # produce
      #      producer = conn.Producer(serializer='json')
      #      print(producer)
      #      producer.publish({ 'args': data, 'kwargs': body['kwargs']},exchange=Exchange('default'), routing_key='sendtestrabbitmq2',declare=[Queue('sendtestrabbitmq2', Exchange('default'), routing_key='sendtestrabbitmq2')])

      #print(body['args'])
      message.ack()
    except:
      #with Connection('amqp://guest:guest@localhost:5672//') as conn:

            # produce
     #       producer = conn.Producer(serializer='json')
      #      print(producer)
      #      producer.publish({ 'args': body['args'], 'kwargs': body['kwargs']},exchange=Exchange('default'), routing_key='sendtestrabbitmq2',declare=[Queue('sendtestrabbitmq2', Exchange('default'), routing_key='sendtestrabbitmq2')])
      return
    

@task
def create_device(url, method, urlData):
  try:
    if (method == "POST"):
      requests.post(url, data=urlData)
    else:
      requests.get(url, data=urlData)
  except:
    return 
  
class CreateDeviceTask(Task):
  
  def run(self, url, method, urlData):
    try:
      if (method == "POST"):
	requests.post(url, data=urlData)
      else:
	requests.get(url, data=urlData)
    except:
      return 
    
class UpdatePersonalAccount(Task):
  
  def run(self, url, urlData):
    try:
      requests.put(url, data=urlData)
    except:
      return 

class SendChangePersonalAccountReport(Task):

  def run(self,urlData, N):
    try:
      print(urlData)
      response = requests.post("http://localhost:8004/change_account_report/",data=urlData)
      print(response)
    except:
      print(N)
      if (N >= 11):
        print("Task run limit exceeded")
      else:
        self.delay(urlData,N+1)
      return

class SendGetPayBillReport(Task):

  def run(self,urlData,N):
    try:
      print(urlData)
      response = requests.post("http://localhost:8004/pay_bill_report/",data=urlData)
      print(response)
    except:
      print(N)
      if (N >= 11):
        print("Task run limit exceeded")
      else:
        self.delay(urlData,N+1)
      return

class SendAuthReport(Task):

  def run(self,urlData,N):
    try:
      print(self.request.id)
      print(urlData)
      response = requests.post("http://localhost:8004/auth_report/",data=urlData)
    except:
      print(N)
      #if (N >= 11):
      #  print("Task run limit exceeded")
      #else:
      #  self.delay(urlData,N+1)
      return
    
class SendAuthReportChecker(Task):

  def run(self, id, urlData, N):
    try:
      print(urlData)
      print(N)
      print(id)
      res = AsyncResult(id)
      print(res.status)
      m = ServerTask.objects.filter(guid=urlData['guid'])[0]
      print(m.guid)
      print("m.processed = " + str(m.processed))
      stat = int(str(m.processed))
      if (stat > 0):
        return
      else:
        print(N)
        if (N >= 5):
          print("Task run limit exceeded")
          return
        else:
          id_new = SendTestRabbitMQ2.apply_async((urlData,N+1),{},countdown=30, expires=60)
          self.apply_async((id, urlData,N+1),countdown=30)
    except:
      print("blet")
      return




class SendTestRabbitMQ(Task):

  def run(self,N):
      return
    #url = 'amqp://guest:guest@localhost:5672//'
    #params = pika.URLParameters(url)
    #connection = pika.BlockingConnection(params)
    #channel = connection.channel()

    #channel.queue_declare(queue='hello')

   # channel.basic_publish(exchange='',
    #                  routing_key='hello',
     #                 body='Hello World!')
    #print(" [x] Sent 'Hello World!'")
    #connection.close()

class SendTestRabbitMQ2(Task):

  def run(self,N,args):
      return

class SendResponse(Task):

  def run(self):
    with Connection('amqp://guest:guest@localhost:5672//') as conn:
        try:
            worker = Worker(conn)
            worker.run()
        except KeyboardInterrupt:
            print('bye bye')

@task
def Deliver(self, args):
  print(args)


tasks.register(Deliver)
tasks.register(CreateDeviceTask)
tasks.register(UpdatePersonalAccount)
tasks.register(SendChangePersonalAccountReport)
tasks.register(SendGetPayBillReport)
tasks.register(SendAuthReport)
tasks.register(SendAuthReportChecker)
tasks.register(SendTestRabbitMQ)
tasks.register(SendResponse)
