from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("core", "0005_explicit_date_contract")]
    operations = [
        migrations.AddField(
            model_name="query",
            name="database_alias",
            field=models.CharField(
                max_length=16,
                default="externa",
                choices=[("externa", "XGA habitual"), ("mahou", "XGA Mahou")],
            ),
        )
    ]
