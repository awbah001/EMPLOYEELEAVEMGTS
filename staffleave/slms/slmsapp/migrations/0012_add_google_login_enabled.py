from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slmsapp', '0011_staff_leave_supporting_document_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='google_login_enabled',
            field=models.BooleanField(default=False),
        ),
    ]
