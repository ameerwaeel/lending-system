from django.shortcuts import render,get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import *
from django.contrib.auth.models import User
from rest_framework import status
from django.contrib.auth.hashers import make_password


from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

# Create your views here.
@api_view(['POST'])
def register(request):
    data=request.data
    user=SignUpSerializer(data=data)
    if user.is_valid():
        if not User.objects.filter(username=data['email']).exists():
            user=User.objects.create(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],

                username=data['email'],

                password=make_password(data['password']),
            )
            return Response({"details":"your account registerd successefuly"},status=status.HTTP_201_CREATED)
        else:
            return Response({"error":"your email already exists "},status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(user.errors)    



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    user=SignUpSerializer(request.user)     
    return Response(user.data)    
