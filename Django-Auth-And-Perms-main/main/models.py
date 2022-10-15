from django.db import models
from django.contrib.auth.models import User


class DiaryDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    diary_name = models.CharField(max_length=16, unique=True, default="set")
    first_name = models.CharField(max_length=16, default="first")
    last_name = models.CharField(max_length=16, default="last")
    gender = models.CharField(max_length=1, default="M")
    age = models.SmallIntegerField(default=0)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.diary_name + " " + self.first_name + " " + self.last_name


class Diet(models.Model):
    user = models.ForeignKey(DiaryDetails, on_delete=models.CASCADE)
    food_name = models.CharField(max_length=16, default="food")
    Grams = models.DecimalField(max_digits=8, decimal_places=2, default=None, blank=True, null=True)
    Energy = models.DecimalField(max_digits=5, decimal_places=2, default=None, blank=True, null=True)
    Fat = models.DecimalField(max_digits=5, decimal_places=2, default=None, blank=True, null=True)
    Carbohydrate = models.DecimalField(max_digits=5, decimal_places=2, default=None, blank=True, null=True)
    Protein = models.DecimalField(max_digits=5, decimal_places=2, default=None, blank=True, null=True)
    Fiber = models.DecimalField(max_digits=5, decimal_places=2, default=None, blank=True, null=True)
    Sugars = models.DecimalField(max_digits=5, decimal_places=2, default=None, blank=True, null=True)
    Sodium = models.DecimalField(max_digits=5, decimal_places=2, default=None, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.food_name + " " + str(self.Energy)
