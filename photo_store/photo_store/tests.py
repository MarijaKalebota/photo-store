import json

from django.http import JsonResponse
from django.test import Client, TestCase

from . import models

PAGE_SIZE = 20


def populate_db_with_images():
    for i in range(1, 101):
        name = "image_{:0>4}".format(i)
        data = "{}.jpg".format(name)
        photo = models.Photo(name=name, data=data)
        photo.save()


def populate_db_with_image_sizes():
    size_small = models.Size(label="small", price=10, shipping_cost=4.99)
    size_small.save()
    size_medium = models.Size(label="medium", price=15, shipping_cost=5.99)
    size_medium.save()
    size_large = models.Size(label="large", price=20, shipping_cost=7.99)
    size_large.save()


def populate_db_with_regions():
    for i in range(1, 11):
        region_name = "region_{:0>3}".format(i)
        region = models.Region(name=region_name)
        region.save()


def populate_db_with_countries():
    for i in range(1, 196):
        country_name = "country_{:0>4}".format(i)
        country = models.Country(name=country_name)
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
            "first_name": "Marija",
            "last_name": "Kalebota Kodzoman",
            "size_id": "1",
            "photo_id": "1",
            "region_id": "1",
            "country_id": "1",
            "email": "marija@example.com",
            "phone": "1111111111",
            "addr1": "Marija Addr1",
            "addr2": "Marija Addr2",
            "city": "Los Angeles",
            "postal_code": "22222",
        }
        self.correct_order_response = {
            "total_price": "14.99",
            "shipping_cost": "4.99",
            "print_price": "10.00",
        }

    def test_photos_get_status_code_200(self):
        response = self.client.get(self.photos_url)
        self.assertEquals(response.status_code, 200, response.content)

    def test_photos_post_status_code_400(self):
        response = self.client.post(self.photos_url)
        self.assertEquals(response.status_code, 400, response.content)

    def test_photos_return_jsonresponse(self):
        response = self.client.get(self.photos_url)
        self.assertEquals(response.get("Content-Type"), "application/json")

    def test_photos_return_only_photos_key(self):
        response = self.client.get(self.photos_url)
        response_dict = dict_from_bytestring(response.content)
        response_keys = list(response_dict.keys())

        self.assertEquals(len(response_keys), 1)
        self.assertEquals(response_keys[0], "photos")

    def test_photos_return_all_photos(self):
        response = self.client.get(self.photos_url)
        response_dict = dict_from_bytestring(response.content)
        number_of_photos_in_response = len(response_dict["photos"])
        number_of_photos_in_db = models.Photo.objects.count()
        self.assertEquals(number_of_photos_in_response, number_of_photos_in_db)

    def test_photos_return_correct_photos_when_paginated(self):
        response = self.client.get("{}?page=2".format(self.photos_url))
        response_dict = dict_from_bytestring(response.content)
        number_of_photos_in_response = len(response_dict["photos"])
        self.assertEquals(number_of_photos_in_response, PAGE_SIZE)

    def test_photos_return_error_when_page_number_too_big(self):
        response = self.client.get("{}?page=6".format(self.photos_url))
        self.assertEquals(response.content.decode(), "Page number is too big.")

    def test_order_get_status_code_400(self):
        response = self.client.get(self.order_url)
        self.assertEquals(response.status_code, 400, response.content)

    def test_order_post_correct_response(self):
        response = self.client.post(
            self.order_url, self.correct_order_form_data)
        response_dict = dict_from_bytestring(response.content)
        self.assertEquals(len(response_dict), 4)
        self.assertTrue(response_dict["order_number"])
        for key in list(self.correct_order_response.keys()):
            self.assertTrue(response_dict[key])
            self.assertEquals(
                response_dict[key], self.correct_order_response[key])
        self.assertEquals(response.status_code, 201, response.content)

    def test_order_post_empty_input(self):
        form_data = self.correct_order_form_data
        form_data["photo_id"] = ""
        response = self.client.post(self.order_url, form_data)
        self.assertEquals(response.status_code, 400, response.content)
        self.assertEquals(response.content.decode(),
                          "Parameter \"photo_id\" needs a value.")

    def test_order_post_too_long_input(self):
        form_data = self.correct_order_form_data
        form_data["city"] = "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd"
        response = self.client.post(self.order_url, form_data)
        self.assertEquals(response.status_code, 400, response.content)
        self.assertEquals(response.content.decode(
        ), "Parameter \"city\" length should be no more than 50.")

    def test_order_post_request_for_nonexistent_resource(self):
        form_data = self.correct_order_form_data
        form_data["size_id"] = "4"
        response = self.client.post(self.order_url, form_data)
        self.assertEquals(response.status_code, 400, response.content)
        self.assertEquals(response.content.decode(),
                          "Requested size not found.")

    # TODO(MarijaKalebota) write tests for code that remains uncovered
