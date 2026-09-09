from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("toylar", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="buyurtma",
            name="telegram_username",
            field=models.CharField(max_length=100, default=""),
            preserve_default=False,
        ),
    ]
