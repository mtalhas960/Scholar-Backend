import json
from django.db import migrations, models


def migrate_field_of_study_to_m2m(apps, schema_editor):
    """Convert JSON array of IDs to M2M relations."""
    Profile = apps.get_model('accounts', 'profile')
    FieldOfStudy = apps.get_model('scholarships', 'FieldOfStudy')
    for profile in Profile.objects.all():
        raw = profile.field_of_study
        if isinstance(raw, str):
            try:
                ids = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                ids = []
        elif isinstance(raw, list):
            ids = raw
        else:
            ids = []
        for fid in ids:
            try:
                field = FieldOfStudy.objects.get(pk=int(fid))
                profile.field_of_study_m2m.add(field)
            except (FieldOfStudy.DoesNotExist, ValueError, TypeError):
                pass


def migrate_funding_to_m2m(apps, schema_editor):
    """Convert JSON array of IDs to M2M relations."""
    Profile = apps.get_model('accounts', 'profile')
    FundingType = apps.get_model('scholarships', 'FundingType')
    for profile in Profile.objects.all():
        raw = profile.funding_preferences
        if isinstance(raw, str):
            try:
                ids = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                ids = []
        elif isinstance(raw, list):
            ids = raw
        else:
            ids = []
        for fid in ids:
            try:
                ft = FundingType.objects.get(pk=int(fid))
                profile.funding_preferences_m2m.add(ft)
            except (FundingType.DoesNotExist, ValueError, TypeError):
                pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_profile_multiselect_fields'),
        ('scholarships', '0004_taxonomy_models'),
    ]

    operations = [
        # Step 1: Add M2M fields with temp names
        migrations.AddField(
            model_name='profile',
            name='field_of_study_m2m',
            field=models.ManyToManyField(blank=True, related_name='student_profiles', to='scholarships.fieldofstudy'),
        ),
        migrations.AddField(
            model_name='profile',
            name='funding_preferences_m2m',
            field=models.ManyToManyField(blank=True, related_name='student_profiles', to='scholarships.fundingtype'),
        ),
        # Step 2: Migrate data from JSON to M2M
        migrations.RunPython(migrate_field_of_study_to_m2m, migrations.RunPython.noop),
        migrations.RunPython(migrate_funding_to_m2m, migrations.RunPython.noop),
        # Step 3: Remove old JSON fields
        migrations.RemoveField(model_name='profile', name='field_of_study'),
        migrations.RemoveField(model_name='profile', name='funding_preferences'),
        # Step 4: Rename M2M fields to final names
        migrations.RenameField(model_name='profile', old_name='field_of_study_m2m', new_name='field_of_study'),
        migrations.RenameField(model_name='profile', old_name='funding_preferences_m2m', new_name='funding_preferences'),
    ]
