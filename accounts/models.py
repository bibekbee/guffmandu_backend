from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    class Gender(models.TextChoices):
        MALE = 'm', 'Male'
        FEMALE = 'f', 'Female'
        OTHER = 'o', 'Other'

    # Login and Authentication
    email = models.EmailField(unique=True, null=False, blank=False)  # Unique email for user authentication
    username = models.CharField(max_length=25, unique=True, null=False, blank=False)  # Unique username
    account_number = models.IntegerField(unique=True, null=True, blank=True)

    # Profile Information
    # full_name = models.CharField(max_length=50)  # User's full name
    profile_photo = models.ImageField(default="default_profile_photo.jpg", upload_to="users_profile_photos/")  # Profile photo
    age = models.PositiveIntegerField(null=True, blank=True)  # User's age (optional)
    gender = models.CharField(max_length=1, choices=Gender.choices)  # User's gender

    # Verification and Security
    is_verified = models.BooleanField(default=False)  # Verification status

    # Financial Information
    balance = models.PositiveIntegerField(default=0)  # User's balance (initially 0)
    transaction_pin = models.IntegerField(
        validators=[MinValueValidator(1000), MaxValueValidator(9999)],
        help_text="4-digit PIN for account security",  # 4-digit PIN for added security
        null=True,
        blank=True
    )

    def __str__(self):
        return self.username  # String representation of the user object
    
    class Meta:
        ordering = ["username"]
    
    def remove_profile_photo(self):
        self.profile_photo = "default_profile_photo.jpg"
        self.save()