from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('id','username')

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'password')

    # def create(self, validated_data):
    #     user = User.objects.create_user(
    #         username=validated_data['username'],
    #         password=validated_data['password']
    #     )
    #     return user

class CompareTemperaturesSerializer(serializers.Serializer):
    user_district = serializers.CharField()
    friend_district = serializers.CharField()
    travel_date = serializers.DateField()
    temperature = serializers.FloatField()