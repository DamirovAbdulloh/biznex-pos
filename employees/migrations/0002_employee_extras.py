from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='pin_code',
            field=models.CharField(max_length=6, unique=True, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='commission_percent',
            field=models.DecimalField(max_digits=5, decimal_places=2, default=0),
        ),
        migrations.AddField(
            model_name='employee',
            name='daily_rate',
            field=models.DecimalField(max_digits=12, decimal_places=2, default=0),
        ),
        migrations.AddField(
            model_name='employee',
            name='monthly_rate',
            field=models.DecimalField(max_digits=12, decimal_places=2, default=0),
        ),
    ]
