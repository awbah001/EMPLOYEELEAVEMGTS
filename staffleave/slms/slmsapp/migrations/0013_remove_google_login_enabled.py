from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slmsapp', '0012_add_google_login_enabled'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='google_login_enabled',
        ),
    ]
