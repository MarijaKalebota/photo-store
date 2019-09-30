from django.test import TestCase

class TestPhotos(TestCase):
    def test_photos_status_code_200(self):
        response = self.client.get('http://127.0.0.1:8000/photo-store/photos/')
        self.assertEquals(response.status_code, 200)
