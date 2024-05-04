from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    name = serializers.CharField()
    password = serializers.CharField()