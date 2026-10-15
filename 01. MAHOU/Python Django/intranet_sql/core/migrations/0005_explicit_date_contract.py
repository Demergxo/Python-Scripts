from django.db import migrations

def forward(apps,schema_editor):
    Param=apps.get_model('core','QueryParam')
    # Preserve prior behavior for custom queries using lowercase fecha_fin,
    # except the supplied Pal_in_out which already includes its end with BETWEEN.
    Param.objects.filter(name='fecha_fin',param_type='date').exclude(query__code='Pal_in_out').update(add_one_day=True)

class Migration(migrations.Migration):
    dependencies=[('core','0004_queryparam_add_one_day')]
    operations=[migrations.RunPython(forward,migrations.RunPython.noop)]
