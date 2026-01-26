# Generated migration for approval comments and saved filters

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('slmsapp', '0020_employee_leave_leave_end_notification_sent'),
    ]

    operations = [
        # Add approval comment fields to Employee_Leave
        migrations.AddField(
            model_name='staff_leave',
            name='dh_approval_comment',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='staff_leave',
            name='hr_approval_comment',
            field=models.TextField(blank=True, null=True),
        ),
        # Create SavedFilter model
        migrations.CreateModel(
            name='SavedFilter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('filter_type', models.CharField(choices=[('leave_review', 'Leave Review'), ('department_leaves', 'Department Leaves'), ('analytics', 'Analytics'), ('custom', 'Custom')], default='custom', max_length=50)),
                ('filter_params', models.JSONField()),
                ('is_default', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='saved_filters', to='slmsapp.customuser')),
            ],
            options={
                'verbose_name': 'Saved Filter',
                'verbose_name_plural': 'Saved Filters',
                'ordering': ['-is_default', '-updated_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='savedfilter',
            constraint=models.UniqueConstraint(fields=['user', 'name'], name='unique_user_filter_name'),
        ),
    ]
