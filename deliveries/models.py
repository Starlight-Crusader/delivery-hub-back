from django.db import models

from agents.models import Agent


class Delivery(models.Model):
    from_agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='deliveries_from')
    to_agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='deliveries_to')
    by_agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='deliveries_by', null=True)

    issued = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)