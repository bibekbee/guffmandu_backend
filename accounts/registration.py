"""

Disclaimer: This module is not django module.

This was custom created by Diwash on 2024/03/12.

If you have any questions while using this, ask him.

"""


from django.contrib.auth import get_user_model
from .validators import *

User = get_user_model()
# This will be used to create a user model.

class CustomUserRegistration:
    """
    Takes registration_data, verifies it using modules, and creates a new user if all is well.

    How to Use:
        - Simply use register_user_if_valid() module by giving request.POST
        - Will return True or False
        - use self.message_to_client attribute to send message to client
        - Message will be assigned to self.message_to_client

    Methods:
        1. register_user_if_valid(self, registration_data) -> bool
        2. valid_password(self) -> bool
        3. user_doesnot_exist(self) -> bool
        4. get_full_name(self) -> str
        5. check_gender(self) -> bool
    """

    message_to_client = None
    success_status:bool = False
    # This messege is sent to the client as a error/success message
    
    def register_user_if_valid(self, registration_data):
        """
        This is the main method of this class:

            Steps:
                1. Takes out all the values and assign it to the attributes.
                2. Creates a user if every other method returns True.
                3. If any error happens when creating user in last then catches error and print and set sorry message to self.message_to_client
        """
        self.email = registration_data.get("email")
        self.username = registration_data.get("username")
        
        self.password = registration_data.get("password")
        self.confirm_password = registration_data.get("confirm_password")

        self.gender = registration_data.get("gender")

        # Returning none if something among the list is not provided
        if not self.all_exists():
            self.message_to_client = "All credentials were not provided"
            return False

        # Checks if user has sent valid form or not.
        # Returns False when not valid.
        if self.valid_password() and self.valid_username() and self.user_doesnot_exist() and self.check_gender():
            try:
                created_user = User.objects.create(
                                    username=self.username,
                                    email = self.email,
                                    gender = self.gender
                                    )
                
                created_user.set_password(self.password)
                created_user.save()

                self.message_to_client = "Your Account was created successfully"
                self.success_status = True
                return created_user
            
            except Exception as e:
                print("Error happened when creating a new user:",e)
                self.message_to_client = "Some error happened when creating your account."
                return False
        
        else:
            return False

    # Checks if given passwords are same or not
    def valid_password(self) -> bool:
        
        validated_data = validate_password(self.password, self.confirm_password)

        if validated_data["is_valid"]:
            return True
        
        self.message_to_client = validated_data["message"]
        return False

    # Checking if the tracsaction pin is valid or not.
    # def is_valid_transaction_pin(self) -> bool:
    #     pin = str(self.transaction_pin)
    #     confirm_pin = str(self.confirm_pin)
        
    #     # Check if PIN is exactly 4 digits and numeric
    #     if not (pin.isdigit() and len(pin) == 4):
    #         self.message_to_client = "Transaction PIN must be a 4-digit numeric value."
    #         return False
        
    #     # Check if PIN and confirmation PIN match
    #     if pin != confirm_pin:
    #         self.message_to_client = "Transaction PINs do not match!"
    #         return False

    #     return True
    
    def user_doesnot_exist(self) -> bool:
        """
        Checks if both email already exists or not
        """
        if User.objects.filter(email=self.email).exists():
            self.message_to_client = "Sorry, this email already exists"
            return False
        
        return True
    
    def valid_username(self) -> bool:
        """
        Checks if username is valid or not using the validate_username() function
        """
        validated_data = validate_username(self.username)

        if validated_data["is_valid"]:
            return True
        
        self.message_to_client = validated_data["message"]
        return False
    
    def check_gender(self) -> bool:
        valid_genders = ["m", "f", "o"]

        if self.gender.lower() in valid_genders:
            return True
        else:
            self.message_to_client = "Sorry, Some error occurred"
            return False
        # This will return if gender is in valid_genders or not
        # Note:
        #   This is for situations where the client uses the browser's Inspect Element capability to do anything incorrect here. 

    def all_exists(self) -> bool :
        lst = [self.email, self.username, self.password, self.confirm_password, self.gender]
        if None in lst:
            self.message_to_client = "You haven't provided all things"
            return False
        
        return True