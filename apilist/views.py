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



# class DecisionMakingAPIView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request):
#         try:
#             data = request.data
#             source_district_name = data.get('source_district_name')
#             destination_district_name = data.get('destination_district_name')

#             response = requests.get('https://raw.githubusercontent.com/strativ-dev/technical-screening-test/main/bd-districts.json')
#             response.raise_for_status()

#             districts_data = response.json().get('districts', [])

#             source_temperatures = None
#             destination_temperatures = None

#             for district in districts_data:
#                 if district['name'] == source_district_name:
#                     source_temperatures = cache.get(f'temperature_at_2pm_{district["name"]}')
#                 elif district['name'] == destination_district_name:
#                     destination_temperatures = cache.get(f'temperature_at_2pm_{district["name"]}')

#                 # if source_temperatures and destination_temperatures:
#                 #     break

#             if source_temperatures is not None and destination_temperatures is not None:
#                 source_average_temperature = sum(source_temperatures) / len(source_temperatures)
#                 destination_average_temperature = sum(destination_temperatures) / len(destination_temperatures)

#                 print("Source Temperatures:", source_temperatures)
#                 print("Destination Temperatures:", destination_temperatures)


#                 decision = "Source location is cooler." if source_average_temperature < destination_average_temperature else "Destination location is cooler."

#                 return Response({'decision': decision}, status=status.HTTP_200_OK)
#             else:
#                 return Response({'error': 'Temperature data not available for the specified source or destination district.'}, status=status.HTTP_404_NOT_FOUND)

#         except requests.exceptions.HTTPError as err:
#             return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DecisionMakingAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            source_district_name = data.get('source_district_name')
            destination_district_name = data.get('destination_district_name')

            # Retrieve all temperatures from the cache
            all_temperatures = cache.get('temperature_data')

            print("temp 1", all_temperatures[:10])

            if all_temperatures is not None:
                print("meow")
                # Filter temperatures for source district
                source_temperatures = [temp for temp in all_temperatures if temp['name'] == source_district_name]

                print("source",source_temperatures)

                # Filter temperatures for destination district
                destination_temperatures = [temp for temp in all_temperatures if temp['districts'] == destination_district_name]

                if source_temperatures and destination_temperatures:
                    # Calculate average temperatures for source and destination districts
                    source_average_temperature = sum(source_temperatures) / len(source_temperatures)
                    destination_average_temperature = sum(destination_temperatures) / len(destination_temperatures)

                    # Compare average temperatures and make a decision
                    decision = "Source location is cooler." if source_average_temperature < destination_average_temperature else "Destination location is cooler."

                    return Response({'decision': decision}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Temperature data not available for the specified source or destination district.'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'error': 'Temperature data not available for any district.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            # Handle exceptions if necessary
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # return Response({"meow"})

           
        
