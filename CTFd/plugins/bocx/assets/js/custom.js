$(document).ready(function () {

  //challenge category update to select only one
 // $('input[name="challenge_category"]').on('change', function () {
  //  $('input[name="challenge_category"]').not(this).prop('checked', false);
 // });
  //challenge category update
  $("#category-challenge-edit-button").click(function () {
    $('input[name="challenge_category"]:checked').each(function () {
      if (this.value) {
        var chal = $.getJSON("/api/v2/category-challenge/" + this.value, function (data) {
          $.each(data, function (index, item) {
            $(".modal.cat_update .modal-body form").attr('action', '/api/v2/category-challenge/' + item.id);
            $(".modal.cat_update .modal-body input#bocx_category_name").val(item.category_name);
            $(".modal.cat_update .modal-body textarea#category_description").val(item.description);
            $(".modal.cat_update").modal("show");
          });
        });
      }
    });
  });
  
  //challenge category delete
//  $("#bocx-delete-button").click(function () {
  //  $('input[name="challenge_category"]:checked').each(function () {
    //  if (this.value) {
     //   $(".modal.cat_delete").modal("show");
    //  }
  //  });
 // });

   //confirm deletion of category category
  //$('.modal.cat_delete button#cat_delete').on('click', function (event) {
   // var $button = $(event.target); // The clicked button
   // var cat_id = null;
   // if ($button) {
     // $('input[name="challenge_category"]:checked').each(function () {
      //  cat_id = this.value;
     // });
     // if (cat_id) {
      //  $.ajax({
        //  url: "/api/v2/category-challenge/" + cat_id,
        //  dataType: 'json',
         // cache: false,
         // contentType: false,
         // processData: false,
         // data: this.value,
         // type: 'delete',
         // success: function (response) {
            //process response data
           // $.each(response, function (key, data) {
             // if (data.success) {
               // location.reload();
            //  }
           // });
         // },
         // error: function (response) {
            //error here
         // }
       // });
    //  }
   // }
 // });
	
});
