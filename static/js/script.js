window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

(function() {
  const VENUE_DELETE_BUTTON = document.querySelector("#delete_venue");
  if (VENUE_DELETE_BUTTON) {
    const VENUE_ID = VENUE_DELETE_BUTTON.dataset.id;
    if (VENUE_ID) {
      VENUE_DELETE_BUTTON.addEventListener("click", () => {
        fetch(`/venues/${VENUE_ID}`, {
          method: "DELETE",
          redirect: "follow"
        }).then(result => {
          window.location = "/";
        });
      });
    }
  }
})();
