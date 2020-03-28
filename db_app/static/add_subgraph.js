$(function($) {
    var fieldNum = 0;
    $("#addsubfield").click(function() {
        var newInput = $("<li><label for=flist-"+fieldNum+ " class=form-label></label><input required type='text' id= flist-"+fieldNum+ " name=flist-"+fieldNum+ " value=''></input></li>")
        //.attr("class", "form-control")
        //.attr("id", "flist-" + fieldNum)
        //.attr("name", "flist-" + fieldNum)
        $("#flist").append(newInput);
        fieldNum++;
    });
});
