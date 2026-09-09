from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql='''
CREATE TABLE IF NOT EXISTS "toylar_buyurtma" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "kategoriya" varchar(30) NOT NULL,
    "shablon" varchar(120) NOT NULL,
    "ism" varchar(100) NOT NULL,
    "telefon" varchar(30) NOT NULL,
    "sana" date NOT NULL,
    "manzil" varchar(250) NOT NULL,
    "qoshimcha" text NOT NULL,
    "izoh" text NOT NULL,
    "yaratilgan" datetime NOT NULL
)
''',
                    reverse_sql='DROP TABLE IF EXISTS "toylar_buyurtma";',
                ),
            ],
            state_operations=[
                migrations.CreateModel(
                    name='Buyurtma',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('kategoriya', models.CharField(choices=[
                            ('toy', "To‘y"),
                            ('yubley', 'Yubiley'),
                            ('tugilgan_kun', "Tug‘ilgan kun"),
                            ('qiz', 'Qiz uzatish'),
                            ('el_oshi', 'El oshi'),
                        ], max_length=30)),
                        ('shablon', models.CharField(max_length=120)),
                        ('ism', models.CharField(max_length=100)),
                        ('telefon', models.CharField(max_length=30)),
                        ('sana', models.DateField()),
                        ('manzil', models.CharField(max_length=250)),
                        ('qoshimcha', models.TextField(blank=True, default='{}')),
                        ('izoh', models.TextField(blank=True)),
                        ('yaratilgan', models.DateTimeField(auto_now_add=True)),
                    ],
                    options={'ordering': ['-yaratilgan']},
                ),
            ],
        ),
    ]
