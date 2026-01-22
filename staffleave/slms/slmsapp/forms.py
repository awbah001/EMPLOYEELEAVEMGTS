from django import forms
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()


class NotificationForm(forms.ModelForm):
    """Form for sending notifications"""

    class Meta:
        model = Notification
        fields = ['title', 'message', 'notification_type', 'recipient']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter notification title'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter your message'
            }),
            'notification_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'recipient': forms.Select(attrs={
                'class': 'form-select',
                'id': 'recipient-select'
            })
        }
        labels = {
            'notification_type': 'Priority Level',
            'title': 'Subject',
        }

    def __init__(self, *args, **kwargs):
        self.sender = kwargs.pop('sender', None)
        super().__init__(*args, **kwargs)

        # Filter recipients to exclude the sender and inactive users
        if self.sender:
            self.fields['recipient'].queryset = User.objects.filter(
                is_active=True
            ).exclude(id=self.sender.id)

        # Set default notification type choices
        self.fields['notification_type'].choices = [
            ('info', '📘 Information'),
            ('warning', '⚠️ Warning'),
            ('success', '✅ Success'),
            ('error', '❌ Error'),
            ('reminder', '⏰ Reminder'),
        ]


class BulkNotificationForm(forms.Form):
    """Form for sending bulk notifications to multiple recipients"""

    recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'id': 'recipients-select'
        }),
        required=True,
        label="Select Recipients"
    )
    title = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter notification title'
        }),
        label="Subject"
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Enter your message'
        })
    )
    notification_type = forms.ChoiceField(
        choices=[
            ('info', '📘 Information'),
            ('warning', '⚠️ Warning'),
            ('success', '✅ Success'),
            ('error', '❌ Error'),
            ('reminder', '⏰ Reminder'),
        ],
        initial='info',
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label="Priority Level"
    )

    def __init__(self, *args, **kwargs):
        self.sender = kwargs.pop('sender', None)
        super().__init__(*args, **kwargs)

        # Exclude sender from recipients if sender is provided
        if self.sender:
            self.fields['recipients'].queryset = User.objects.filter(
                is_active=True
            ).exclude(id=self.sender.id)
