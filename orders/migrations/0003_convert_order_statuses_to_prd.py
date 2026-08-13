# Data migration: convert order statuses from old vocabulary to PRD vocabulary
# pending→new, confirmed→paid, preparing→processing

from django.db import migrations


OLD_TO_NEW = {
    'pending': 'new',
    'confirmed': 'paid',
    'preparing': 'processing',
    # ready, completed, cancelled stay the same
}

NEW_TO_OLD = {
    'new': 'pending',
    'paid': 'confirmed',
    'processing': 'preparing',
}


def convert_statuses_forward(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    for old_val, new_val in OLD_TO_NEW.items():
        Order.objects.filter(status=old_val).update(status=new_val)


def convert_statuses_reverse(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    for new_val, old_val in NEW_TO_OLD.items():
        Order.objects.filter(status=new_val).update(status=old_val)


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_update_status_vocabulary'),
    ]

    operations = [
        migrations.RunPython(
            code=convert_statuses_forward,
            reverse_code=convert_statuses_reverse,
        ),
    ]
