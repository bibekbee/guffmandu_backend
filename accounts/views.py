# django imports
from django.contrib.auth import get_user_model, authenticate

# rest_framework imports
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

# importing serializers
from .serializers import UserProfileDataSerializer

# imports from APPS
from utilities.response_utilities import ResponseUtilities
from .registration import CustomUserRegistration
from .validators import validate_username, validate_password, validate_pin, compress_image


# Getting USER Model with the django given function
User = get_user_model()

class LoginView(APIView, ResponseUtilities):

    permission_classes = [AllowAny]
    
    def post(self, request, format=None):
        username = request.data.get("username")
        password = request.data.get("password")
        print(username, password)
        user = authenticate(request, username = username, password = password)

        if user:
            print("User is authenticated✅")
            refresh = RefreshToken.for_user(user)

            self.success_status = True
            self.message_to_client = "logged in successfully"
            self.response_data = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
        else:
            print("User is not authenticated")
            self.message_to_client = "username or password was not matched !"

        return Response(self.get_generated_response())
    
class RegisterView(APIView, ResponseUtilities, CustomUserRegistration):
    
    def post(self, request, format=None):
        print("Here to signup !")
        user = self.register_user_if_valid(request.data)
        print(self.get_generated_response())

        return Response(self.get_generated_response())

class AuthUserQuickData(APIView, ResponseUtilities):

    permission_classes = [IsAuthenticated]
    
    def get(self, request, format=None):
        try:
            self.response_data = UserProfileDataSerializer(instance = request.user).data
            self.success_status = True
        except:
            self.message_to_client = "Something went wrong when fetching the data"
        
        return Response(self.get_generated_response())

class UpdateUsernameView(APIView, ResponseUtilities):
    # Only authenticated users can access this view
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):

        new_username = request.data.get("new_username", None)
        
        try:
            # The below function validate the new username using the validate_username function
            # Returns a dictionary with:
            # - 'is_valid' (bool): True if the username is valid, False if not.
            # - 'message' (str): A message explaining the validation result (empty if valid, error message if invalid).
            validate_data = validate_username(new_username)

            if validate_data["is_valid"]:
                # If username is valid, update it
                user = request.user
                user.username = new_username
                user.save()

                self.success_status = True  # Mark the operation as successful
                self.message_to_client = "Username changed successfully"
            else:
                # If validation fails, return the error message
                self.message_to_client = validate_data["message"]

        except Exception as e:
            # Handle any unexpected errors during the process
            self.message_to_client = "Error occurred while changing username!"

        # Return the structured response with status and message
        return Response(self.get_generated_response())
    
class UpdateProfilePhotoView(APIView, ResponseUtilities):
    
    permission_classes = [IsAuthenticated]
    MAX_SIZE = 2 * 1024 * 1024  # 2 MB
    ALLOWED_FILE_TYPES = ['image/jpeg', 'image/png'] # add more if new fetures

    def post(self, request):
        """
            Handles user profile photo updates.
        
            Args:
                request: HTTP POST request object containing user data and uploaded file.
            
            Behavior:
                - Checks if the 'commit' field is 'update'.
                - Validates if a photo is provided.
                - Compresses the photo if it exceeds 2MB.
                - Saves the new photo to the user's profile.
        """
        commit = request.data.get("commit")
        profile_photo = request.FILES.get("profile_photo", "")
        user = request.user

        if commit == "update":
            if not profile_photo:
                self.message_to_client = "No profile photo provided"
            else:
                
                # Validating the FILE TYPE
                # Allowing only JPG and PNG file type
                if profile_photo.content_type not in self.ALLOWED_FILE_TYPES:
                    self.message_to_client = "Only JPEG and PNG images are allowed."
                    return Response(self.get_generated_response())

                # Validating the photo size
                if profile_photo.size > self.MAX_SIZE:
                    self.message_to_client = "Maximum photo size allowed is 2 MB."
                    return Response(self.get_generated_response())

                # Assign the new profile photo
                user.profile_photo = profile_photo
                user.save()
                self.success_status = True

        elif commit == "remove":
            if user.profile_photo.name == "default_profile_photo.jpg":
                self.message_to_client = "No profile photo to remove"
            else:
                # Revert to default profile photo
                user.remove_profile_photo()
                self.success_status = True
                self.message_to_client = "Profile photo removed successfully"

        else:
            self.message_to_client = "Invalid commit action"

        return Response(self.get_generated_response())
    
class UpdatePasswordView(APIView, ResponseUtilities):
    # Only authenticated users can access this view
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        old_password = request.data.get("old_password", None)
        new_password = request.data.get("new_password", None)
        confirm_password = request.data.get("confirm_password", None)
        
        try:
            # Check if old password is provided
            if not old_password:
                self.message_to_client = "Old Password is required !"
                return Response(self.get_generated_response())
            
            # First, check if the old password is correct
            user = request.user
            if not user.check_password(old_password):  # Verifies if the old password matches
                self.message_to_client = "Incorrect old password !"
                return Response(self.get_generated_response())
            
            # Validate the new password using the validate_password function
            validate_data = validate_password(new_password, confirm_password)

            if validate_data["is_valid"]:
                # If password is valid, update it
                user.set_password(new_password)  # This safely hashes the new password
                user.save()

                self.success_status = True  # Mark the operation as successful
                self.message_to_client = "Password changed successfully."
            else:
                # If validation fails, return the error message
                self.message_to_client = validate_data["message"]

        except Exception as e:
            # Handle any unexpected errors during the process
            self.message_to_client = "Error occurred while changing password!"

        # Return the structured response with status and message
        return Response(self.get_generated_response())

class UpdatePINView(APIView, ResponseUtilities):
    # Only authenticated users can access this view
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        password = request.data.get("password", None)  # User account password
        new_pin = request.data.get("new_pin", None)
        confirm_pin = request.data.get("confirm_pin", None)
        
        try:
            # Check if password is provided
            if not password:
                self.message_to_client = "Password is required to change the PIN"
                return Response(self.get_generated_response())

            # First, check if the old password is correct
            user = request.user
            if not user.check_password(password):  # Verifies if the old password matches
                self.message_to_client = "Incorrect password."
                return Response(self.get_generated_response())

            # Validate the new PIN using the verify_pin function
            validate_data = validate_pin(new_pin, confirm_pin)

            if validate_data["is_valid"]:
                # If PIN is valid, update it
                # Here, we update the PIN field or any field you want to store the PIN
                user.pin = new_pin  # You can modify this based on where the PIN is stored
                user.save()

                self.success_status = True  # Mark the operation as successful
                self.message_to_client = "PIN changed successfully."
            else:
                # If validation fails, return the error message
                self.message_to_client = validate_data["message"]

        except Exception as e:
            # Handle any unexpected errors during the process
            self.message_to_client = "Error occurred while changing PIN!"

        # Return the structured response with status and message
        return Response(self.get_generated_response())