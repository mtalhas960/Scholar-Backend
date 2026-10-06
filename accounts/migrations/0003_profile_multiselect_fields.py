import json
from django.db import migrations, models


def convert_field_of_study(apps, schema_editor):
    """Convert existing string values to JSON arrays before column type change."""
    Profile = apps.get_model('accounts', 'profile')
    for profile in Profile.objects.all():
        old_value = profile.field_of_study
        if old_value and not old_value.startswith('['):
            profile.field_of_study = json.dumps([old_value])
        elif not old_value:
            profile.field_of_study = json.dumps([])
        # Already JSON array — leave as-is
        profile.save(update_fields=['field_of_study'])


def convert_financial_status(apps, schema_editor):
    """Drop old financial_status values (they're choice strings, not IDs)."""
    Profile = apps.get_model('accounts', 'profile')
    for profile in Profile.objects.all():
        profile.funding_preferences = json.dumps([])
        profile.save(update_fields=['funding_preferences'])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_profile_photo'),
    ]

    operations = [
        # Step 1: Convert existing string data to valid JSON arrays while column is still CharField
        migrations.RunPython(convert_field_of_study, migrations.RunPython.noop),
        # Step 2: Change field_of_study from CharField to JSONField
        migrations.AlterField(
            model_name='profile',
            name='field_of_study',
            field=models.JSONField(blank=True, default=list, help_text='List of FieldOfStudy IDs'),
        ),
        # Step 3: Add funding_preferences
        migrations.AddField(
            model_name='profile',
            name='funding_preferences',
            field=models.JSONField(blank=True, default=list, help_text='List of FundingType IDs'),
        ),
        # Step 4: Convert financial_status data (clear it)
        migrations.RunPython(convert_financial_status, migrations.RunPython.noop),
        # Step 5: Remove financial_status
        migrations.RemoveField(
            model_name='profile',
            name='financial_status',
        ),
    ]
