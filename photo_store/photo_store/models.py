from django.db import models

class Photo(models.Model):
    name = models.CharField(max_length = 50)
    data = models.ImageField()

class Size(models.Model):
    label = models.CharField(max_length = 50)
    price = models.DecimalField(max_digits = 8, decimal_places = 2)


class Region(models.Model):
	name = models.CharField(max_length = 50)


class Country(models.Model):
	name = models.CharField(max_length = 50)


# TODO(MarijaKalebota) Extract user and shipping details into 
# separate tables for potential reuse
class Order(models.Model):
    timestamp = models.DateTimeField()
    photo_id = models.ForeignKey(Photo)
    size_id = models.ForeignKey(Size)

    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    email = models.CharField(max_length = 50)
    phone = models.CharField(max_length = 50)
    addr1 = models.CharField(max_length = 50)
    addr2 = models.CharField(max_length = 50)
    city = models.CharField(max_length = 50)
    region = models.ForeignKey(Region)
    postal_code = models.CharField(max_length = 50)
    country = models.ForeignKey(Country)
