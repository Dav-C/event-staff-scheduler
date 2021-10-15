from django import forms

from django.contrib.auth.models import User
from .models import Event, TeamMessage, UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["timezone", "user"]


class TeamMessageForm(forms.ModelForm):
    class Meta:
        model = TeamMessage
        fields = ["message_title", "message"]
        widgets = {
            "message_title": forms.TextInput(
                attrs={"class": "detail-box-form-field full-width"}
            ),
            "message": forms.Textarea(
                attrs={"class": "detail-box-form-field full-width"}
            ),
        }


class CustomMMCF(forms.ModelMultipleChoiceField):
    def label_from_instance(self, team_member):
        return f"{team_member.first_name} {team_member.last_name}"


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "title",
            "start_datetime",
            "end_datetime",
            "released",
            "event_type",
            "status",
            "event_notes",
            "team_members",
        ]

    team_members = CustomMMCF(
        required=False,
        queryset=User.objects.filter(groups__name__exact="team_members"),
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "detail-box-form-checkbox team-member-checkbox",
            }
        ),
    )
    start_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M:%S",
            attrs={
                "class": "detail-box-form-field date-time-field",
                "type": "datetime-local",
            },
        ),
    )
    end_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M:%S",
            attrs={
                "class": "detail-box-form-field date-time-field",
                "type": "datetime-local",
            },
        ),
    )


class EventFormTeamMemberView(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["team_member_notes"]
        widgets = {
            "team_member_notes": forms.Textarea(
                attrs={
                    "class": "event-detail-item event-notes-box",
                    "rows": 5,
                    "cols": 60,
                },
            ),
        }
