# Imports from rest_framework
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

# Improts from apps
from utilities.response_utilities import ResponseUtilities

# Importing serializers
from .serializers import FeedBackAndReportSerializer

class HandleFeedbackAndReport(APIView, ResponseUtilities):

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, format=None):
        serializer = FeedBackAndReportSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            self.success_status = True
            self.message_to_client = "We received your feedback ! Thank You So much !"
            print("Received a FeedBack!")
        else :
            self.message_to_client = "Data not in proper format!"

        return Response(self.get_generated_response())