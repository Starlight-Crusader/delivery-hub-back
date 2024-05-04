from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework import response, status
from rest_framework.pagination import PageNumberPagination

from .models import Delivery
from agents.models import Agent, AgentTypes
from .serializers import CreateDeliverySerializer, DeliverySerializer
from authen.views import UserRoles

from authen.jwt import JWTAuthentication


@api_view(['POST'])
def create_delivery(request):
    from_agent, payload = None, None
    try:
        jwt_auth = JWTAuthentication()
        from_agent, payload = jwt_auth.authenticate(request)
    except:
        return response.Response({'details': "Auth. credentials are incorrect/missing!"}, status=status.HTTP_401_UNAUTHORIZED)

    if payload['user_role'] != UserRoles.MANAGER.value or from_agent.type != AgentTypes.CONSUMER.value:
        return response.Response({'details': "You are not authorized to perform this action!"}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = CreateDeliverySerializer(data=request.data)
    if serializer.is_valid():
        to_agent = None
        
        try:
            to_agent = Agent.objects.get(name=serializer.validated_data['to_name'])
        except Agent.DoesNotExist:
            return response.Response({'details': "Addressee not found!"}, status=status.HTTP_404_NOT_FOUND)

        if from_agent == to_agent:
            return response.Response({'details': "You are not allowed to do this!"}, status=status.HTTP_403_FORBIDDEN)
        
        new_delivery = Delivery(from_agent=from_agent, to_agent=to_agent)
        new_delivery.save()

        return response.Response({'details': "Delivery request created successfully!"}, status=status.HTTP_201_CREATED)
    return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_deliveries(request):
    agent, payload = None, None
    try:
        jwt_auth = JWTAuthentication()
        agent, payload = jwt_auth.authenticate(request)
    except:
        return response.Response({'details': "Auth. credentials are incorrect/missing!"}, status=status.HTTP_401_UNAUTHORIZED)
    
    queryset = None

    if agent.type == AgentTypes.CONSUMER.value:
        queryset = Delivery

    if agent.type == AgentTypes.CONSUMER.value:
        if payload['user_role'] == UserRoles.VIEWER.value:
            queryset = Delivery.objects.filter((Q(from_agent=agent) | Q(to_agent=agent)) & Q(received=True))
        elif payload['user_role'] == UserRoles.WORKER.value:
            queryset = Delivery.objects.filter((Q(from_agent=agent) | Q(to_agent=agent)) & (Q(issued=False) | Q(received=False)))
        elif payload['user_role'] == UserRoles.MANAGER.value:
            queryset = Delivery.objects.filter(Q(from_agent=agent) | Q(to_agent=agent))

    elif agent.type == AgentTypes.PROVIDER.value:
        if payload['user_role'] == UserRoles.VIEWER.value:
            queryset = Delivery.objects.filter(Q(by_agent=agent) & Q(received=True))
        elif payload['user_role'] == UserRoles.WORKER.value:
            queryset = Delivery.objects.filter(Q(by_agent=agent) & Q(issued=True) & Q(delivered=False))
        elif payload['user_role'] == UserRoles.MANAGER.value:
            queryset = Delivery.objects.filter(Q(by_agent=agent) | Q(by_agent__isnull=True))
    
    paginator = PageNumberPagination()
    paginator.page_size = 10

    result_page = paginator.paginate_queryset(queryset, request)
    serializer = DeliverySerializer(result_page, many=True)

    return paginator.get_paginated_response(serializer.data)


@api_view(['PATCH'])
def take_delivery(request, delivery_id):
    agent, payload = None, None
    try:
        jwt_auth = JWTAuthentication()
        agent, payload = jwt_auth.authenticate(request)
    except:
        return response.Response({'details': "Auth. credentials are incorrect/missing!"}, status=status.HTTP_401_UNAUTHORIZED)
    
    delivery = None
    try:
        delivery = Delivery.objects.get(id=delivery_id)
    except Delivery.DoesNotExist:
        return response.Response({'details': "Delivery record not found!"}, status=status.HTTP_404_NOT_FOUND)
    
    if payload['user_role'] != UserRoles.MANAGER.value or agent.type != AgentTypes.PROVIDER.value:
        return response.Response({'details': "You are not allowed to do this!"}, status=status.HTTP_403_FORBIDDEN)
    
    if delivery.by_agent is None:
        delivery.by_agent = agent
        delivery.save()

        return response.Response({'details': "You've successfuly taken this delivery order!"}, status=status.HTTP_200_OK)
    else:
        return response.Response({'details': "This delivery order is already taken!"}, status=status.HTTP_403_FORBIDDEN)



@api_view(['PATCH'])
def check_delivery(request, delivery_id):
    agent, payload = None, None
    try:
        jwt_auth = JWTAuthentication()
        agent, payload = jwt_auth.authenticate(request)
    except:
        return response.Response({'details': "Auth. credentials are incorrect/missing!"}, status=status.HTTP_401_UNAUTHORIZED)
    
    delivery = None
    try:
        delivery = Delivery.objects.get(id=delivery_id)
    except Delivery.DoesNotExist:
        return response.Response({'details': "Delivery record not found!"}, status=status.HTTP_404_NOT_FOUND)

    if payload['user_role'] != UserRoles.WORKER.value:
        return response.Response({'details': "You are not allowed to do this!"}, status=status.HTTP_403_FORBIDDEN)
    
    if agent.type == AgentTypes.CONSUMER.value:
        if delivery.issued == False and delivery.from_agent == agent and delivery.by_agent is None:
            delivery.issued = True
            delivery.save()
        elif delivery.delivered == True and delivery.received == False and delivery.to_agent == agent:
            delivery.received = True
            delivery.save()
        else:
            return response.Response({'details': "You are not allowed to do this!"}, status=status.HTTP_403_FORBIDDEN)
    elif agent.type == AgentTypes.PROVIDER.value:
        if delivery.issued == True and delivery.delivered == False and delivery.by_agent == agent:
            delivery.delivered = True
            delivery.save()
        else:
            return response.Response({'details': "You are not allowed to do this!"}, status=status.HTTP_403_FORBIDDEN)

    return response.Response({'details': "Records successfully updated!"}, status=status.HTTP_200_OK)