/* global console*/
/*jshint esversion: 6 */

if (document.body.classList.contains('main_navigation_available')) {
    // slide out navigation
    let navButton = document.getElementById("navButton"),
        navBar = document.getElementById("navBar");
    let navOpenClose = function () {
        "use strict";
        if (navBar.style.height === "15rem") {
            navBar.style.height = "0";
        } else {
            navBar.style.height = "15rem";
        }
    };
    navButton.addEventListener("click", navOpenClose, false);
    console.log('main navigation menu loaded successfully');
}

// planning page schedule release and restrict confirmation modal box
// and expand/collapse buttons
if (document.body.classList.contains('planning_page')) {
    let releaseScheduleConfirmBtn = document.getElementById("releaseScheduleConfirmBtn");
    let cancelScheduleReleaseBtn = document.getElementById("cancelScheduleReleaseBtn");
    let scheduleReleaseModal = document.getElementById("scheduleReleaseModal");
    let restrictScheduleConfirmBtn = document.getElementById("restrictScheduleConfirmBtn");
    let cancelScheduleRestrictBtn = document.getElementById("cancelScheduleRestrictBtn");
    let scheduleRestrictModal = document.getElementById("scheduleRestrictModal");
    document.querySelectorAll('.calendar-day-expand-btn').forEach(item => {
        "use strict";
        item.addEventListener('click', event => {
        let calendarDayBox = item.parentElement.parentElement;
        let collapseBtn = calendarDayBox.querySelector('.calendar-day-collapse-btn');
        let expandBtn = item;
        calendarDayBox.style.height = "auto";
        expandBtn.style.display = "none";
        collapseBtn.style.display = "inline";
        collapseBtn.addEventListener('click', event => {
            calendarDayBox.style.height = "25rem";
            collapseBtn.style.display = "none";
            expandBtn.style.display = "inline";
        });
      });
    });
    let openScheduleReleaseModal = function()  {
        "use strict";
        scheduleReleaseModal.style.display = "flex";
        releaseScheduleConfirmBtn.style.visibility = "hidden";
    };
    let closeScheduleReleaseModal = function() {
        "use strict";
        scheduleReleaseModal.style.display = "none";
        releaseScheduleConfirmBtn.style.visibility = "visible";
    };

    let openScheduleRestrictModal = function() {
        "use strict";
        scheduleRestrictModal.style.display = "flex";
        restrictScheduleConfirmBtn.style.visibility = "hidden";
    };

    let closeScheduleRestrictModal = function() {
        "use strict";
        scheduleRestrictModal.style.display = "none";
        restrictScheduleConfirmBtn.style.visibility = "visible";
    };
    releaseScheduleConfirmBtn.addEventListener("click", openScheduleReleaseModal, false);
    cancelScheduleReleaseBtn.addEventListener("click", closeScheduleReleaseModal, false);
    restrictScheduleConfirmBtn.addEventListener("click", openScheduleRestrictModal, false);
    cancelScheduleRestrictBtn.addEventListener("click", closeScheduleRestrictModal, false);
    console.log('schedule page modal onclick event listener successful');
}

// search filters, open and close
if (document.body.classList.contains('search_filters_available')) {
    let searchFilterBox = document.getElementById('searchFilterBox');
    let searchFilterButton = document.getElementById('searchFilterButton');
    let searchFilterCloseButton = document.getElementById('searchFilterCloseButton');
    let openSearchFilterBox = function() {
        "use strict";
        searchFilterBox.style.display = "inline";
    };
    let closeSearchFilterBox = function() {
        "use strict";
        searchFilterBox.style.display = "none";
    };
    searchFilterButton.addEventListener("click", openSearchFilterBox, false);
    searchFilterCloseButton.addEventListener("click", closeSearchFilterBox, false);

    console.log('search filter box loaded successfully');
}

// team message box, open and close
if (document.body.classList.contains('team_messages_available')) {
    let teamMessageDeliveryOpenBtn = document.getElementById("teamMessageDeliveryOpenBtn"),
        teamMessageDeliveryCloseBtn = document.getElementById("teamMessageDeliveryCloseBtn"),
        teamMessageDeliveryBox = document.getElementById("teamMessageDeliveryBox");
    let openTeamMessageBox = function() {
        "use strict";
        teamMessageDeliveryBox.style.height = "75%";
        teamMessageDeliveryBox.style.visibility = "visible";
    };
    let closeTeamMessageBox = function() {
        "use strict";
        teamMessageDeliveryBox.style.height = "0";
        teamMessageDeliveryBox.style.visibility = "hidden";
    };
    teamMessageDeliveryOpenBtn.addEventListener("click", openTeamMessageBox, false);
    teamMessageDeliveryCloseBtn.addEventListener("click", closeTeamMessageBox, false);

    console.log('team message box loaded successfully');
}

console.log('this application has been brought to you by David Cates.');