$(function($) {

  $('#root').change(function(event){
    var root_id = $(this).val();
    var root_name = $( "#root option:selected" ).text();

    //Ajax Request
    $.getJSON(
        '/get_fields' + '/' + root_id,
        function(data){

            //Remove old options
            $('#fields').find('option').remove();

            //add root first
             $('#fields').append(
                    $('<option>', {
                        value: root_id,
                        text: root_name + ' (root)'
                    })
             );

            //Add new items
            $.each(data, function(key, val){
                var option_item = '<option value="' + val['uuid'] + '">'+ val['name'] + '</option>'
                //$('#fields').append(option_item);
                //$('#fields').append(val['uuid'], val['name']);
                $('#fields').append(
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