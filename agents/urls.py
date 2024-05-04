from django.urls import path
from . import views

urlpatterns = [
    path('get', views.get_all_agents),
    path('get/<int:user_id>', views.get_one_agent),
    path('create', views.create_agent),
    path('drop', views.drop_all_agents),
    path('drop/<int:user_id>', views.drop_one_agent),
]
