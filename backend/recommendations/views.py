from rest_framework import generics, permissions
from rest_framework.response import Response
from catalog.serializers import ProductSerializer
from .engine import content_recommendations
from .models import UserInteraction

class RecommendationView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        product_id = request.query_params.get("product_id")
        products = content_recommendations(product_id, 8)
        if request.user.is_authenticated and product_id:
            UserInteraction.objects.create(user=request.user, product_id=int(product_id), interaction_type="VIEW")
        return Response(ProductSerializer(products, many=True).data)
