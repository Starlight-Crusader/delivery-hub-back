from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework import views, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
import random

from enum import Enum

from agents.views import PassAuth
from agents.models import Agent

from .serializers import LoginSerializer
from .jwt import JWTAuthentication

Agent = get_user_model()


class UserRoles(Enum):
    VIEWER = 1
    WORKER = 2
    MANAGER = 3


class LoginView(views.APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        name = serializer.validated_data.get('name')
        password = serializer.validated_data.get('password')

        agent = None

        try:
            agent = Agent.objects.get(name=name)
        except Agent.DoesNotExist:
            return Response({'detail': "Agent not found!"}, status=status.HTTP_404_NOT_FOUND)

        user_role = None

        if check_password(password, agent.viewer_pass):
            user_role = UserRoles.VIEWER.value
        elif check_password(password, agent.worker_pass):
            user_role = UserRoles.WORKER.value
        elif check_password(password, agent.manager_pass):
            user_role = UserRoles.MANAGER.value
        else:
            return Response({'detail': "Incorrect password!"}, status=status.HTTP_401_UNAUTHORIZED)
        
        jwt_token = JWTAuthentication.create_jwt(agent, user_role)

        return Response({'token': jwt_token, 'agent_name': agent.name, 'agent_type': agent.type, 'user_role': user_role}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([PassAuth])
def get_rand_token(request):
    roles_list = list(role.value for role in UserRoles)
    rand_role = random.choice(roles_list)
    rand_agent = random.choice(Agent.objects.all())

    jwt_token = JWTAuthentication.create_jwt(rand_agent, rand_role)

    return Response({'token': jwt_token, 'agent_name': rand_agent.name, 'agent_type': rand_agent.type, 'user_role': rand_role}, status=status.HTTP_200_OK)
