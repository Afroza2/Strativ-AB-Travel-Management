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
from prophet.serialize import model_from_json
import pandas as pd
from datetime import datetime

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





class DecisionMakingAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            source_district_name = data.get('source_district_name')
            destination_district_name = data.get('destination_district_name')

            # Retrieve temperatures for source district
            source_cache_key = f'temperature_at_2pm_{source_district_name}'
            source_temperature_at_2pm = cache.get(source_cache_key)

            # Retrieve temperatures for destination district
            destination_cache_key = f'temperature_at_2pm_{destination_district_name}'
            destination_temperature_at_2pm = cache.get(destination_cache_key)

            if source_temperature_at_2pm is not None and destination_temperature_at_2pm is not None:
                # Calculate average temperature for the source district
                source_average_temperature = sum(source_temperature_at_2pm) / len(source_temperature_at_2pm)

                # Calculate average temperature for the destination district
                destination_average_temperature = sum(destination_temperature_at_2pm) / len(destination_temperature_at_2pm)

                # Compare average temperatures and make a travel recommendation
                if source_average_temperature < destination_average_temperature:
                    recommendation = f"Traveling from {source_district_name} to {destination_district_name} is Recommended as destination is cooler."
                else:
                    recommendation = f"Traveling from {source_district_name} to {destination_district_name} is NOT Recommended as destination is hotter."

                return Response({'recommendation': recommendation}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Temperature data not available for the specified source or destination district.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            # Handle exceptions if necessary
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class WeatherPredictionAPIView(APIView):
    def post(self, request):
        try:
            # Load serialized model
            with open('../utils/model.json', 'r') as fin:
                m = model_from_json(fin.read())

            # Extract input date from the request data
            input_date_str = request.data.get('date')
            input_date = datetime.strptime(input_date_str, '%Y-%m-%d')

            # Create a dataframe with the input date
            future_df = pd.DataFrame({'ds': [input_date]})

            # Make predictions
            forecast = m.predict(future_df)

            # Extract the predicted temperature for the input date
            predicted_temperature = forecast.loc[0, 'yhat']

            # Return the predicted temperature as a JSON response with status code 200 (OK)
            return Response({'predicted_temperature': predicted_temperature}, status=status.HTTP_200_OK)

        except FileNotFoundError:
            # Return an error response if the model file is not found with status code 500 (Internal Server Error)
            return Response({'error': 'Model file not found'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            # Return an error response for other exceptions with status code 500 (Internal Server Error)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
