from datetime import datetime, date, timedelta

import calendar

from django.utils import timezone
from django.db.models import Q
from django.db.models.functions import ExtractMonth
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.models import User
from django.views.generic.edit import FormMixin
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from .forms import (
    EventForm,
    EventFormTeamMemberView,
    TeamMessageForm,
    UserProfileForm,
)
from .models import Event, TeamMessage, UserProfile


class Login(LoginView):
    template_name = "ess_app/login.html"


class Logout(LogoutView):
    next_page = "login"

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.add_message(request, messages.INFO, "Successfully logged out.")
        return response


class SetTimeZone(LoginRequiredMixin, View):
    """The timezone is always set to US/Pacific until the user overrides with
    a new timezone"""

    def get(self, request):
        user_profile = UserProfile.objects.get(user_id=request.user.id)
        timezone.activate(user_profile.timezone)
        current_timezone = timezone.get_current_timezone()
        messages.info(self.request, f"timezone set to {current_timezone}")
        return redirect("event_list")

    def post(self, request):
        timezone_selection = request.POST["timezone"]
        user_profile = UserProfile.objects.get(user_id=request.user.id)
        user_profile.timezone = timezone_selection
        user_profile.save()
        timezone.activate(user_profile.timezone)
        current_timezone = timezone.get_current_timezone()
        messages.info(self.request, f"timezone set to {current_timezone}")
        return redirect("event_list")


class EventList(LoginRequiredMixin, FormMixin, ListView):
    # form used for changing the user's timezone.
    form_class = UserProfileForm
    template_name = "ess_app/event_schedule.html"
    # initial values for search inputs in the options bar
    title_search = None
    min_date = None
    max_date = None
    max_date_default_value = (date.today() + timedelta(days=31)).strftime("%Y-%m-%d")
    # status filters
    status_filter = False
    planning_filter = False
    under_contract_filter = False
    approved_filter = False
    cancelled_filter = False
    # event type filters
    event_type_filter = False
    online_live_filter = False
    online_pre_recorded_filter = False
    online_hybrid_filter = False
    in_person_filter = False
    # released status filters
    released_restricted_filter = False
    released_restricted_filter_active = False
    no_team_members_assigned_filter = False
    selected_team_members_for_filtering = []
    # dictionary used to compare assigned team members to events in the queryset
    # this is so only assigned team members can edit the team member notes for a event
    per_event_assigned_team_members = {}

    def get_template_names(self):
        """Check for staff status (User model) and set the correct template."""
        if self.request.user.is_staff:
            self.template_name = "ess_app/event_schedule.html"
        else:
            self.template_name = "ess_app/event_schedule_team_member_view.html"
        return [self.template_name]

    def get_queryset(self):
        if self.request.user.is_staff:
            self.queryset = Event.return_30_days.all().prefetch_related("team_members")
        else:
            self.queryset = Event.return_30_days_released.all().prefetch_related(
                "team_members"
            )

        # get inputs from template (search/filter)
        self.title_search = self.request.GET.get("title_search")
        self.min_date = self.request.GET.get("min_date")
        self.max_date = self.request.GET.get("max_date")
        self.planning_filter = self.request.GET.get("planning_filter")
        self.under_contract_filter = self.request.GET.get("under_contract_filter")
        self.approved_filter = self.request.GET.get("approved_filter")
        self.cancelled_filter = self.request.GET.get("cancelled_filter")
        self.online_live_filter = self.request.GET.get("online_live_filter")
        self.online_pre_recorded_filter = self.request.GET.get(
            "online_pre_recorded_filter"
        )
        self.online_hybrid_filter = self.request.GET.get("online_hybrid_filter")
        self.in_person_filter = self.request.GET.get("in_person_filter")
        self.released_restricted_filter = self.request.GET.get(
            "released_restricted_filter"
        )
        self.no_team_members_assigned_filter = self.request.GET.get(
            "no_team_members_assigned_filter"
        )
        # create a list of team members who have been selected for filtering
        # this controls both the queryset filter and feeds into the context
        # so selected team members are "checked" when the page is reloaded
        self.selected_team_members_for_filtering = []
        for team_member in User.objects.filter(groups__name__exact="team_members"):
            team_member_id = self.request.GET.get(str(team_member.id))
            if team_member_id == str(team_member.id):
                self.selected_team_members_for_filtering.append(int(team_member_id))

        # check if a event type filter is active
        if (
            self.online_live_filter
            or self.online_pre_recorded_filter
            or self.online_hybrid_filter
            or self.in_person_filter
        ):
            self.event_type_filter = True

        # check if a status filter is active:
        if (
            self.planning_filter
            or self.under_contract_filter
            or self.approved_filter
            or self.cancelled_filter
        ):
            self.status_filter = True

        if self.min_date:
            if self.min_date > self.max_date or self.max_date == "" or None:
                messages.warning(self.request, "Please specify a valid date range")

            else:
                if self.request.user.is_staff:
                    self.queryset = (
                        Event.objects.order_by("start_datetime")
                        .filter(
                            start_datetime__date__gte=self.min_date,
                            start_datetime__date__lte=self.max_date,
                        )
                        .prefetch_related("team_members")
                    )
                else:
                    self.queryset = (
                        Event.objects.order_by("start_datetime")
                        .filter(
                            start_datetime__date__gte=self.min_date,
                            start_datetime__date__lte=self.max_date,
                            released=True,
                        )
                        .prefetch_related("team_members")
                    )

        if self.title_search:
            self.queryset = self.queryset.filter(title__icontains=self.title_search)

        """This section filters events either by team member names,
        events with no assigned team members or both options at the same time"""
        if (
            self.selected_team_members_for_filtering
            and self.no_team_members_assigned_filter
        ):
            self.queryset = self.queryset.filter(
                Q(team_members__id__in=self.selected_team_members_for_filtering)
                | Q(team_members=None)
            )
        if (
            self.selected_team_members_for_filtering
            and not self.no_team_members_assigned_filter
        ):
            self.queryset = self.queryset.filter(
                team_members__id__in=self.selected_team_members_for_filtering
            )
        if (
            self.no_team_members_assigned_filter
            and not self.selected_team_members_for_filtering
        ):
            self.queryset = self.queryset.filter(team_members=None)

        if self.event_type_filter:
            self.queryset = self.queryset.filter(
                Q(event_type__iexact=self.online_live_filter)
                | Q(event_type__iexact=self.online_pre_recorded_filter)
                | Q(event_type__iexact=self.online_hybrid_filter)
                | Q(event_type__iexact=self.in_person_filter)
            )

        if self.status_filter:
            self.queryset = self.queryset.filter(
                Q(status__iexact=self.planning_filter)
                | Q(status__iexact=self.under_contract_filter)
                | Q(status__iexact=self.approved_filter)
                | Q(status__iexact=self.cancelled_filter)
            )

        if self.released_restricted_filter:
            if self.released_restricted_filter == "released":
                self.queryset = self.queryset.filter(released=True)
            elif self.released_restricted_filter == "restricted":
                self.queryset = self.queryset.filter(released=False)
            elif self.released_restricted_filter == "released_and_restricted":
                self.queryset = self.queryset.filter(
                    Q(released=True) | Q(released=False)
                )
            self.released_restricted_filter_active = True

        # add event titles and the team member usernames assigned to those
        # events to a dictionary for comparison in the template. Only team members
        # assigned to a event should have access to the update url
        if not self.request.user.is_staff:
            self.per_event_assigned_team_members = {}
            for event in self.queryset:
                self.per_event_assigned_team_members[event.title] = []
                for team_member in event.team_members.all():
                    self.per_event_assigned_team_members[event.title].append(
                        team_member.username
                    )

        return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_team_members = User.objects.filter(groups__name__exact="team_members")
        all_team_messages = TeamMessage.objects.all()
        user_profile = UserProfile.objects.get(user_id=self.request.user.id)
        user_profile_initial_dict = {"timezone": user_profile.timezone}
        user_profile_form = UserProfileForm(initial=user_profile_initial_dict)

        context["all_team_members"] = all_team_members
        context["all_team_messages"] = all_team_messages
        context["title_search"] = self.title_search
        context["min_date"] = self.min_date
        context["max_date"] = self.max_date
        context["max_date_default_value"] = self.max_date_default_value
        context["planning_filter"] = self.planning_filter
        context["under_contract_filter"] = self.under_contract_filter
        context["approved_filter"] = self.approved_filter
        context["cancelled_filter"] = self.cancelled_filter
        context["event_type_filter"] = self.event_type_filter
        context["online_live_filter"] = self.online_live_filter
        context["online_pre_recorded_filter"] = self.online_pre_recorded_filter
        context["online_hybrid_filter"] = self.online_hybrid_filter
        context["in_person_filter"] = self.in_person_filter
        context["released_restricted_filter"] = self.released_restricted_filter
        context[
            "no_team_members_assigned_filter"
        ] = self.no_team_members_assigned_filter
        context[
            "selected_team_members_for_filtering"
        ] = self.selected_team_members_for_filtering
        context[
            "per_event_assigned_team_members"
        ] = self.per_event_assigned_team_members
        context["user_profile"] = user_profile
        context["user_profile_form"] = user_profile_form
        return context


class EventDetail(LoginRequiredMixin, DetailView):
    """Display the details of a single event"""

    queryset = Event.objects.all()
    template_name = None

    def get_template_names(self):
        """Check for staff status (User model) and set the correct template."""
        if self.request.user.is_staff:
            self.template_name = "ess_app/event_detail.html"
        else:
            self.template_name = "ess_app/event_detail_team_member_view.html"
        return [self.template_name]


class EventCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Create a new Event"""

    form_class = EventForm
    model = Event
    template_name = "ess_app/event_form.html"
    extra_context = {"update": False}

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        messages.success(self.request, "Event successfully created")
        url = self.object.get_absolute_url()

        return url

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.warning(self.request, "Insufficient permission to create events")
            return redirect("event_list")
        else:
            messages.warning(self.request, "please login to continue")
            return redirect("login")

    def has_permission(self):
        if self.request.user.is_staff:
            return True
        else:
            return False


class EventUpdate(LoginRequiredMixin, UpdateView):
    """Update an existing Event"""

    model = Event
    template_name = None
    extra_context = {"update": True}

    def get_form_class(self):
        """Check for staff status (User model) and set the form class."""
        return EventForm if self.request.user.is_staff else EventFormTeamMemberView

    def get_template_names(self):
        """Check for staff status (User model) and set the correct template."""
        if self.request.user.is_staff:
            self.template_name = "ess_app/event_form.html"
        else:
            self.template_name = "ess_app/event_form_team_member_view.html"
        return [self.template_name]

    def check_assigned_team_members(self, context, **response_kwargs):
        """check if a user is assigned as an event team member, if they are not,
        editing the event notes is prohibited and the user is redirected"""
        if self.request.user.is_authenticated:
            request_user_id = self.request.user.id
            team_members = self.object.team_members.all()
            assigned_team_members_id_list = []
            for team_member_id in team_members:
                assigned_team_members_id_list.append(team_member_id.id)
            if request_user_id in assigned_team_members_id_list:
                return self.response_class(
                    request=self.request,
                    template=self.get_template_names(),
                    context=context,
                    using=self.template_engine,
                    **response_kwargs,
                )
            else:
                messages.warning(self.request, "You are not assigned to this event")
                return redirect("event_list")

    def render_to_response(self, context, **response_kwargs):
        if self.request.user.is_staff:
            return super().render_to_response(context)
        else:
            return self.check_assigned_team_members(context)

    def get_success_url(self, **kwargs):
        """Return the URL to redirect to after processing a valid form."""
        messages.success(self.request, "event successfully updated")
        url = reverse_lazy("event_detail", kwargs={"slug": self.object.slug})
        return url


class EventDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Confirm and delete a Tag via HTML Form"""

    model = Event
    template_name = "ess_app/confirm_event_delete.html"
    success_url = reverse_lazy("event_list")

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.warning(self.request, "Insufficient permission to delete events")
            return redirect("event_list")
        else:
            messages.warning(self.request, "Please login to continue")
            return redirect("login")

    def has_permission(self):
        if self.request.user.is_staff:
            return True
        else:
            return False

    def get_success_url(self):
        """Return the URL to redirect to after deleting a event."""
        messages.success(self.request, "event successfully deleted")
        if self.success_url:
            return self.success_url.format(**self.object.__dict__)


class EventPlanning(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """View various data filters for schedule planning purposes"""

    template_name = "ess_app/event_planning.html"
    queryset = Event.objects.order_by("start_datetime").filter(
        start_datetime__year=datetime.today().year,
        start_datetime__month__gte=datetime.today().month,
        start_datetime__month__lte=datetime.today().month,
    )
    title_contains_query = None
    event_type_query = None
    status_query = None
    date_query = None
    online_live_events = None
    online_pre_recorded_events = None
    online_hybrid_events = None
    in_person_events = None
    all_events_in_selected_month = None
    event_count_by_team_member = None
    planning_calendar_dates = []
    released_restricted_events_by_month_current_year = None
    planning_events = None
    under_contract_events = None
    approved_events = None
    cancelled_events = None
    event_count_by_day_and_hour_online_live = None
    event_count_by_day_and_hour_online_pre_recorded = None
    event_count_by_day_and_hour_online_hybrid = None
    event_count_by_day_and_hour_in_person = None

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.warning(
                self.request, "Insufficient permission, you cannot access this page"
            )
            return redirect("event_list")
        else:
            messages.warning(self.request, "Please login to continue")
            return redirect("login")

    def has_permission(self):
        if self.request.user.is_staff:
            return True
        else:
            return False

    def get_queryset(self):
        # activate the users preferred timezone
        user_profile = UserProfile.objects.get(user_id=self.request.user.id)
        timezone.activate(user_profile.timezone)

        # get the contents of the search input and filter the queryset
        title_contains = self.request.GET.get("title_search")
        self.date_query = self.request.GET.get("date_query")
        if type(self.date_query) == str:
            self.date_query = datetime.strptime(self.date_query, "%Y-%m")
        elif self.date_query is None:
            self.date_query = date.today()
        event_type = self.request.GET.get("event_type")
        status = self.request.GET.get("status")

        self.queryset = Event.objects.order_by("start_datetime").filter(
            start_datetime__year__gte=self.date_query.year,
            start_datetime__year__lte=self.date_query.year,
        )

        # filter queryset by event type
        if event_type:
            if event_type == "online_live":
                self.queryset = self.queryset.filter(event_type__iexact="online_live")

            elif event_type == "online_pre_recorded":
                self.queryset = self.queryset.filter(
                    event_type__iexact="online_pre_recorded"
                )
            elif event_type == "online_hybrid":
                self.queryset = self.queryset.filter(event_type__iexact="online_hybrid")
            elif event_type == "in_person":
                self.queryset = self.queryset.filter(event_type__iexact="in_person")

        # filter queryset by text entered into "event names" search box
        if title_contains:
            self.queryset = self.queryset.filter(title__icontains=title_contains)

        # filter queryset by event status
        if status:
            if status == "planning":
                self.queryset = self.queryset.filter(status__iexact="planning")

            elif status == "under_contract":
                self.queryset = self.queryset.filter(status__iexact="under_contract")
            elif status == "approved":
                self.queryset = self.queryset.filter(status__iexact="approved")
            elif status == "cancelled":
                self.queryset = self.queryset.filter(status__iexact="cancelled")

        # create filtered query sets by event type for the count box (planning page)
        self.online_live_events = self.queryset.filter(
            start_datetime__month=self.date_query.month,
            event_type__iexact="online_live",
        )
        self.online_pre_recorded_events = self.queryset.filter(
            start_datetime__month=self.date_query.month,
            event_type__iexact="online_pre_recorded",
        )
        self.online_hybrid_events = self.queryset.filter(
            start_datetime__month=self.date_query.month,
            event_type__iexact="online_hybrid",
        )
        self.in_person_events = self.queryset.filter(
            start_datetime__month=self.date_query.month, event_type__iexact="in_person"
        )
        self.all_events_in_selected_month = self.queryset.filter(
            start_datetime__month=self.date_query.month,
        )

        # create queryset for team member/event count insight box
        all_team_members = User.objects.filter(groups__name__exact="team_members")
        self.event_count_by_team_member = (
            all_team_members.order_by("first_name")
            .filter(events__start_datetime__month=self.date_query.month)
            .annotate(Count("events"))
        )

        # event counts by month for the insight box in the upper block of the
        # planning page
        self.released_restricted_events_by_month_current_year = (
            Event.objects.filter(start_datetime__year=datetime.today().year)
            .annotate(month=ExtractMonth("start_datetime"))
            .values("month")
            .annotate(event_count_released=Count("id", filter=Q(released=True)))
            .annotate(event_count_restricted=Count("id", filter=Q(released=False)))
            .annotate(event_count_total=Count("id"))
            .order_by("month")
        )

        # Generate dates for the calendar (planning page)
        self.planning_calendar_dates = []
        calendar_dates = calendar.Calendar(firstweekday=6)
        days_of_the_month = calendar_dates.itermonthdates(
            self.date_query.year, self.date_query.month
        )

        # count events by event type and day/hour for lower block of planning page
        self.event_count_by_day_and_hour_online_live = (
            self.queryset.filter(event_type="online_live")
            .values("start_datetime")
            .annotate(event_count_online_live=Count("id"))
        )
        self.event_count_by_day_and_hour_online_pre_recorded = (
            self.queryset.filter(event_type="online_pre_recorded")
            .values("start_datetime")
            .annotate(event_count_online_pre_recorded=Count("id"))
        )
        self.event_count_by_day_and_hour_online_hybrid = (
            self.queryset.filter(event_type="online_hybrid")
            .values("start_datetime")
            .annotate(event_count_online_hybrid=Count("id"))
        )
        self.event_count_by_day_and_hour_in_person = (
            self.queryset.filter(event_type="in_person")
            .values("start_datetime")
            .annotate(event_count_in_person=Count("id"))
        )

        for calendar_date in days_of_the_month:
            self.planning_calendar_dates.append(calendar_date)

        return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # create context to populate the values of the search inputs so the
        # fields stay populated after a search
        self.title_contains_query = self.request.GET.get("title_search")
        self.event_type_query = self.request.GET.get("event_type")
        self.status_query = self.request.GET.get("status")

        context["title_contains_query"] = self.title_contains_query
        context["date_query"] = self.date_query
        context["event_type_query"] = self.event_type_query
        context["status_query"] = self.status_query
        context["online_live_events"] = self.online_live_events
        context["online_pre_recorded_events"] = self.online_pre_recorded_events
        context["online_hybrid_events"] = self.online_hybrid_events
        context["in_person_events"] = self.in_person_events
        context["event_count_by_team_member"] = self.event_count_by_team_member
        context["all_events_in_selected_month"] = self.all_events_in_selected_month
        context["planning_calendar_dates"] = self.planning_calendar_dates
        context[
            "released_restricted_events_by_month_current_year"
        ] = self.released_restricted_events_by_month_current_year
        context[
            "event_count_by_day_and_hour_online_live"
        ] = self.event_count_by_day_and_hour_online_live
        context[
            "event_count_by_day_and_hour_online_pre_recorded"
        ] = self.event_count_by_day_and_hour_online_pre_recorded
        context[
            "event_count_by_day_and_hour_online_hybrid"
        ] = self.event_count_by_day_and_hour_online_hybrid
        context[
            "event_count_by_day_and_hour_in_person"
        ] = self.event_count_by_day_and_hour_in_person

        return context


class EventRelease(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Release events based on a range of dates"""

    """Test for staff status. Non-staff, authenticated users, are 
    returned status 403"""

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.warning(self.request, "Insufficient permissions to release")
            return redirect("event_list")
        else:
            messages.warning(self.request, "Please login to continue")
            return redirect("login")

    def has_permission(self):
        if self.request.user.is_staff:
            return True
        else:
            return False

    def get(self, request):
        min_release_date = self.request.GET.get("min_release_date")
        max_release_date = self.request.GET.get("max_release_date")
        try:
            min_release_date = datetime.strptime(min_release_date, "%Y-%m-%d")
        except ValueError:
            messages.warning(self.request, "Please specify a valid date range")
            return redirect("event_planning")

        try:
            max_release_date = datetime.strptime(max_release_date, "%Y-%m-%d")
        except ValueError:
            messages.warning(self.request, "Please specify a valid date range")
            return redirect("event_planning")

        if min_release_date > max_release_date:
            messages.warning(self.request, "Please specify a valid date range")
        else:
            events = Event.objects.filter(
                start_datetime__date__gte=min_release_date,
                start_datetime__date__lte=max_release_date,
                released=False,
            )

            if events.count() >= 501:
                messages.warning(
                    self.request, "Event releases limited to 500 at a time"
                )

                return redirect("event_planning")

            else:
                for event in events:
                    event.released = True
                    event.save()
            messages.success(self.request, "events released successfully")

        return redirect("event_planning")


class EventRestrict(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Restrict events based on a range of dates"""

    """Test for staff status. Non-staff, authenticated users, are 
    returned status 403"""

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.warning(self.request, "Insufficient permissions to restrict")
            return redirect("event_list")
        else:
            messages.warning(self.request, "Please login to continue")
            return redirect("login")

    def has_permission(self):
        if self.request.user.is_staff:
            return True
        else:
            return False

    def get(self, request):
        min_restrict_date = self.request.GET.get("min_restrict_date")
        max_restrict_date = self.request.GET.get("max_restrict_date")

        try:
            min_restrict_date = datetime.strptime(min_restrict_date, "%Y-%m-%d")
        except ValueError:
            messages.warning(self.request, "Please specify a valid date range")
            return redirect("event_planning")
        try:
            max_restrict_date = datetime.strptime(max_restrict_date, "%Y-%m-%d")
        except ValueError:
            messages.warning(self.request, "Please specify a valid date range")
            return redirect("event_planning")

        if min_restrict_date > max_restrict_date:
            messages.warning(self.request, "Please specify a valid date range")
        else:
            events = Event.objects.filter(
                start_datetime__date__gte=min_restrict_date,
                start_datetime__date__lte=max_restrict_date,
                released=True,
            )

            if events.count() >= 501:
                messages.warning(
                    self.request, "event restrictions limited to 500 at a time"
                )

                return redirect("event_planning")

            else:
                for event in events:
                    event.released = False
                    event.save()
            messages.success(self.request, "events restricted successfully")

        return redirect("event_planning")


class TeamMessageCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Create a new Event"""

    form_class = TeamMessageForm
    model = TeamMessage
    template_name = "ess_app/team_message_form.html"
    extra_context = {"update": False}

    """Test for staff status. Non-staff, authenticated users, are 
    returned status 403"""

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.warning(
                self.request, "Insufficient permissions to create team messages"
            )
            return redirect("event_list")
        else:
            messages.warning(self.request, "Please login to continue")
            return redirect("login")

    def has_permission(self):
        if self.request.user.is_staff:
            return True
        else:
            return False

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        messages.success(self.request, "Team Message successfully created")
        url = self.object.get_absolute_url()

        return url


class TeamMessageUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Update an existing Team Message object"""

    form_class = TeamMessageForm
    model = TeamMessage
    template_name = "ess_app/team_message_form.html"
    extra_context = {"update": True}

    """Test for staff status. Non-staff, authenticated users, are 
    returned status 403"""

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.warning(
                self.request, "Insufficient permissions to update team messages"
            )
            return redirect("event_list")
        else:
            messages.warning(self.request, "Please login to continue")
            return redirect("login")

    def has_permission(self):
        if self.request.user.is_staff:
            return True
        else:
            return False

    def get_success_url(self, **kwargs):
        """Return the URL to redirect to after processing a valid form."""
        messages.success(self.request, "Team message successfully updated")
        url = reverse_lazy("team_message_detail", kwargs={"slug": self.object.slug})
        return url


class TeamMessageDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Confirm and delete a Team Message object"""

    model = TeamMessage
    template_name = "ess_app/confirm_team_message_delete.html"
    success_url = reverse_lazy("event_list")

    """Test for staff status. Non-staff, authenticated users, are 
    returned status 403"""

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.warning(
                self.request, "Insufficient permissions to delete team messages"
            )
            return redirect("event_list")
        else:
            messages.warning(self.request, "Please login to continue")
            return redirect("login")

    def has_permission(self):
        if self.request.user.is_staff:
            return True
        else:
            return False

    def get_success_url(self):
        """Return the URL to redirect to after deleting a event."""
        messages.success(self.request, "Team Message successfully deleted")
        if self.success_url:
            return self.success_url.format(**self.object.__dict__)


class TeamMessageDetail(LoginRequiredMixin, DetailView):
    """Display the details of a single Team Message Object"""

    queryset = TeamMessage.objects.all()
    template_name = "ess_app/team_message_detail.html"
