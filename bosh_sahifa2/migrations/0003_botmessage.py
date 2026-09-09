from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("bosh_sahifa2", "0002_botuser")]

    operations = [
        migrations.CreateModel(
            name="BotMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("chat_id", models.BigIntegerField(db_index=True)),
                ("message_id", models.BigIntegerField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"indexes": [models.Index(fields=["chat_id", "message_id"], name="bosh_sahifa2_chat_id_8f9a2b_idx")]},
        ),
    ]
