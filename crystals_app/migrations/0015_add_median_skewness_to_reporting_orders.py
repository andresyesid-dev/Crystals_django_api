from django.db import migrations


def add_median_skewness_headers(apps, schema_editor):
    SpecificReportingOrder = apps.get_model('crystals_app', 'SpecificReportingOrder')
    GeneralReportingOrder = apps.get_model('crystals_app', 'GeneralReportingOrder')

    # Get all factory IDs that already have specific reporting order data
    specific_factory_ids = SpecificReportingOrder.objects.values_list('factory_id', flat=True).distinct()
    for factory_id in specific_factory_ids:
        existing = set(SpecificReportingOrder.objects.filter(factory_id=factory_id).values_list('value', flat=True))
        from django.db.models import Max
        max_order = SpecificReportingOrder.objects.filter(factory_id=factory_id).aggregate(m=Max('ordering'))['m'] or 0
        to_add = []
        if 'Median' not in existing:
            max_order += 1
            to_add.append(SpecificReportingOrder(factory_id=factory_id, value='Median', ordering=max_order))
        if 'Skewness' not in existing:
            max_order += 1
            to_add.append(SpecificReportingOrder(factory_id=factory_id, value='Skewness', ordering=max_order))
        if to_add:
            SpecificReportingOrder.objects.bulk_create(to_add)

    # Get all factory IDs that already have general reporting order data
    general_factory_ids = GeneralReportingOrder.objects.values_list('factory_id', flat=True).distinct()
    for factory_id in general_factory_ids:
        existing = set(GeneralReportingOrder.objects.filter(factory_id=factory_id).values_list('value', flat=True))
        from django.db.models import Max
        max_order = GeneralReportingOrder.objects.filter(factory_id=factory_id).aggregate(m=Max('ordering'))['m'] or 0
        to_add = []
        if 'Median' not in existing:
            max_order += 1
            to_add.append(GeneralReportingOrder(factory_id=factory_id, value='Median', ordering=max_order))
        if 'Skewness' not in existing:
            max_order += 1
            to_add.append(GeneralReportingOrder(factory_id=factory_id, value='Skewness', ordering=max_order))
        if to_add:
            GeneralReportingOrder.objects.bulk_create(to_add)


class Migration(migrations.Migration):

    dependencies = [
        ('crystals_app', '0014_historicreport_median_skewness_and_more'),
    ]

    operations = [
        migrations.RunPython(add_median_skewness_headers, migrations.RunPython.noop),
    ]
