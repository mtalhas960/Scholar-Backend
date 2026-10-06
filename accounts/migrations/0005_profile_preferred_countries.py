from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_profile_m2m_fields'),
        ('scholarships', '0005_add_image_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='preferred_countries',
            field=models.ManyToManyField(
                blank=True,
                related_name='interested_students',
                to='scholarships.country',
            ),
        ),
    ]
