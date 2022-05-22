from rest_framework import serializers
from .models import CustomUser as User

from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):


    class Meta:
        model = User
        fields = ['url','id','username','email','password']
        read_only_fields = ('id',)
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):

        print(validated_data)
        user = User(**validated_data)

        user.set_password(validated_data['password'])
        user.save()
        return user