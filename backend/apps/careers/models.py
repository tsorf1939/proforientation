from django.db import models


class Profession(models.Model):
    profession_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    avg_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    demand_level = models.IntegerField(null=True, blank=True)
    universities = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'professions'
        verbose_name = 'Профессия'
        verbose_name_plural = 'Профессии'
        constraints = [
            models.CheckConstraint(
                check=models.Q(demand_level__gte=1, demand_level__lte=5),
                name='profession_demand_range'
            )
        ]

    def __str__(self):
        return self.name


class ProfessionTypeWeights(models.Model):
    profession = models.OneToOneField(
        Profession, on_delete=models.CASCADE,
        related_name='type_weights', db_column='profession_id'
    )
    weight_people = models.IntegerField(default=0)
    weight_intellectual = models.IntegerField(default=0)
    weight_practical = models.IntegerField(default=0)
    weight_aesthetic = models.IntegerField(default=0)
    weight_physical = models.IntegerField(default=0)
    weight_administrative = models.IntegerField(default=0)

    class Meta:
        db_table = 'profession_type_weights'
        verbose_name = 'Веса профессии'
        verbose_name_plural = 'Веса профессий'
