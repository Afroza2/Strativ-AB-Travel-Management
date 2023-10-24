from django.shortcuts import render
from rest_framework import generics, permissions, status
import requests
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, UserSerializer
from .models import CustomUser
from apilist.tasks import fetch_and_store_temperature
from django.core.cache import cache
import datetime

# Create your views here.

class UserRegistration(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'User registered successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogin(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        username = data.get('username', None)
        password = data.get('password', None)
        user = CustomUser.objects.filter(username=username).first()
        
        # if user is None or password is None:
            # return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # if not user.check_password(password):
        #     return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        if user is None or password is None or not user.check_password(password):
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
          
            'access token': str(refresh.access_token),
              'refresh token': str(refresh),
        }, status=status.HTTP_200_OK)
    

class UserListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)  # UserSerializer for displaying user details
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CoolestDistrictsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            response = requests.get('https://raw.githubusercontent.com/strativ-dev/technical-screening-test/main/bd-districts.json')
            response.raise_for_status()

            districts_data = response.json().get('districts', [])

            coolest_districts = []

            for district in districts_data:
                cache_key = f'temperature_at_2pm_{district["name"]}'
                temperature_at_2pm = cache.get(cache_key)

                if temperature_at_2pm is not None:
                    # Calculate average temperature for the district
                    average_temperature = sum(temperature_at_2pm) / len(temperature_at_2pm)
                    coolest_districts.append({
                        'district_name': district['name'],
                        'average_temperature_2pm': average_temperature
                    })

            # Sort the coolest districts based on average temperature
            coolest_districts.sort(key=lambda x: x['average_temperature_2pm'])
            top_10_coolest_districts = coolest_districts[:10]

            return Response({'coolest_districts': top_10_coolest_districts}, status=status.HTTP_200_OK)

        except requests.exceptions.HTTPError as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class FetchTemperatureView(APIView):
    def get(self, request, *args, **kwargs):
    
        fetch_and_store_temperature.delay()
        temperature_at_2pm = cache.get('temperature_at_2pm')

        if temperature_at_2pm is not None:
    # Do something with the temperature data
            print(f'Temperature at 2 PM: {temperature_at_2pm}')
        else:
            # The data is not in the cache, handle this situation accordingly
            print('Temperature data is not available in the cache.')
        return Response({'message': 'Temperature fetching task has been initiated.'})

