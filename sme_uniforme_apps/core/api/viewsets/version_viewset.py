from rest_framework import viewsets
from utility.api_version import API_VERSION
from rest_framework.response import Response


class ApiVersion(viewsets.ViewSet):

    def list(self, request):
        return Response({'API_Version': API_VERSION})
