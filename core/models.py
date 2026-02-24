from django.db import models
from django.contrib.auth.models import User
import uuid


class Bolge(models.Model):
    ad = models.CharField(max_length=100)

    def __str__(self):
        return self.ad


class Isletme(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefon = models.CharField(max_length=20)
    bolge = models.ForeignKey(Bolge, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Kurye(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefon = models.CharField(max_length=20)
    bolgeler = models.ManyToManyField(Bolge)

    def __str__(self):
        return self.user.username


class Siparis(models.Model):

    ODEME_TIPLERI = [
        ('nakit', 'Nakit'),
        ('online', 'Online'),
        ('kart', 'Kart'),
        ('metropol', 'Metropol'),
    ]

    DURUM_SECENEKLERI = [
        ('bekliyor', 'Bekliyor'),
        ('alindi', 'Alındı'),
        ('teslim', 'Teslim Edildi'),
    ]

    fis_no = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    isletme = models.ForeignKey(Isletme, on_delete=models.CASCADE)
    teslim_bolge = models.ForeignKey(Bolge, on_delete=models.CASCADE)
    adres = models.CharField(max_length=255)
    odeme_tipi = models.CharField(max_length=20, choices=ODEME_TIPLERI)
    fis_foto = models.ImageField(upload_to="fisler/")
    alan_kurye = models.ForeignKey(Kurye, on_delete=models.SET_NULL, null=True, blank=True)
    durum = models.CharField(max_length=20, choices=DURUM_SECENEKLERI, default='bekliyor')
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sipariş {self.id}"