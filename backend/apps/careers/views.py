from rest_framework import generics, permissions
from .models import Profession
from .serializers import ProfessionListSerializer, ProfessionDetailSerializer
from .filters import ProfessionFilter


class ProfessionListView(generics.ListAPIView):
    queryset = Profession.objects.all().order_by('name')
    serializer_class = ProfessionListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = ProfessionFilter
    search_fields = ['name', 'category', 'description']
    ordering_fields = ['name', 'avg_salary', 'demand_level']


class ProfessionDetailView(generics.RetrieveAPIView):
    queryset = Profession.objects.select_related('type_weights')
    serializer_class = ProfessionDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'profession_id'
