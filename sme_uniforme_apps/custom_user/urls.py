from django.urls import include, path
from rest_framework import routers

from .api.viewsets.usuario_viewset import UsuarioViewset

router = routers.DefaultRouter()

router.register("usuarios", UsuarioViewset, "Usuários")

urlpatterns = [
    path('', include(router.urls))
]
