from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    country = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='owner')
    viewers = models.ManyToManyField(User, through='UserRelation', related_name='viewers')
    
    add_in_favorites = models.IntegerField(null=True)

    def __str__(self):
        return f'Id {self.id}: Name {self.name}'


class UserRelation(models.Model):
    RATE_CHOICES = (
        (1, 'Bullshit'),
        (2, 'Bad'),
        (3, 'Normal'),
        (4, 'Good'),
        (5, 'Well'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    in_favorites = models.BooleanField(default=False)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True)

    def __str__(self):
        return f"Product: {self.product.name} - Rate {self.rate}"

    def save(self, *args, **kwargs):
        from .other_code import set_favorites

        creating = not self.pk 
        old_f = self.in_favorites

        super().save(*args, **kwargs)

        new_f = self.in_favorites

        if old_f != new_f or creating:
            set_favorites(self.product)


