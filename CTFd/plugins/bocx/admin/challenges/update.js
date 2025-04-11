CTFd.plugin.run((_CTFd) => {
    const $ = _CTFd.lib.$
    const md = _CTFd.lib.markdown()
})
$(document).ready(function () {
  //get CTF category Challenge selector
    $.getJSON("/api/v2/challenge-category/0", function (data) {
         $.each(data, function (index, item) {
           var option = $('<option>', {
            value: item.id,
            text: item.category
        });

        if (item.id == window.CHALLENGE_CTF_CATEGORY) { 
            option.prop('selected', true); 
        } 
        $('select#bocx_category').append(option);
        });
    });
   
  //get BOCX Teams
    $.getJSON("/api/v2/bocx_teams", function (data) {
        $.each(data, function (index, item) {
           var option = $('<option>', {
            value: item.id,
            text: item.name
           });

          if (item.id == window.CHALLENGE_TEAM_ID) { 
            option.prop('selected', true); 
          } 
          $('select#team_id').append(option);
        });
    });
  //save updated challenges
//   $('#challenge-update-container form').submit(function(event) {
  //  event.preventDefault();
    //var selectedCat = $('#bocx_category option:selected').val();
   // var selectedTeam = $('#team_id option:selected').val();  
   // $.ajax({
     //  url: "/api/v2/challenge-update/" + window.CHALLENGE_ID,
     //  dataType: 'json',
     //  cache: false,
     //  contentType: 'application/json; charset=utf-8',
     //  processData: false,
      // data: JSON.stringify({'bocx_category': selectedCat,'team_id': selectedTeam }),
      // type: 'post',
      // success: function (response) {
         //process response data
        // if(response == true){
          //  location.reload();
       //  }
       // },
      // error: function (response) {
                  //error here
     //  }
    // });

   // });


});

