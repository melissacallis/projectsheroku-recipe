// select_all.js
$("#selectall").change(function() {
    if ($(this).is(":checked")) {
        $(".checkboxSelection").prop('checked', true);
    } else {
        $(".checkboxSelection").prop('checked', false);
    }
});
