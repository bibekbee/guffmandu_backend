from django.db import models

# Create your models here.
class FeedBackAndReport(models.Model):
    
    class Category(models.TextChoices):
        FEEDBACK = "feedback","Feedback"
        BUG = "bug","BUG"
        FEATURE_REQUEST = "feature_request","Feature_Request"

    category = models.CharField(max_length=16, choices=Category.choices)
    message = models.CharField(max_length=300)

    photo = models.ImageField(upload_to="feedback_and_report/", null=True, blank=True)

    email = models.EmailField(null=True, blank=True)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.message[0:11]
