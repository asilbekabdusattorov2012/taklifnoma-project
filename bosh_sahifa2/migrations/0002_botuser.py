from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("bosh_sahifa2", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="BotUser",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("telegram_id", models.BigIntegerField(unique=True)),
                ("username", models.CharField(blank=True, max_length=100)),
                ("first_name", models.CharField(blank=True, max_length=150)),
                ("joined_at", models.DateTimeField(auto_now_add=True)),
                ("last_seen", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["-last_seen"]},
        ),
    ]
