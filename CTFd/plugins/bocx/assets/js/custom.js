$(document).ready(function () {

 //bocx category update
  $("#bocx-add-button").click(function () {
      $(".modal.bocx_add").modal("show");
  });

 $('input[name="bocx_category"]').on('change', function () {
    $('input[name="bocx_category"]').not(this).prop('checked', false);
  });
  //bocx category update
  $("#bocx-edit-button").click(function () {
    $('input[name="bocx_category"]:checked').each(function () {
      if (this.value) {
        var chal = $.getJSON("/api/v2/challenge-category/" + this.value, function (data) {
          $.each(data, function (index, item) { console.log(item);
            $(".modal.bocx_update .modal-body form").attr('action', '/api/v2/challenge-category/' + item.id);
            $(".modal.bocx_update .modal-body input#challenge-bocx-category-name").val(item.category);
            $(".modal.bocx_update .modal-body textarea#challenge-bocx-category-description").val(item.description);
            $(".modal.bocx_update").modal("show");
          });
        });
      }
    });
  });

 //delete ctf  category
  $("#bocx-delete-button").click(function () {
    $('input[name="bocx_category"]:checked').each(function () {
      if (this.value) {
        $(".modal.bocx_delete").modal("show");
      }
    });
  });
   //confirm deletion of ctf category
  $('.modal.bocx_delete button#bocx_delete').on('click', function (event) {
    var $button = $(event.target); // The clicked button
    var bocx_id = null;
    if ($button) {
      $('input[name="bocx_category"]:checked').each(function () {
        bocx_id = this.value;
      });
      if (bocx_id) {
        $.ajax({
          url: "/api/v2/challenge-category/" + bocx_id,
          dataType: 'json',
          cache: false,
          contentType: false,
          processData: false,
          data: this.value,
          type: 'delete',
          success: function (response) {
            //process response data
            $.each(response, function (key, data) {
              if (data.success) {
                location.reload();
              }
            });
          },
          error: function (response) {
            //error here
          }
        });
      }
    }
  });
    

   //open bocx ctf category
   $(".unlock-category-link").on("click", function(event) {
     event.preventDefault();
      var categoryId = $(this).data("value");
      if (categoryId) {
        $.ajax({
          url: "/api/v2/ctf-category/" + categoryId,
          dataType: 'json',
          cache: false,
          contentType: false,
          processData: false,
          data: categoryId,
          type: 'post',
          success: function (response) {
            //process response data
            $.each(response, function (key, data) {
             //if succeess
              if(data.success){
                 window.location.href = "/challenges";
             }
            });
          },
          error: function (response) {
            // location.reload();
            console.log("errror:", response);
          }
        });
      }
  });

  //Add Category
  $('button#bocx_add').on('click', function (event) {
    // Handle the form data
   // event.preventDefault();
    var $button = $(event.target); // The clicked button
    var bocx_id = null;
     console.log("add category");
    if ($button) {
     // $('input[name="bocx_category"]:checked').each(function () {
      //  bocx_id = this.value;
     // });
     // if (bocx_id) {
        $.ajax({
          url: "/api/v2/challenge-category/0",
          dataType: 'json',
          cache: false,
          contentType: false,
          processData: false,
          data: 0,
          type: 'post',
          success: function (response) {
            //process response data
            $.each(response, function (key, data) {
              //console.log(response);
              if (data.success) {
                location.reload();
              }
            });
          },
          error: function (response) {
            //error here
          }
        });
     // }
    }
  });
//add servers inventory
$('input[name="server_logo_checkbox"]').on('change', function () {
    $('input[name="server_logo_checkbox"]').not(this).prop('checked', false);
  });
$("#team-server-edit-button").click(function () {
      $(".team_server_update").modal("show");
  });

});
