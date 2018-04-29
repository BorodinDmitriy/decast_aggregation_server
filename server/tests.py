# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.reverse import reverse
from django.test import TestCase,Client
from rest_framework import status
from rest_framework.test import APITestCase,APIClient
# Create your tests here.
class ChangeDeviceAccountTestCase(APITestCase):
   def setUp(self):
    self.url = "/devices/1/change_device_account/"
    self.account={
      'personal_account' : 'test'
      }
   def test_rate_put_good(self):
    response = self.client.put(
            self.url,
            self.account
        )
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
   def test_rate_put_bad(self):
    del self.account['personal_account'] 
    response = self.client.put(
            self.url,
            self.account
        )
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class DeviceListTestCase(APITestCase):
  def setUp(self):
    self.url = "/devices/"
  def test_rate_get_good(self):
    response = self.client.get(
            self.url
        )
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    
class DeviceDetailTestCase(APITestCase):
  def setUp(self):
    self.url = "/devices/1/"
  def test_rate_get_good(self):
    response = self.client.get(
            self.url
        )
    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
  def test_rate_put_good(self):
    response = self.client.put(
            self.url
        )
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
  def test_rate_delete_good(self):
    response = self.client.delete(
            self.url
        )
    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class DeviceReadingsTestCase(APITestCase):
  def setUp(self):
    self.url = "/devices/1/readings/"
  def test_rate_get_good(self):
    response = self.client.get(
            self.url
        )
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
  def test_rate_post_good(self):
    response = self.client.post(
            self.url
        )
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
class EIRCDeviceListTestCase(APITestCase):
  def setUp(self):
    self.url = "/eirc_devices/"
  def test_rate_get_good(self):
    response = self.client.get(
            self.url
        )
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    
class EIRCDeviceDetailTestCase(APITestCase):
  def setUp(self):
    self.url = "/eirc_devices/1/"
    self.account={
      'personal_account' : 'test'
      }
  def test_rate_get_good(self):
    response = self.client.get(
            self.url
        )
    self.assertEqual(response.status_code, status.HTTP_200_OK)
  def test_rate_put_good(self):
    response = self.client.put(
            self.url
        )
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    
class RateListTestCase(APITestCase):
  def setUp(self):
    self.url = "/rates/"
  def test_rate_get_good(self):
    response = self.client.get(
            self.url
        )
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    
class RateDetailTestCase(APITestCase):
  def setUp(self):
    self.url = "/rates/1/"
    self.account={
      'personal_account' : 'test'
      }
  def test_rate_get_good(self):
    response = self.client.get(
            self.url
        )
    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
  def test_rate_put_good(self):
    response = self.client.put(
            self.url
        )
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class DevicesByUserIdTestCase(APITestCase):
  def setUp(self):
    self.url = "/users/1/devices/"
    self.account={
      'personal_account' : 'test'
      }
    self.eirc_data={
	"id":"1",
	"type":"water",
	"reading":"000000",
	"personal_account":"1",
	"serial_number":"1"
	}
  def test_rate_get_good(self):
    response = self.client.get(
            self.url
        )
    self.assertEqual(response.status_code, status.HTTP_200_OK)
  def test_rate_post_good(self):
    response = self.client.post(
            self.url,self.eirc_data
        )
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)