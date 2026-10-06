"""
Migration 0004: Convert text fields to ForeignKey taxonomy references.

Steps:
1. Create taxonomy tables (StudyLevel, FundingType, Country, FieldOfStudy)
2. Populate from existing scholarship text data
3. Add FK fields to Scholarship
4. Copy data from old text fields to new FK fields
5. Remove old text fields
"""

from django.db import migrations, models
import django.db.models.deletion


def populate_taxonomies(apps, schema_editor):
    """Create taxonomy objects from existing scholarship data."""
    Scholarship = apps.get_model('scholarships', 'Scholarship')
    StudyLevel = apps.get_model('scholarships', 'StudyLevel')
    FundingType = apps.get_model('scholarships', 'FundingType')
    Country = apps.get_model('scholarships', 'Country')
    FieldOfStudy = apps.get_model('scholarships', 'FieldOfStudy')

    # Country flag mapping
    COUNTRY_FLAGS = {
        'Pakistan': ('🇵🇰', 'PK'),
        'United States': ('🇺🇸', 'US'),
        'Germany': ('🇩🇪', 'DE'),
        'United Kingdom': ('🇬🇧', 'GB'),
        'Turkey': ('🇹🇷', 'TR'),
        'Australia': ('🇦🇺', 'AU'),
        'European Union': ('🇪🇺', 'EU'),
        'China': ('🇨🇳', 'CN'),
        'Switzerland': ('🇨🇭', 'CH'),
        'Canada': ('🇨🇦', 'CA'),
        'Japan': ('🇯🇵', 'JP'),
        'South Korea': ('🇰🇷', 'KR'),
        'France': ('🇫🇷', 'FR'),
        'Sweden': ('🇸🇪', 'SE'),
        'Netherlands': ('🇳🇱', 'NL'),
        'New Zealand': ('🇳🇿', 'NZ'),
    }

    # Old value → new slug mapping for funding types (they were stored as slugs)
    FUNDING_SLUG_TO_NAME = {
        'fully_funded': 'Fully Funded',
        'partially_funded': 'Partially Funded',
        'tuition_only': 'Tuition Only',
        'stipend': 'Stipend Based',
    }

    import re

    def make_slug(name):
        return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

    # 1. Create StudyLevel objects
    levels = {}
    for s in Scholarship.objects.values_list('degree_level', flat=True).distinct():
        slug = make_slug(s)
        obj, _ = StudyLevel.objects.get_or_create(name=s, defaults={'slug': slug})
        levels[s] = obj

    # 2. Create FundingType objects
    fundings = {}
    for s in Scholarship.objects.values_list('funding_type', flat=True).distinct():
        name = FUNDING_SLUG_TO_NAME.get(s, s)
        slug = make_slug(name)
        obj, _ = FundingType.objects.get_or_create(name=name, defaults={'slug': slug})
        fundings[s] = obj

    # 3. Create Country objects
    countries = {}
    for s in Scholarship.objects.values_list('country', flat=True).distinct():
        flag_data = COUNTRY_FLAGS.get(s, ('', ''))
        slug = make_slug(s)
        obj, _ = Country.objects.get_or_create(name=s, defaults={'slug': slug, 'flag': flag_data[0], 'code': flag_data[1]})
        countries[s] = obj

    # 4. Create FieldOfStudy objects
    fields = {}
    for s in Scholarship.objects.values_list('field_of_study', flat=True).distinct():
        slug = make_slug(s)
        obj, _ = FieldOfStudy.objects.get_or_create(name=s, defaults={'slug': slug})
        fields[s] = obj

    # 5. Update scholarships with FK references
    for s in Scholarship.objects.all():
        s._country_id = countries[s.country].id
        s._degree_level_id = levels[s.degree_level].id
        s._field_of_study_id = fields[s.field_of_study].id
        s._funding_type_id = fundings[s.funding_type].id
        # Use update to avoid triggering save() which would try to use old fields
        Scholarship.objects.filter(pk=s.pk).update(
            _country_id=countries[s.country].id,
            _degree_level_id=levels[s.degree_level].id,
            _field_of_study_id=fields[s.field_of_study].id,
            _funding_type_id=fundings[s.funding_type].id,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('scholarships', '0003_add_application_url'),
    ]

    operations = [
        # 1. Create taxonomy models
        migrations.CreateModel(
            name='StudyLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=120, unique=True)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ['order', 'name'],
                'verbose_name_plural': 'Study Levels',
            },
        ),
        migrations.CreateModel(
            name='FundingType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=120, unique=True)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ['order', 'name'],
                'verbose_name_plural': 'Funding Types',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=120, unique=True)),
                ('flag', models.CharField(blank=True, help_text='Flag emoji, e.g. 🇺🇸', max_length=10)),
                ('code', models.CharField(blank=True, help_text='ISO 3166-1 alpha-2, e.g. US', max_length=2)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='FieldOfStudy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('slug', models.SlugField(max_length=220, unique=True)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ['order', 'name'],
                'verbose_name_plural': 'Fields of Study',
            },
        ),

        # 2. Add temporary FK fields (nullable)
        migrations.AddField(
            model_name='scholarship',
            name='_country',
            field=models.ForeignKey(
                to='scholarships.Country',
                on_delete=django.db.models.deletion.PROTECT,
                null=True,
                related_name='+',
            ),
        ),
        migrations.AddField(
            model_name='scholarship',
            name='_degree_level',
            field=models.ForeignKey(
                to='scholarships.StudyLevel',
                on_delete=django.db.models.deletion.PROTECT,
                null=True,
                related_name='+',
            ),
        ),
        migrations.AddField(
            model_name='scholarship',
            name='_field_of_study',
            field=models.ForeignKey(
                to='scholarships.FieldOfStudy',
                on_delete=django.db.models.deletion.PROTECT,
                null=True,
                related_name='+',
            ),
        ),
        migrations.AddField(
            model_name='scholarship',
            name='_funding_type',
            field=models.ForeignKey(
                to='scholarships.FundingType',
                on_delete=django.db.models.deletion.PROTECT,
                null=True,
                related_name='+',
            ),
        ),

        # 3. Populate FK data from text fields
        migrations.RunPython(populate_taxonomies, migrations.RunPython.noop),

        # 4. Remove old text fields
        migrations.RemoveField(
            model_name='scholarship',
            name='country',
        ),
        migrations.RemoveField(
            model_name='scholarship',
            name='degree_level',
        ),
        migrations.RemoveField(
            model_name='scholarship',
            name='field_of_study',
        ),
        migrations.RemoveField(
            model_name='scholarship',
            name='funding_type',
        ),

        # 5. Rename temp FK fields to final names
        migrations.RenameField(
            model_name='scholarship',
            old_name='_country',
            new_name='country',
        ),
        migrations.RenameField(
            model_name='scholarship',
            old_name='_degree_level',
            new_name='degree_level',
        ),
        migrations.RenameField(
            model_name='scholarship',
            old_name='_field_of_study',
            new_name='field_of_study',
        ),
        migrations.RenameField(
            model_name='scholarship',
            old_name='_funding_type',
            new_name='funding_type',
        ),
    ]
