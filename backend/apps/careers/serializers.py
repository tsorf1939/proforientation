from rest_framework import serializers
from .models import Profession, ProfessionTypeWeights


class ProfessionTypeWeightsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionTypeWeights
        fields = [
            'weight_people', 'weight_intellectual', 'weight_practical',
            'weight_aesthetic', 'weight_physical', 'weight_administrative',
        ]


class ProfessionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = ['profession_id', 'name', 'category', 'avg_salary', 'demand_level']


class ProfessionDetailSerializer(serializers.ModelSerializer):
    type_weights = ProfessionTypeWeightsSerializer(read_only=True)

    class Meta:
        model = Profession
        fields = ['profession_id', 'name', 'category', 'description', 'avg_salary', 'demand_level', 'type_weights', 'universities']
