# Imports from dajngo
from django.contrib.auth import get_user_model

# Importing third party libraries
from PIL import Image # Will be using to compress the image size
from io import BytesIO
import re

# Getting User Model using django given function
User = get_user_model()

def validate_username(username):
    """
    Validates a username based on specific criteria:
    1. Username must not be empty or consist only of whitespace.
    2. Length must be between 3 and 20 characters.
    3. Must contain at least one letter (a-z, A-Z).
    4. Cannot start with a number.
    5. Can only include letters, numbers, and underscores.
    6. Cannot consist solely of numbers.
    7. Must not already exist in the database.

    Args:
        username (str): The username to validate.

    Returns:
        dict: A dictionary containing:
            - `is_valid` (bool): Whether the username is valid.
            - `message` (str): The validation message if invalid, empty if valid.
    """
    # Initialize a dictionary to store the result
    data = {"is_valid": False, "message": ""}

    # Helper function to set the error message and return the result
    def fail(message):
        """
        Sets the failure message and updates the data dictionary.
        
        Args:
            message (str): The failure message to include.
        
        Returns:
            dict: Updated data dictionary with the failure message.
        """
        data["message"] = message
        return data

    # Check if the username is empty or consists only of whitespace
    if not username or username.strip() == "":
        return fail("No username provided")

    # Validate the length of the username
    if not (3 <= len(username) <= 20):
        return fail("Username must be between 3 and 20 characters!")

    # Ensure the username contains at least one letter
    if not re.search(r'[a-zA-Z]', username):
        return fail("Username must contain at least one letter!")

    # Ensure the username does not start with a number
    if username[0].isdigit():
        return fail("Username cannot start with a number!")

    # Check for invalid characters (anything other than letters, numbers, or underscores)
    if re.search(r'[^a-zA-Z0-9_]', username):
        return fail("Username can only contain letters, numbers, and underscores!")

    # Ensure the username is not entirely numeric
    if username.isdigit():
        return fail("Username cannot be only numbers!")

    # Check if the username already exists in the database
    if User.objects.filter(username=username).exists():
        return fail("Username already exists")

    # If all validations pass, set `is_valid` to True
    data["is_valid"] = True
    return data

def validate_pin(new_pin, confirm_pin):
    """
    Verifies that the provided PIN meets the following conditions:
    1. Both `new_pin` and `confirm_pin` are provided and match.
    2. PIN must be exactly 4 digits.
    3. PIN contains only numeric characters.

    Args:
        new_pin (str): The new PIN to be set.
        confirm_pin (str): The confirmation PIN to match.

    Returns:
        dict: A dictionary with:
              - 'is_valid' (bool): True if the PIN is valid, False otherwise.
              - 'message' (str): Validation result message.
    """
    data = {"is_valid": False, "message": ""}

    # Helper function to set the failure message and return the result
    def fail(message):
        data["message"] = message
        return data

    # Check if both new_pin and confirm_pin are provided
    if not new_pin or not confirm_pin:
        return fail("Both PIN and confirmation PIN are required.")

    # Check if the pins match
    if new_pin != confirm_pin:
        return fail("PINs do not match.")

    # Check if PIN length is exactly 4 digits
    if len(new_pin) != 4:
        return fail("PIN must be exactly 4 digits.")

    # Ensure PIN contains only numeric characters
    if not new_pin.isdigit():
        return fail("PIN can only contain numeric characters.")

    # If all checks pass
    data["is_valid"] = True
    return data

def validate_password(password, confirm_password):
    """
    Validates the provided password based on the following rules:
    1. Password must be at least 8 characters long.
    2. Password must include at least one uppercase letter.
    3. Password must include at least one numeric digit.
    4. Password must include at least one special character.
    5. Password and confirm_password must match.

    Args:
        password (str): The password to validate.
        confirm_password (str): Confirmation for the password.

    Returns:
        dict: A dictionary with:
              - 'is_valid' (bool): True if the password is valid, False otherwise.
              - 'message' (str): Validation result message.
    """
    data = {"is_valid": False, "message": ""}

    # Helper function to set failure messages and return result
    def fail(message):
        data["message"] = message
        return data

    # Check if both password and confirm_password are provided
    if not password or not confirm_password:
        return fail("Both fields are required.")

    # Check if passwords match
    if password != confirm_password:
        return fail("Passwords do not match.")

    # Check for minimum length
    if len(password) < 8:
        return fail("Password must be at least 8 characters long.")

    # Check for at least one uppercase letter
    if not any(char.isupper() for char in password):
        return fail("Password must contain at least one uppercase letter.")

    # Check for at least one number
    if not any(char.isdigit() for char in password):
        return fail("Password must contain at least one numeric digit.")

    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return fail("Password must contain at least one special character.")

    # If all checks pass
    data["is_valid"] = True
    return data

# Function to compress an image file
def compress_image(image_file, max_size_kb=2000):
    """
    Compresses an image to ensure its size is under the specified max size in kilobytes.
    
    Args:
        image_file: A file-like object representing the uploaded image.
        max_size_kb: Maximum allowed size of the image in kilobytes (default is 2000 KB or 2 MB).
    
    Returns:
        A BytesIO object containing the compressed image.
    """
    # Open the uploaded image using Pillow
    image = Image.open(image_file)
    
    # Create a temporary in-memory buffer to hold the compressed image
    buffer = BytesIO()

    # Save the image with initial compression (quality 85 for lossy formats like JPEG)
    image.save(buffer, format=image.format, optimize=True, quality=85)
    
    # Check if the image size exceeds the max allowed size
    # buffer.tell() gives the size of the data in the buffer in bytes
    while buffer.tell() > max_size_kb * 1024:  # max_size_kb is in KB, convert to bytes (1KB = 1024 bytes)
        # If the image is still too large, reset the buffer and reduce the quality further
        buffer = BytesIO()  # Reset the buffer for the next compression attempt
        
        # Dynamically adjust the quality to reduce the image size further
        # Lower the quality if the image size is still larger than the limit
        quality = max(10, int(85 * (max_size_kb * 1024 / buffer.tell())))  # Prevent quality from going below 10
        
        # Save the image again with the updated compression quality
        image.save(buffer, format=image.format, optimize=True, quality=quality)

    # Reset the buffer pointer to the beginning so it can be read from the start
    buffer.seek(0)
    
    # Return the in-memory buffer containing the compressed image
    return buffer