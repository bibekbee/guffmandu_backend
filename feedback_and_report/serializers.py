from rest_framework.serializers import ModelSerializer
from .models import FeedBackAndReport


class FeedBackAndReportSerializer(ModelSerializer):

    class Meta:
        model = FeedBackAndReport
        fields = "__all__"