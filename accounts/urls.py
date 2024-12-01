from django.urls import path
from . import views

# imports from rest_framework_simplejwt
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    
    # Authentication
    path("login/", views.LoginView.as_view(), name="login"),
    path("sign-up/", views.RegisterView.as_view(), name="sign_up"),
    path('token-refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User Profile Data
    path('auth-user-quick-data/', views.AuthUserQuickData.as_view(), name='auth_user_quick_data'),

    # User Profile Update Vides
    path("update-username/", views.UpdateUsernameView.as_view(), name="update_username"),
    path("update-profile-photo/", views.UpdateProfilePhotoView.as_view(), name="update_username"),
    path("update-password/", views.UpdatePasswordView.as_view(), name="update_username"),
    path("update-pin/", views.UpdatePINView.as_view(), name="update_username"),
]