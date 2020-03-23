$(function($) {

  $('#root_field1').change(function(event){
    var root_id = $(this).val();
    var root_name = $( "#root_field1 option:selected" ).text();

    //Ajax Request
    $.getJSON(
        '/get_fields' + '/' + root_id,
        function(data){

            //Remove old options
            $('#field1').find('option').remove();

            //add root first
             $('#field1').append(
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
                $('#field1').append(
                    $('<option>', {
                        value: val['uuid'],
                        text: val['name']
                    })
                );
            });
        }
    );
  });




  $('#root_field2').change(function(event){
    var root_id = $(this).val();
    var root_name = $( "#root_field2 option:selected" ).text();

    //Ajax Request
    $.getJSON(
        '/get_fields' + '/' + root_id,
        function(data){

            //Remove old options
            $('#field2').find('option').remove();

            //add root first
             $('#field2').append(
                    $('<option>', {
                        value: root_id,
                        text: root_name + ' (root)'
                    })
             );

            //Add new items
            $.each(data, function(key, val){
                var option_item = '<option value="' + val['uuid'] + '">'+ val['name'] + '</option>'
                $('#field2').append(
                    $('<option>', {
                        value: val['uuid'],
                        text: val['name']
                    })
                );
            });
        }
    );
  });



  $('#field1').change(function(event){
    var field1_id = $(this).val();
    var field2_id = $( "#field2 option:selected" ).val();
    if (field2_id != ""){
        //Ajax Request
        $.getJSON(
            '/get_rel' + '/' + field1_id + '/' + field2_id,
            function(data){ //data = un string avec la bonne relation entre field1 et field2
                console.log(data);
                if(data.length === 0){
                    console.log(data.length);
                    $('#actual_rel').attr("value", '');
                }
                else{
                    $('#actual_rel').attr("value", data[0]['type']);
                }
            }
        );
    }
  });


  $('#field2').change(function(event){
    var field2_id = $(this).val();
    var field1_id = $( "#field1 option:selected" ).val();
    if (field1_id != ""){
        //Ajax Request
        $.getJSON(
            '/get_rel' + '/' + field1_id + '/' + field2_id,
            function(data){ //data = un string avec la bonne relation entre field1 et field2
                if(data.length === 0){
                    $('#actual_rel').attr("value", '');
                }
                else{
                    $('#actual_rel').attr("value", data[0]['type']);
                }
            }
        );
    }
  });



});