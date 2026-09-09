from django.contrib import admin
from .models import Buyurtma


@admin.register(Buyurtma)
class BuyurtmaAdmin(admin.ModelAdmin):
    list_display = ('ism', 'telegram_username', 'telefon', 'kategoriya', 'shablon', 'sana', 'yaratilgan')
    list_filter = ('kategoriya', 'sana')
    search_fields = ('ism', 'telegram_username', 'telefon', 'shablon', 'manzil')
