import base64

from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from . import models


def is_param_set(param_name, param_value):
    if not param_value:
        raise ValueError("Parameter \"{}\" needs a value.".format(param_name))


def is_valid_text_param(param_name, param_value, max_length=50):
    is_param_set(param_name, param_value)
    if len(param_value) > max_length:
        raise ValueError("Parameter \"{}\" length should be no more than \"{}\".".format(
            param_name, max_length))


def is_valid_id_param(param_name, param_value, param_objects):
    is_param_set(param_name, param_value)
    param_objects.get(id=param_value)


@csrf_exempt
def order(request):
    if request.method != "POST":
        return HttpResponse(status=400)

    params_text_with_error_messages = [
        ("first_name", "First name too long"),
        ("last_name", "Last name too long"),
        ("addr1", "Address line 1 is too long"),
        ("addr2", "Address line 2 is too long"),
        ("city", "City name too long"),
    ]

    values = {}
    for param, error_msg in params_text_with_error_messages:
        try:
            param_value = request.POST.get(param)
            is_valid_text_param(param, param_value)
        except ValueError as error:
            return HttpResponse(error, status=400)

        values[param] = param_value

    params_id_with_error_messages = [
        ("photo_id", models.Photo.objects,
         models.Photo.DoesNotExist, "Photo does not exist."),
        ("size_id", models.Size.objects,
         models.Size.DoesNotExist, "Size does not exist."),
        ("region_id", models.Region.objects,
         models.Region.DoesNotExist, "Region does not exist."),
        ("country_id", models.Country.objects,
         models.Country.DoesNotExist, "Country does not exist."),
    ]

    for param, param_objects, param_error, error_msg in params_id_with_error_messages:
        try:
            param_value = request.POST.get(param)
            is_valid_id_param(param, param_value, param_objects)
        except param_error:
            return HttpResponse(error_msg, status=400)
        except ValueError as error:
            return HttpResponse(error, status=400)

        values[param] = param_value

    email = request.POST.get("email")
    if not email:
        return HttpResponse("Field \"email\" must be set", status=400)
    try:
        validate_email(email)
    except ValidationError:
        return HttpResponse("Invalid email.", status=400)

    phone = request.POST.get("phone")
    if not phone:
        return HttpResponse("Field \"phone\" must be set", status=400)

    postal_code = request.POST.get("postal_code")
    if not postal_code:
        return HttpResponse("Field \"postal_code\" must be set", status=400)
    try:
        int(postal_code)
    except ValueError:
        return HttpResponse("Invalid postal code. Please only input digits.", status=400)

    new_order = models.Order(
        photo_id=values["photo_id"],
        size_id=values["size_id"],
        first_name=values["first_name"],
        last_name=values["last_name"],
        email=email,
        phone=phone,
        addr1=values["addr1"],
        addr2=values["addr2"],
        city=values["city"],
        region_id=values["region_id"],
        postal_code=postal_code,
        country_id=values["country_id"],
    )

    try:
        with transaction.atomic():
            new_order.save()

            order_number = new_order.id
            print_size = models.Size.objects.get(id=new_order.size_id)
            total_price = print_size.price + print_size.shipping_cost

            response_data = {
                "order_number": order_number,
                "print_price": print_size.price,
                "shipping_cost": print_size.shipping_cost,
                "total_price": total_price
            }
            return JsonResponse(response_data, status=201)

    except IntegrityError:
        return HttpResponse("Transaction unsuccessful, please try again", status=400)


@csrf_exempt
def photos(request):
    if request.method != "GET":
        return HttpResponse(status=400)

    photos = models.Photo.objects.all().order_by("id")

    if request.GET.get('page'):
        page = request.GET.get('page')

        if not page:
            return HttpResponse("Field \"page\" incorrectly set", status=400)
        if int(page) > 5:
            return HttpResponse("Page number is too big", status=400)

        paginator = Paginator(photos, 20)
        photos = paginator.page(page)

    if request.GET.get('names') == "True":
        encoded_photos = [photo.name for photo in photos]
    else:
        binary_photos = [photo.data.read() for photo in photos]
        encoded_photos = [str(base64.b64encode(photo))
                          for photo in binary_photos]

    photos_with_ids = []
    for i in range(len(encoded_photos)):
        photo_with_id = {
            "id": photos[i].id,
            "photo": encoded_photos[i],
        }
        photos_with_ids.append(photo_with_id)

    response_data = {
        "photos": photos_with_ids,
    }
    return JsonResponse(response_data)
