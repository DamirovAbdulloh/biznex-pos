from django.db import migrations, models


def backfill_sent_quantity(apps, schema_editor):
    OrderItem = apps.get_model('orders', 'OrderItem')
    OrderItem.objects.filter(order__sent_to_kitchen=True).update(sent_quantity=models.F('quantity'))


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_order_is_modified'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='sent_quantity',
            field=models.DecimalField(decimal_places=2, default=0, help_text="Oshpazga so'nggi marta yuborilgan miqdor (0 = hali yuborilmagan)", max_digits=10),
        ),
        migrations.RunPython(backfill_sent_quantity, noop_reverse),
    ]
