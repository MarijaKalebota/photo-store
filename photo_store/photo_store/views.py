from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from . import models
import base64

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

@csrf_exempt
def photos(request):
    if(request.method == "GET"):
        photos = models.Photo.objects.all().order_by("id")

        if (request.GET.get('page')):
            page = request.GET.get('page')
            paginator = Paginator(photos, 20)
            photos = paginator.page(page)
        
        if(request.GET.get('names') == "True"):
            encoded_photos = [photo.name for photo in photos]
        else:
            binary_photos = [photo.data.read() for photo in photos]
            encoded_photos = [str(base64.b64encode(photo)) for photo in binary_photos]
        
        photos_with_ids = []
        for i in range(len(encoded_photos)):
            photo_with_id = {
                "id" : photos[i].id,
                "photo" : encoded_photos[i],
            }
            photos_with_ids.append(photo_with_id)

        response_data = {
                "photos" : photos_with_ids,
                }
        return JsonResponse(response_data)
    else:
        return HttpResponse(status=400)
