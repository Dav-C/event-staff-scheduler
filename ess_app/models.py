import uuid
from datetime import date, timedelta
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django_extensions.db.fields import AutoSlugField


class Return30DaysEventManager(models.Manager):
    """return only 30 days of events for use in the EventList View"""

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .order_by("start_datetime")
            .filter(
                start_datetime__date__gte=date.today(),
                start_datetime__date__lte=date.today() + timedelta(days=31),
            )
        )


class Return30DaysReleasedEventManager(models.Manager):
    """return only 30 days of events for use in the EventList View"""

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .order_by("start_datetime")
            .filter(
                start_datetime__date__gte=date.today(),
                start_datetime__date__lte=date.today() + timedelta(days=31),
                released=True,
            )
        )


class UserProfile(models.Model):
    class Meta:
        verbose_name = "User Profile Information"
        verbose_name_plural = "Profiles"
        ordering = ["user"]

    timezone_choices = [
        ("US/Arizona", "US/Arizona"),
        ("US/Central", "US/Central"),
        ("US/Eastern", "US/Eastern"),
        ("US/Mountain", "US/Mountain"),
        ("US/Pacific", "US/Pacific"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    timezone = models.CharField(
        max_length=50, choices=timezone_choices, default="US/Pacific"
    )

    def __str__(self):
        return f"{self.user} profile information"


@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()


class Event(models.Model):
    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        indexes = [
            models.Index(fields=["start_datetime"]),
        ]

    event_type_choices = [
        ("online_live", "Online - Live"),
        ("online_pre_recorded", "Online - Pre-Recorded"),
        ("online_hybrid", "Online - Hybrid"),
        ("in_person", "In Person"),
    ]
    status_choices = [
        ("planning", "Planning"),
        ("under_contract", "Under Contract"),
        ("approved", "Approved"),
        ("cancelled", "Cancelled"),
    ]

    title = models.CharField(max_length=200)
    slug = AutoSlugField(
        max_length=100,
        help_text="event slug field",
        unique=True,
        populate_from=[
            "title",
            "start_datetime__month",
            "start_datetime__day",
            "start_datetime__year",
        ],
    )
    start_datetime = models.DateTimeField(blank=True, null=True)
    end_datetime = models.DateTimeField(blank=True, null=True)
    released = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=status_choices, blank=False)
    event_type = models.CharField(
        max_length=50, choices=event_type_choices, blank=False
    )
    event_notes = models.TextField(
        max_length=500,
        blank=True,
    )
    team_member_notes = models.TextField(max_length=500, blank=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team_members = models.ManyToManyField(
        User, related_name="events", blank=True, default=None
    )
    objects = models.Manager()
    return_30_days = Return30DaysEventManager()
    return_30_days_released = Return30DaysReleasedEventManager()

    def get_absolute_url(self):
        return reverse("event_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return f"{self.title}: {self.start_datetime.date()}"


class TeamMessage(models.Model):
    class Meta:
        verbose_name = "Team Message"
        verbose_name_plural = "Team Messages"
        ordering = ["-created_at"]

    slug = AutoSlugField(
        max_length=100,
        help_text="Team Messages",
        populate_from=["message_title"],
        unique=True,
    )
    message_title = models.CharField(max_length=50, blank=False)
    message = models.TextField(max_length=500, blank=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def get_absolute_url(self):
        return reverse("team_message_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return f"{self.created_at}: {self.message_title}"
