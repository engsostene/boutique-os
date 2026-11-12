from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Confirm that the Boutique OS backend is running.

    This endpoint is public so that the frontend and monitoring
    tools can check API availability without logging in.
    """
    return Response({
        "application": "Rwanda Boutique OS",
        "status": "operational",
        "message": "Backend API is responding successfully.",
    })
