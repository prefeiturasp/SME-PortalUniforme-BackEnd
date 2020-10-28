from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import serializers

from sme_uniforme_apps.proponentes.api.serializers.proponente_serializer import ProponenteSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class UsuarioSerializer(serializers.ModelSerializer):
    proponente = ProponenteSerializer()
    token = serializers.SerializerMethodField()

    def get_token(self, obj):
        if not obj.last_login:
            token_generator = PasswordResetTokenGenerator()
            novo_token = token_generator.make_token(obj)
            return novo_token
        return None

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "proponente", "last_login", "token")
