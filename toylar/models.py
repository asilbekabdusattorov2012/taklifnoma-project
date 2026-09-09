from django.db import models


class Buyurtma(models.Model):
    KATEGORIYA = [
        ('toy', "To‘y"),
        ('yubley', 'Yubiley'),
        ('tugilgan_kun', "Tug‘ilgan kun"),
        ('qiz', 'Qiz uzatish'),
        ('el_oshi', 'El oshi'),
    ]

    kategoriya = models.CharField(max_length=30, choices=KATEGORIYA)
    shablon = models.CharField(max_length=120)
    ism = models.CharField(max_length=100)
    telefon = models.CharField(max_length=30)
    telegram_username = models.CharField(max_length=100)
    sana = models.DateField()
    manzil = models.CharField(max_length=250)
    # Kategoriya bo‘yicha barcha qo‘shimcha maydonlar JSON sifatida saqlanadi.
    qoshimcha = models.TextField(blank=True, default='{}')
    izoh = models.TextField(blank=True)
    yaratilgan = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-yaratilgan']

    def __str__(self):
        return f'{self.ism} — {self.shablon}'
