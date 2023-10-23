from django.shortcuts import render
from rest_framework import generics, permissions, status
import requests
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, UserSerializer
from .models import CustomUser

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
                latitude = district.get('lat')  
                longitude = district.get('long')  

                if latitude is not None and longitude is not None:
                    api_url = f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m&timezone=GMT'

                    # print(f"Fetching data for {district.get('name')} - {api_url}")  
                    
                    weather_response = requests.get(api_url)
                    weather_response.raise_for_status()  

                    weather_data = weather_response.json()

                    # print("data", weather_data) 

                    hourly_data = weather_data.get('hourly', {})
                    temperature_2m_values = hourly_data.get('temperature_2m', [])

                    # print(f"Temperature 2m values: {temperature_2m_values}")  

                    
                    avg_temp_2pm = sum(temperature_2m_values) / len(temperature_2m_values) if temperature_2m_values else None

                    if avg_temp_2pm is not None:
                        coolest_districts.append({
                            'district_name': district.get('name'), 
                            'average_temperature_2pm': avg_temp_2pm
                        })

            
            coolest_districts.sort(key=lambda x: x['average_temperature_2pm'])
            top_10_coolest_districts = coolest_districts[:10]

            return Response({'coolest_districts': top_10_coolest_districts}, status=status.HTTP_200_OK)

        except requests.exceptions.HTTPError as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

