from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Offer
from .serializers import OfferSerializer

@api_view(["GET"])
@permission_classes([AllowAny])
def offers_list(request):
    qs = Offer.objects.filter(is_active=True).order_by("price_eur")
    data = OfferSerializer(qs, many=True).data
    return Response(data)
