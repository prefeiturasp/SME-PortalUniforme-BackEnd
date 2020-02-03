from django.urls import path
from rest_framework import routers

from .api.viewsets.usuario_viewset import UsuarioViewset

router = routers.DefaultRouter()

router.register("usuario", UsuarioViewset)

urlpatterns = [
    path('', router.urls)
]
