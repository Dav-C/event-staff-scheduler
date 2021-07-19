from django.urls import path

from .views import (
    Login,
    Logout,
    EventCreate,
    EventDetail,
    EventList,
    EventUpdate,
    EventDelete,
    EventPlanning,
    EventRelease,
    EventRestrict,
    SetTimeZone,
    TeamMessageCreate,
    TeamMessageUpdate,
    TeamMessageDelete,
    TeamMessageDetail,
)


urlpatterns = [
    path("login/", Login.as_view(), name="login"),
    path("logout", Logout.as_view(), name="logout"),
    path("set_timezone", SetTimeZone.as_view(), name="set_timezone"),
    path("events", EventList.as_view(), name="event_list"),
    path("events/create", EventCreate.as_view(), name="event_create"),
    path("events/<str:slug>/update", EventUpdate.as_view(), name="event_update"),
    path("events/<str:slug>", EventDetail.as_view(), name="event_detail"),
    path("events/<str:slug>/delete", EventDelete.as_view(), name="event_delete"),
    path("event-planning", EventPlanning.as_view(), name="event_planning"),
    path(
        "event-planning/event-release",
        EventRelease.as_view(),
        name="event_release",
    ),
    path(
        "event-planning/event-restrict",
        EventRestrict.as_view(),
        name="event_restrict",
    ),
    path(
        "team-message/create", TeamMessageCreate.as_view(), name="team_message_create"
    ),
    path(
        "team-message/<str:slug>/update",
        TeamMessageUpdate.as_view(),
        name="team_message_update",
    ),
    path(
        "team-message/<str:slug>/delete",
        TeamMessageDelete.as_view(),
        name="team_message_delete",
    ),
    path(
        "team-message/<str:slug>",
        TeamMessageDetail.as_view(),
        name="team_message_detail",
    ),
]
