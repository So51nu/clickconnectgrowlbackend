from django.http import JsonResponse
from .models import Testimonial


def testimonial_list(request):
    data = []
    testimonials = Testimonial.objects.filter(is_active=True).order_by("sort_order", "-id")

    for item in testimonials:
        data.append(
            {
                "id": item.id,
                "name": item.name,
                "role": item.role,
                "description": item.description,
                "avatar": item.avatar.url if item.avatar else "",
                "rating": item.rating,
                "width": item.width,
                "height": item.height,
            }
        )

    return JsonResponse(data, safe=False)