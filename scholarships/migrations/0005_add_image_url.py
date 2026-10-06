from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scholarships', '0004_taxonomy_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='scholarship',
            name='image_url',
            field=models.URLField(blank=True, help_text='Scholarship card image URL', max_length=500),
        ),
    ]