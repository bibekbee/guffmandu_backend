# Imporiting from django
from django.contrib.auth import get_user_model

# Importing from rest_FRAMEWORK
from rest_framework.serializers import ModelSerializer

User = get_user_model()

class UserProfileDataSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "age", "balance", "email", "gender", "profile_photo"]