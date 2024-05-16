from datetime import datetime, timedelta

import jwt
from jwt.exceptions import ExpiredSignatureError
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed, ParseError

Agent = get_user_model()


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # Extract the JWT from the Authorization header
        jwt_token = request.headers.get('Authorization')
        if jwt_token is None:
            return None
        
        jwt_token = JWTAuthentication.get_the_token_from_header(jwt_token)  # clean the token

        # Decode the JWT and verify its signature
        try:
            payload = jwt.decode(jwt_token, settings.JWT_CONF['SECRET_KEY'], algorithms=['HS256'])
        except jwt.exceptions.InvalidSignatureError:
            raise AuthenticationFailed('Invalid signature!')
        except ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired!')
        except:
            raise ParseError()
    
        
        # Get the user's org. from the database
        agent_id = payload.get('agent_id')
        if agent_id is None:
            raise AuthenticationFailed('Agent identifier not found in JWT!')

        agent = Agent.objects.get(id=agent_id)
        if agent is None:
            raise AuthenticationFailed('Agent not found!')
        
        # Return the agent and token payload
        return agent, payload

    @classmethod
    def create_jwt(cls, agent, user_role):

        # Create the JWT payload
        payload = {
            'agent_id': agent.id,
            'user_role': user_role,
            'iat': datetime.now().timestamp(),
            'exp': int((datetime.now() + timedelta(minutes=settings.JWT_CONF['TOKEN_LIFETIME_MINUTES'])).timestamp()),
        }

        # Encode the JWT with your secret key
        jwt_token = jwt.encode(payload, settings.JWT_CONF['SECRET_KEY'], algorithm='HS256')

        return jwt_token

    @classmethod
    def get_the_token_from_header(cls, token):
        token = token.replace('Bearer', '').replace(' ', '')  # clean the token
        return token