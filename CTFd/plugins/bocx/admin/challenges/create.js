CTFd.plugin.run((_CTFd) => {
    const $ = _CTFd.lib.$
    const md = _CTFd.lib.markdown()
})

$(document).ready(function () {
  //get CTF category Challenge selector
    $.getJSON("/api/v2/challenge-category/0", function (data) {
        $.each(data, function (index, item) {
            $('select#bocx_category').append($('<option>', { 
                value: item.id,
                text : item.category
            }));
        });
    });

   //get BOCX Teams
    $.getJSON("/api/v2/bocx_teams", function (data) {
        $.each(data, function (index, item) {
            $('select#team_id').append($('<option>', { 
                value: item.id,
                text : item.name
            }));
        });
    });

});
