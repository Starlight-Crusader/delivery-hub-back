from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework import views, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import LoginSerializer
from .jwt import JWTAuthentication

Agent = get_user_model()


class LoginView(views.APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        name = serializer.validated_data.get('name')
        password = serializer.validated_data.get('password')

        agent = Agent.objects.get(name=name)
        if agent is None:
            return Response({'message': "Agent not found!"}, status=status.HTTP_404_NOT_FOUND)
        
        VIEWER = 1
        WORKER = 2
        MANAGER = 3
        user_type = None

        if check_password(password, agent.viewer_pass):
            user_type = VIEWER
        elif check_password(password, agent.worker_pass):
            user_type = WORKER
        elif check_password(password, agent.manager_pass):
            user_type = MANAGER
        else:
            return Response({'message': "Incorrect password!"}, status=status.HTTP_401_UNAUTHORIZED)
        
        jwt_token = JWTAuthentication.create_jwt(agent, user_type)

        return Response({'token': jwt_token})