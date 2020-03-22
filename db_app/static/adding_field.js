$(function($) {

    level = $("#level").val();
    if( level == 1){
        jQuery("label[for='root_field_attached']").hide();
        jQuery("#root_field_attached").hide();

        jQuery("label[for='level2_field']").hide();
        jQuery("#level2_field").hide();
    }

    if( level == 2){
        jQuery("label[for='root_field_attached']").show();
        jQuery("#root_field_attached").show();

        jQuery("label[for='level2_field']").hide();
        jQuery("#level2_field").hide();
    }

    if (level == 3){
        jQuery("label[for='root_field_attached']").show();
        jQuery("#root_field_attached").show();

        jQuery("label[for='level2_field']").show();
        jQuery("#level2_field").show();
    }

  $('#level').change(function(event){
    var level = $(this).val();
    //var level = $( "#root option:selected" );
    //level = $("#level").val();

    if( level == 1){
        jQuery("label[for='root_field_attached']").hide();
        jQuery("#root_field_attached").hide();

        jQuery("label[for='level2_field']").hide();
        jQuery("#level2_field").hide();
    }

    if( level == 2){
        jQuery("label[for='root_field_attached']").show();
        jQuery("#root_field_attached").show();

        jQuery("label[for='level2_field']").hide();
        jQuery("#level2_field").hide();
    }

    if (level == 3){
        jQuery("label[for='root_field_attached']").show();
        jQuery("#root_field_attached").show();

        jQuery("label[for='level2_field']").show();
        jQuery("#level2_field").show();
    }
   });

   $('#root_field_attached').change(function(event){
       var root_id = $("#root_field_attached").val();

        //Ajax Request
        $.getJSON(
            '/get_fields' + '/' + root_id,
            function(data){
                //Remove old options
                $('#level2_field').find('option').remove();

                //Add new items
                $.each(data, function(key, val){
                    var option_item = '<option value="' + val['uuid'] + '">'+ val['name'] + '</option>'
                    $('#level2_field').append(
                        $('<option>', {
                            value: val['uuid'],
                            text: val['name']
                        })
                    );
                });
            }
        );
    });
});