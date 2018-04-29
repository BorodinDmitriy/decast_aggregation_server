# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework import status
from tasks import *
from django.conf import settings
from models import Token, ServerTask
from serializers import TokenSerializer
from uuid import uuid1

import requests
import logging
import json
import pika
import threading

from kombu.pools import producers
from kombu import Exchange, Queue
from kombu import Connection

# 8000 - mobile-backend
# 8001 - rates
# 8002 - eirc_devices
# 8003 - aggregation server

logger = logging.getLogger('django')

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
def run():
    print("WAAAT")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    print(connection)
    channel.queue_declare(queue='test')
    channel.basic_consume(callback,
                      queue='test',
                      no_ack=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
    
def send_as_task(connection, args=(), kwargs={}):
    payload = { 'args': args, 'kwargs': kwargs}
    routing_key = 'sendtestrabbitmq2'
    queue = Queue('sendtestrabbitmq2', Exchange('default'), routing_key='sendtestrabbitmq2')

    print(payload)
    with Connection('amqp://guest:guest@localhost:5672//') as conn:

      # produce
      producer = conn.Producer(serializer='json')
      print(producer)
      return producer.publish(payload,exchange=Exchange('default'),routing_key='sendtestrabbitmq2',declare=[queue])


def check_token(token):
  try:
    checked_token = ''
    url = "http://localhost:8000/auth/api-token-verify/"
    headers = {'Content-Type' : 'application/json'}
    data = {'token' : str(token)}
    response = (requests.post(url, data=data)).json()
  
    checked_token = response.get('token')
    #non_field_errors = response['non_field_errors']
    #print(settings.JWT_AUTH)
  
    if (checked_token is None):
      return 0
    else:
      return 1
  except:
    return 0
  
def refresh_token(token):
  try:
    checked_token = ''
    url = "http://localhost:8000/auth/api-token-refresh/"
    headers = {'Content-Type' : 'application/json'}
    data = {'token' : str(token)}
    response = (requests.post(url, data=data)).json()
  
    checked_token = response.get('token')
    #non_field_errors = response['non_field_errors']
   
  
    if (checked_token is None):
      return 0
    else:
      return 1
  except:
    return 0

def check_eirc_token(token):
  try:
    checked_token = ''
    url = "http://localhost:8002/auth/api-token-verify/"
    headers = {'Content-Type' : 'application/json'}
    data = {'token' : str(token)}
    response = (requests.post(url, data=data)).json()
  
    checked_token = response.get('token')
    #non_field_errors = response['non_field_errors']
    #print(checked_token)
  
    if (checked_token is None):
      return 0
    else:
      return 1
  except:
    return 0
  
def refresh_eirc_token(token):
  try:
    checked_token = ''
    url = "http://localhost:8002/auth/api-token-auth/"
    headers = {'Content-Type' : 'application/json'}
    data = {'username' : 'decast_eirc', 'password': settings.APPS.get('decast_eirc')}
    response = (requests.post(url, data=data)).json()
  
    print(response.get('token'))
    if (response.get('token') is not None):
      checked_token = response.get('token')
      print("BLAAAAAA" )
      Token.objects.filter(name="decast_eirc").update(token=response.get('token'))
  
    if (checked_token is None):
      return 0
    else:
      return 1
  except:
    return 0
  


class CustomValidation(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred.'

    def __init__(self, detail, status_code):
        if status_code is not None:self.status_code = status_code
        if detail is not None:
            self.detail = {"detail": force_text(detail)}
        else: self.detail = {'detail': force_text(self.default_detail)}

# Create your views here.
  
    
# /worker/
class SendWorker(APIView):

  def get(self, request):
    SendResponse.apply_async()
    
    #t = threading.Thread(target=run)
    #t.start()
    

# /auth/send_report/
# for sending report from client
class SendAuthRep(APIView):

  def post(self, request):
    #SendResponse.apply_async()
    try:
      #a = SendAuthReport.delay(request.data,0)
      #print(a)
      #SendAuthReportChecker.delay(a, request.data, 0)
      #b = SendTestRabbitMQ2.delay(request.data,0)
      gu = uuid1().hex
      dat = request.data
      dat['guid'] = gu
      print("dat=")
      print(dat)
      ServerTask.objects.create(guid=str(gu),processed=0)
      b = SendTestRabbitMQ2.apply_async((dat,0),{},expires=60)
      print(b)
      SendAuthReportChecker.delay(b, dat, 0)
      
      #connection = Connection('amqp://guest:guest@localhost:5672//')
      #a = send_as_task(connection,args=(request.data,0), kwargs={})
      #print(a)

      return Response(status=status.HTTP_200_OK)
    except:
      return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# /devices/<id>/get_pay_bill/
class GetPayBill(APIView):
  
  def get(self,request,id):
    # report data
    report = {}
    report["personal_account"] = "0000-0000-0000-0000"
    report["reading"] = "000000"
    report["rate"] = "0.00"
    report["status"] = "False"
    #end report data
    result = {}
    result["personal_account"] = "-"
    result["consumption_volume"] = "-"
    result["rate"] = "-"
    result["value"] = "-"
    
    try:
      #Token.objects.filter(name="decast_eirc").update(token=result["rate"])
      #print(Token.objects.filter(name="decast_eirc"))
      token = Token.objects.get(name="decast_eirc")
      print(token)
      err = check_eirc_token(token)
      print('WAS')
      print(err)
      if (err == 0):
	print('WAS2')
	err = refresh_eirc_token(token)
        print(err)
        token = Token.objects.get(name="decast_eirc")
        print('WAS3')
        print(token)
        err = check_eirc_token(token)
        print(err)
	if (err == 0):
          print(report)
          SendGetPayBillReport.delay(json.dumps(report),0)
	  return Response(result,status=status.HTTP_401_UNAUTHORIZED)
    except:
      print(report)
      SendGetPayBillReport.delay(json.dumps(report),0)
      return Response(result,status=status.HTTP_401_UNAUTHORIZED)

    try:
      token = (request.META.get('HTTP_AUTHORIZATION')).split(' ', 1)[1]
      print(token)
      err = check_token(token)
      if (err == 0):
	err = refresh_token(token)
	if (err == 0):
          print(report)
          SendGetPayBillReport.delay(json.dumps(report),0)
	  return Response(result,status=status.HTTP_401_UNAUTHORIZED)
    except:
      print(report)
      SendGetPayBillReport.delay(json.dumps(report),0)
      return Response(result,status=status.HTTP_401_UNAUTHORIZED)
    
    
    try:
      try:
	url = 'http://localhost:8000/devices/' + str(id) + '/'
	logger.info("Getting device data: " + str(url))
	response = requests.get(url)
	result["personal_account"] = response.json()["personal_account"]
        report["personal_account"] = response.json()["personal_account"]
      except:
        print(report)
        SendGetPayBillReport.delay(json.dumps(report),0)
	return Response(result,status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      try:
	url = 'http://localhost:8000/devices/' + str(id) + '/'
	logger.info("Getting device data: " + str(url))
	response = requests.get(url)
	sent_reading = response.json()["sent_reading"]
	logger.info("Device's last reading: " + str(sent_reading))
      
	url = 'http://localhost:8000/devices/' + str(id) + '/readings/' + str(sent_reading) + '/'
	logger.info("Getting last reading value: " + str(url))
	response = requests.get(url)
	current_value = response.json()["value"]
	logger.info("Device's last reading value: " + str(current_value))
    
	url = 'http://localhost:8002/eirc_devices/' + str(id) + '/'
        headers = {'Authorization' : 'JWT ' + str(Token.objects.get(name="decast_eirc"))}
	logger.info("Getting eirc reading value: " + str(url))
	response = requests.get(url)
	eirc_value = response.json()["reading"]
	type = response.json()["type"]
	logger.info("Eirc's reading value: " + str(eirc_value))
    
	difference = long(current_value) - long(eirc_value)
	result["consumption_volume"] = str(difference)
        report["reading"] = result["consumption_volume"]
    
	try:
	  url = 'http://localhost:8001/rate/?type=' + str(type)
	  logger.info("Getting rate value: " + str(url))
	  response = requests.get(url)
	  rate = response.json()["value"]
	  result["rate"] = str(rate)
	  logger.info("Rate's value: " + str(rate))
	  result["value"] = float(difference * rate)
          report["rate"] = str(rate)
	except:
          print(report)
          SendGetPayBillReport.delay(json.dumps(report),0)
	  return Response(result,status=response.status_code)
      except:
        print(report)
        SendGetPayBillReport.delay(json.dumps(report),0)
	return Response(result,status=response.status_code)
      report["status"] = "True"
      print(report)
      SendGetPayBillReport.delay(json.dumps(report),0)
      return Response(result,status=response.status_code)
    except:
      logger.info("Error in getting pay bill")
      SendGetPayBillReport.delay(json.dumps(report),0)
      return Response(result,status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# /users/<id>/devices/
class DevicesByUserId(APIView):
  
  def isNum(self,data):
    try:
        print(int(data))
        return True
    except ValueError:
        return False
      
      
  def get(self,request,id):
    print(settings.APPS['decast_eirc'])

    token_eirc = Token.objects.get(name="decast_billing")
    print(token_eirc)
    try:
      token = (request.META.get('HTTP_AUTHORIZATION')).split(' ', 1)[1]
      print(token)
      err = check_token(token)
      if (err == 0):
	err = refresh_token(token)
	if (err == 0):
	  return Response(status=status.HTTP_401_UNAUTHORIZED)
    except:
      return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    
    try:
      url = 'http://localhost:8000/users/' + str(id) + '/devices/'
      logger.info("Getting devices by user id: " + str(url))
      response = requests.get(url)
      return Response(response.json(),status=response.status_code)
    except:
      logger.info("Error in getting devices by user id")
      return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  def post(self,request,id):
    response = {}
    result={}
    device={}
    device_id=0
    
    try:
      token = (request.META.get('HTTP_AUTHORIZATION')).split(' ', 1)[1]
      print(token)
      err = check_token(token)
      if (err == 0):
	err = refresh_token(token)
	if (err == 0):
	  return Response("Unauthorized",status=status.HTTP_401_UNAUTHORIZED)
    except:
      return Response("Unauthorized",status=status.HTTP_401_UNAUTHORIZED)
    
    try: 
      url = 'http://localhost:8000/users/' + str(id) + '/devices/'
      logger.info('Creating new device: ' + str(url))
      response = requests.post(url,data=request.data)
      device_id = response.json()
      if not self.isNum(str(device_id)):
	raise CustomValidation(device_id['detail'],status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      logger.info("Device id: " + str(device_id))
      
      url = 'http://localhost:8000/devices/' + str(device_id)
      logger.info('Getting new device data: ' + str(url))
      device = requests.get(url).json()
      logger.info("Device data: " + str(device_id))
      
      url = 'http://localhost:8000/devices/' + str(device_id) + '/readings/'
      logger.info('Setting init reading value : ' + str(url))
      response = requests.post(url,data={"value":"000000"})
    except:
      if (self.isNum(str(device_id))):
	url = 'http://localhost:8000/devices/' + str(device_id) + '/'
	logger.info("Deleting device by id: " + str(url))
	response = requests.delete(url)
	return Response(response,status=response.status_code)
      else:
	return Response(device_id['detail'],status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
    try:
      eirc_data={
	"id":device["id"],
	"type":"water",
	"reading":"000000",
	"personal_account":device["personal_account"],
	"serial_number":device["serial_number"]
	}
      try:
	url = 'http://localhost:8002/eirc_devices/'
	logger.info('Registering device in eirc: ' + str(url))
	response = requests.post(url,data=eirc_data)

	logger.info("Success.")
	return Response(device_id,status=response.status_code)
      except:
	if (self.isNum(str(device_id))):
	  url = 'http://localhost:8000/devices/' + str(device_id) + '/'
	  logger.info("Deleting device by id: " + str(url))
	  response = requests.delete(url)
	  return Response(response.json(),status=response.status_code)
    except:
      result['detail'] = "Error in creating new device by user id"
      logger.info("Error in creating new device by user id")
      return Response(result,status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
# /devices/<id>/change_device_account/
class ChangeDeviceAccount(APIView):
  def check_personal_account(self,personal_account):
    check_array = personal_account.split('-')
    print(check_array)
    length = len(check_array)
    if (length != 4):
      return 0
    else:
      for i in range(0,length):
	if (long(check_array[i]) == 0):
	  return 0
    return 1
  def put(self,request,id):
    # report data
    report = {}
    old = ''
    new = ''
    stts = ''
    # report data end
    try:
      token = (request.META.get('HTTP_AUTHORIZATION')).split(' ', 1)[1]
      print(token)
      err = check_token(token)
      if (err == 0):
	err = refresh_token(token)
	if (err == 0):
	  return Response("Unauthorized",status=status.HTTP_401_UNAUTHORIZED)
    except:
      return Response("Unauthorized",status=status.HTTP_401_UNAUTHORIZED)
    
    
    try:
      if not (self.check_personal_account(request.data["personal_account"])):
	return Response("Incorrect personal_account",status=status.HTTP_400_BAD_REQUEST)
    except:
      return Response("Incorrect personal_account",status=status.HTTP_400_BAD_REQUEST)
    try:
      url = 'http://localhost:8000/devices/' + str(id) + '/'
      logger.info('Updating local device account: ' + str(url))
      response = requests.get(url)

      old = response.json()["personal_account"]
      report["old"] = old
      print(response.json()["personal_account"])

      url = 'http://localhost:8000/devices/' + str(id) + '/'
      logger.info('Updating local device account: ' + str(url))
      response = requests.put(url,data=request.data)

      new = response.json()["personal_account"]
      report["new"] = new
      print(response.json()["personal_account"])

      url = 'http://localhost:8002/eirc_devices/' + str(id) + '/'
      logger.info('Updating eirc device account: ' + str(url))
      try:
	response = requests.put(url,data=request.data)
      except:
        stts = "False"
        report["status"] = stts
        SendChangePersonalAccountReport.delay(json.dumps(report),0)

	UpdatePersonalAccount.delay('http://localhost:8003/devices/' + str(id) + '/change_device_account/',request.data)
	return Response(status=status.HTTP_200_OK)
      logger.info("Success.")
      stts = "True"
      report["status"] = stts
      SendChangePersonalAccountReport.delay(json.dumps(report),0)
      return Response(status=response.status_code)
    except:
      stts = "False"
      report["status"] = stts
      SendChangePersonalAccountReport.delay(json.dumps(report),0)

      logger.info("Error in updating devices account")
      return Response('Error in updating devices account ',status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# /devices/
class DeviceList(APIView):
  def get(self,request):
    url = 'http://localhost:8000/devices/'
    logger.info('Getting local device list: ' + str(url))
    response = requests.get(url)
    logger.info("Success.")
    return Response(response.json(),status=response.status_code)
# /devices/<id>/
class DeviceDetail(APIView):
  def check_personal_account(self,personal_account):
    check_array = personal_account.split('-')
    print(check_array)
    length = len(check_array)
    if (length != 4):
      return 0
    else:
      for i in range(0,length):
	if (long(check_array[i]) == 0):
	  return 0
    return 1
  def get(self,request,id):
    url = 'http://localhost:8000/devices/' + str(id) + '/'
    logger.info('Getting local device details: ' + str(url))
    response = requests.get(url)
    logger.info("Success.")
    return Response(response.json(),status=response.status_code)
  def put(self,request,id):
    try:
      if not (self.check_personal_account(request.data["personal_account"])):
	return Response("Incorrect personal_account",status=status.HTTP_400_BAD_REQUEST)
    except:
      return Response("Incorrect personal_account",status=status.HTTP_400_BAD_REQUEST)
    try:
      url = 'http://localhost:8000/devices/' + str(id) + '/'
      logger.info('Updating local device details: ' + str(url))
      response = requests.put(url,data=request.data)
      logger.info("Success.")
      return Response(response.json(),status=response.status_code)
    except:
      logger.info("Error in updating.")
      return Response('Error in updating local device . ',status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  def delete(self,request,id):
    url = 'http://localhost:8000/devices/' + str(id) + '/'
    logger.info('Deleting local device details: ' + str(url))
    response = requests.delete(url)
    logger.info("Success.")
    return Response(response,status=response.status_code)
  
# /devices/<id>/readings/
class DeviceReadings(APIView):
  def isNum(self,data):
    try:
        print(long(data))
        return True
    except ValueError:
        return False
  def check_reading(self,reading):
    return self.isNum(reading)
  def get(self,request,id):
    try:
      url = 'http://localhost:8000/devices/' + str(id) + '/readings/'
      logger.info('Getting local device readings: ' + str(url))
      response = requests.get(url)
      logger.info("Success.")
      return Response(response.json(),status=response.status_code)
    except:
      logger.info("Error in getting local device readings.")
      return Response('Error in getting local device reading. ',status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  def post(self,request,id):
    
    try:
      token = (request.META.get('HTTP_AUTHORIZATION')).split(' ', 1)[1]
      print(token)
      err = check_token(token)
      if (err == 0):
	err = refresh_token(token)
	if (err == 0):
	  return Response("Unauthorized",status=status.HTTP_401_UNAUTHORIZED)
    except:
      return Response("Unauthorized",status=status.HTTP_401_UNAUTHORIZED)
    
    
    try:
      if not (self.check_reading(request.data["value"])):
	return Response("Incorrect value",status=status.HTTP_400_BAD_REQUEST)
    except:
      return Response("Incorrect value",status=status.HTTP_400_BAD_REQUEST)
    try:
      url = 'http://localhost:8000/devices/' + str(id) + '/readings/'
      logger.info('Creating local device readings: ' + str(url))
      response = requests.post(url,data=request.data)
      return Response(response.json(),status=response.status_code)
    except:
      logger.info("Error in creating local device readings.")
      return Response('Error creating local device reading. ',status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
# /eirc_devices/
class EIRCDeviceList(APIView):
  def get(self,request):
    url = 'http://localhost:8002/eirc_devices/'
    logger.info('Getting eirc devices: ' + str(url))
    response = requests.get(url)
    logger.info("Success.")
    return Response(response.json(),status=response.status_code)
# /eirc_devices/<id>/
class EIRCDeviceDetail(APIView):
  def check_personal_account(self,personal_account):
    check_array = personal_account.split('-')
    print(check_array)
    length = len(check_array)
    if (length != 4):
      return 0
    else:
      for i in range(0,length):
	if (long(check_array[i]) == 0):
	  return 0
    return 1
  def get(self,request,id):
    url = 'http://localhost:8002/eirc_devices/' + str(id) + '/'
    logger.info('Getting eirc device details: ' + str(url))
    response = requests.get(url)
    logger.info("Success.")
    return Response(response.json(),status=response.status_code)
  def put(self,request,id):
    try:
      if not (self.check_personal_account(request.data["personal_account"])):
	return Response("Incorrect personal_account",status=status.HTTP_400_BAD_REQUEST)
    except:
      return Response("Incorrect personal_account",status=status.HTTP_400_BAD_REQUEST)
    try:
      url = 'http://localhost:8002/eirc_devices/' + str(id) + '/'
      logger.info('Updating eirc device details: ' + str(url))
      response = requests.put(url,data=request.data)
      logger.info("Success.")
      return Response(response.json(),status=response.status_code)
    except:
      logger.info('Error in updating eirc device details. ')
      return Response('Error in updating eirc device details. ',status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# /user/?email=demansen@yandex.ru
class UserByEmail(APIView):
  def get(self,request):
    url = 'http://localhost:8000/user/?email=' + request.GET['email']
    print(url)
    logger.info('Getting user id by email: ' + str(url))
    response = requests.get(url)
    logger.info("Success.")
    return Response(response.json(),status=response.status_code)
# /rates/
class RateList(APIView):
  def get(self,request):
    url = 'http://localhost:8001/rates/'
    logger.info('Getting rates: ' + str(url))
    response = requests.get(url)
    logger.info("Success.")
    return Response(response.json(),status=response.status_code)
# /rates/<id>/
class RateDetail(APIView):
  def isNum(self,data):
    try:
        print(float(data))
        return True
    except ValueError:
        return False
  def check_rate(self,rate):
    return self.isNum(rate)
  def get(self,request,id):
    url = 'http://localhost:8001/rates/' + str(id) + '/'
    logger.info('Getting rate details: ' + str(url))
    response = requests.get(url)
    logger.info("Success.")
    return Response(response.json(),status=response.status_code)
  def put(self,request,id):
    try:
      if not (self.check_personal_account(request.data["value"])):
	return Response("Incorrect value",status=status.HTTP_400_BAD_REQUEST)
    except:
      return Response("Incorrect value",status=status.HTTP_400_BAD_REQUEST)
    try:
      url = 'http://localhost:8001/rates/' + str(id) + '/'
      logger.info('Updating rate details: ' + str(url))
      response = requests.put(url,data=request.data)
      logger.info("Success.")
      return Response(response.json(),status=response.status_code)
    except:
      logger.info('Error in updating rate details. ')
      return Response('Error in updating rate details. ',status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# /rate/?type=gas
class RateByType(APIView):
  def get(self,request):
    url = 'http://localhost:8001/rate/?type=' + str(request.GET.get('type'))
    logger.info('Getting rate id by type: ' + str(url))
    response = requests.get(url)
    logger.info("Success.")
    return Response(response.json(),status=response.status_code)
