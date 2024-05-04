from django.urls import path
from . import views

urlpatterns = [
    path('create', views.create_delivery),
    path('get', views.get_deliveries),
    path('take/<int:delivery_id>', views.take_delivery),
    path('check/<int:delivery_id>', views.check_delivery),
]