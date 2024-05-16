from rest_framework import serializers
from .models import Delivery

from agents.serializers import AgentSerializer


class DeliverySerializer(serializers.ModelSerializer):
    from_agent = AgentSerializer(read_only=True)
    to_agent = AgentSerializer(read_only=True)
    by_agent = AgentSerializer(read_only=True)

    class Meta:
        model = Delivery
        fields = ['id', 'from_agent', 'to_agent', 'by_agent', 'issued', 'delivered', 'received']


class CreateDeliverySerializer(serializers.Serializer): 
    to_name = serializers.CharField()