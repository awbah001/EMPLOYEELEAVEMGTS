# Generated migration for leave_end_notification_sent field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slmsapp', '0019_alter_customuser_user_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff_leave',
            name='leave_end_notification_sent',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
