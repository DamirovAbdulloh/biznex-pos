from django.db import migrations

def create_default_roles(apps, schema_editor):
    Role = apps.get_model('employees', 'Role')
    Role.objects.get_or_create(name='Ofitsant')
    Role.objects.get_or_create(name='Oshpaz')

class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0002_employee_extras'),
    ]

    operations = [
        migrations.RunPython(create_default_roles, migrations.RunPython.noop),
    ]
