from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from . import models

def create_dummy_data():
    photo1 = models.Photo(name = "photo1", data = "dnsfnj")
    photo1.save()
    region1 = models.Region(name = "reg1")
    region1.save()
    country1 = models.Country(name = "usa")
    country1.save()


@csrf_exempt
def order(request):
    if request.method == "POST":

        photo_id = request.POST.get("photo_id")
        size_id = request.POST.get("size_id")
        
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        addr1 = request.POST.get("addr1")
        addr2 = request.POST.get("addr2")
        city = request.POST.get("city")
        region_id = request.POST.get("region_id")
        postal_code = request.POST.get("postal_code")
        country_id = request.POST.get("country_id")

        new_order = models.Order(
            photo_id = photo_id,
            size_id = size_id,
            first_name = first_name,
            last_name = last_name,
            email = email,
            phone = phone,
            addr1 = addr1,
            addr2 = addr2,
            city = city,
            region_id = region_id,
            postal_code = postal_code,
            country_id = country_id
            )

        new_order.save()

        order_number = new_order.id
        print_size = models.Size.objects.get(id=new_order.size_id)
        total_price = print_size.price + print_size.shipping_cost

        response_data = {
            "order_number" : order_number,
            "total_price" : total_price
            }
        return JsonResponse(response_data, status=201)
    else:
        return HttpResponse(status=400)

def photos(request):
    return HttpResponse('Returning all photos')
