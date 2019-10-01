from django.test import TestCase, Client
from django.http import JsonResponse
import json
from . import models

PAGE_SIZE = 20

def populate_db_with_images():
   for i in range(1,101):
       name = "image_{:0>4}".format(i)
       data = name + ".jpg"
       photo = models.Photo(name = name, data = data)
       photo.save()

def populate_db_with_image_sizes():
    size_small = models.Size(label="small", price = 10, shipping_cost = 4.99)
    size_small.save()
    size_medium = models.Size(label="medium", price = 15, shipping_cost = 5.99)
    size_medium.save()
    size_large = models.Size(label="large", price = 20, shipping_cost = 7.99)
    size_large.save()

def populate_db_with_regions():
    for i in range(1, 11):
        region_name = "region_{:0>3}".format(i)
        region = models.Region(name = region_name)
        region.save()

def populate_db_with_countries():
    for i in range(1, 196):
        country_name = "country_{:0>4}".format(i)
        country = models.Country(name = country_name)
        country.save()

def dict_from_bytestring(bytestring):
    string_format = bytestring.decode()
    dict_format = json.loads(string_format)
    return dict_format

class TestPhotos(TestCase):

    def setUp(self):
        self.client = Client()
        populate_db_with_images()
        populate_db_with_image_sizes()
        populate_db_with_regions()
        populate_db_with_countries()
        self.photos_url = '/photo-store/photos/'
        self.order_url = '/photo-store/order/'
        self.correct_order_form_data = {
            "first_name" : "Marija",
            "last_name" : "Kalebota Kodzoman",
            "size_id" : "1",
            "photo_id" : "1",
            "region_id" : "1",
            "country_id" : "1",
            "email" : "marija@example.com",
            "phone" : "1111111111",
            "addr1" : "Marija Addr1",
            "addr2" : "Marija Addr2",
            "city" : "Los Angeles",
            "postal_code" : "22222",
        }

    def test_photos_get_status_code_200(self):
        response = self.client.get(self.photos_url)
        self.assertEquals(response.status_code, 200)

    def test_photos_post_status_code_400(self):
        response = self.client.post(self.photos_url)
        self.assertEquals(response.status_code, 400)

    def test_photos_return_jsonresponse(self):
        response = self.client.get(self.photos_url)
        self.assertEquals(response.__getitem__("Content-Type"), "application/json")

    def test_photos_return_only_photos_key(self):
        response = self.client.get(self.photos_url)
        response_dict = dict_from_bytestring(response.content)
        dict_keys = response_dict.keys()
        keys = list(dict_keys)
        self.assertEquals(len(keys), 1)
        self.assertEquals(keys[0], "photos")

    def test_photos_return_all_photos(self):
        response = self.client.get(self.photos_url)
        response_dict = dict_from_bytestring(response.content)
        number_of_photos_in_response = len(response_dict["photos"])
        number_of_photos_in_db = models.Photo.objects.count()
        self.assertEquals(number_of_photos_in_response, number_of_photos_in_db)

    def test_photos_return_correct_photos_when_paginated(self):
        response = self.client.get(self.photos_url + "?page=2")
        response_dict = dict_from_bytestring(response.content)
        number_of_photos_in_response = len(response_dict["photos"])
        self.assertEquals(number_of_photos_in_response, PAGE_SIZE)
    
    def test_photos_return_error_when_page_number_too_big(self):
        response = self.client.get(self.photos_url + "?page=6")
        self.assertEquals(response.content.decode(), "Page number is too big")

    def test_order_get_status_code_400(self):
        response = self.client.get(self.order_url)
        self.assertEquals(response.status_code, 400)

    def test_order_post_status_code_201(self):
        response = self.client.post(self.order_url, self.correct_order_form_data)
        self.assertEquals(response.status_code, 201)

    #TODO test responses with incorrect input
    #TODO do not allow DB to save if transaction was unsuccessful
