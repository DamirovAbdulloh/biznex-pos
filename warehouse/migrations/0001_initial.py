from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Balance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Balans',
            },
        ),
        migrations.CreateModel(
            name='WarehouseItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Mahsulot nomi')),
                ('quantity', models.DecimalField(decimal_places=3, default=1, max_digits=12, verbose_name='Miqdori')),
                ('unit', models.CharField(default='dona', max_length=30, verbose_name="O'lchov birligi")),
                ('price_per_unit', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Birlik narxi')),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Jami narx')),
                ('note', models.TextField(blank=True, verbose_name='Izoh')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Ombor mahsuloti',
                'verbose_name_plural': 'Ombor mahsulotlari',
                'ordering': ['-created_at'],
            },
        ),
    ]
