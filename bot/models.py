from django.db import models


class TgUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=15, default='-')

    is_bot = models.BooleanField(default=False)
    language_code = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Joined')
    
    edit_msg = models.IntegerField(blank=True, null=True)

    step = models.IntegerField(default=0)

    deleted = models.BooleanField(default=False)

    def __str__(self):
        if self.last_name:
            return f'{self.first_name} {self.last_name}'
        else:
            return f'{self.first_name}'


class Product(models.Model):
    itemcode = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name


class Material(models.Model):
    products = models.ManyToManyField(Product, related_name='materials', blank=True)  # Many-to-many relationship
    itemcode = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name



from django.db.models import F

class Report(models.Model):
    CHOICES = [
        ("Kun", "Kun"),
        ("Tun", "Tun"),
    ]
    machine_num = models.IntegerField(verbose_name='aparat', null=True, blank=True)
    date = models.DateField()
    default_value = models.CharField(
        max_length=3, choices=CHOICES, default="Kun", blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    termoplast_measure = models.FloatField(blank=True, null=True)
    defect_measure = models.FloatField(blank=True, null=True, verbose_name='atxod')
    waste_measure = models.FloatField(blank=True, null=True, verbose_name='brak')
    material = models.ForeignKey(Material, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.FloatField(blank=True, null=True)
    is_confirmed = models.BooleanField(default=False)
    user = models.ForeignKey(to=TgUser, on_delete=models.CASCADE, related_name='reports')