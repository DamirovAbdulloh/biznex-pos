from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_order_kitchen_sent_at_is_paid'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_modified',
            field=models.BooleanField(default=False, help_text="Oshpazga yuborilgandan keyin o'zgartirilgan"),
        ),
    ]
