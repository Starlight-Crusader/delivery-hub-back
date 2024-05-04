from rest_framework.decorators import api_view, permission_classes
from rest_framework import response, status, permissions

from .models import Agent
from .serializers import AgentSerializer

ADMIN_PASS_HEADER_NAME = 'X-Password'
ADMIN_PASS = 'DjIbOuTi'


class PassAuth(permissions.BasePermission):
    def has_permission(self, request, view):
        password = request.headers.get(ADMIN_PASS_HEADER_NAME)

        if password != ADMIN_PASS:
            return False
        
        return True


@api_view(['GET'])
@permission_classes([PassAuth])
def get_all_agents(request):
    try:
        agents = Agent.objects.all()
        serializer = AgentSerializer(agents, many=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return response.Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([PassAuth])
def get_one_agent(request, user_id):
    try:
        agent = Agent.objects.get(id=user_id)
        serializer = AgentSerializer(agent)
        return response.Response(serializer.data, status=status.HTTP_200_OK)
    except Agent.DoesNotExist:
        return response.Response({'message': 'Agent not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return response.Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([PassAuth])
def create_agent(request):
    try:
        serializer = AgentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return response.Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([PassAuth])
def drop_all_agents(request):
    try:
        Agent.objects.all().delete()
        return response.Response({'message': 'All agents deleted successfully.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return response.Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([PassAuth])
def drop_one_agent(request, user_id):
    try:
        agent = Agent.objects.get(id=user_id)
        agent.delete()
        return response.Response({'message': f'Agent with ID {user_id} deleted successfully.'}, status=status.HTTP_200_OK)
    except Agent.DoesNotExist:
        return response.Response({'message': 'Agent not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return response.Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
