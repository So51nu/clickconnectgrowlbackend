from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from .models import HeaderMenu
from .serializers import HeaderMenuSerializer


class HeaderMenuListAPIView(ListAPIView):
    serializer_class = HeaderMenuSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return HeaderMenu.objects.all().order_by("order", "id")