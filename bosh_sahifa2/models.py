from django.db import models


class Invitation(models.Model):
    groom_name = models.CharField(max_length=100)
    bride_name = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    body = models.TextField(max_length=1000)
    event_date = models.DateField()
    event_time = models.TimeField()
    venue = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    phone = models.CharField(max_length=30, blank=True)
    template = models.CharField(max_length=100, default='wedding-1')
    slug = models.SlugField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class BotUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_seen']

    def __str__(self):
        return self.username or self.first_name or str(self.telegram_id)


class BotMessage(models.Model):
    chat_id = models.BigIntegerField(db_index=True)
    message_id = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['chat_id', 'message_id'])]

    def __str__(self):
        return f'{self.chat_id}:{self.message_id}'
