from django.db import migrations, models
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    Scholarship = apps.get_model('scholarships', 'Scholarship')
    for scholarship in Scholarship.objects.all():
        scholarship.slug = slugify(scholarship.title)
        scholarship.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('scholarships', '0001_initial'),
    ]

    operations = [
        # Step 1: Add slug field (nullable initially)
        migrations.AddField(
            model_name='scholarship',
            name='slug',
            field=models.SlugField(max_length=350, blank=True, default=''),
        ),
        # Step 2: Populate slugs for existing records
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
        # Step 3: Add unique constraint
        migrations.AlterField(
            model_name='scholarship',
            name='slug',
            field=models.SlugField(max_length=350, unique=True),
        ),
    ]
