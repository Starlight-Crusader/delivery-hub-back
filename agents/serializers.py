from rest_framework import serializers
from .models import Agent
from django.contrib.auth.hashers import make_password


class AgentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Agent
        fields = '__all__'

    def create(self, validated_data):
        validated_data['viewer_pass'] = make_password(validated_data['viewer_pass'])
        validated_data['worker_pass'] = make_password(validated_data['worker_pass'])
        validated_data['manager_pass'] = make_password(validated_data['manager_pass'])

        return super().create(validated_data)
