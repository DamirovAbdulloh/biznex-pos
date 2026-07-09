from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_orderitem_sent_quantity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='is_modified',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='sent_quantity',
        ),
    ]
