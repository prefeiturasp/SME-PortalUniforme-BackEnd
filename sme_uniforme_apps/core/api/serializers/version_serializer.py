from rest_framework import serializers


class VersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = None
        fields = '__all__'
