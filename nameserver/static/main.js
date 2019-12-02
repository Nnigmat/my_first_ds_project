button = document.getElementById('sent-button')
button.addEventListener("click", function(){
    $.ajax({
        type:'GET',
        url:"/get/storages",
        dataType:'text',
        success:function(data){
            sent_to_nodes(data)
        },
        fail:function(data){
            console.log('fail');
        }
})});

upload_file = document.getElementById('upload');


function sent_to_nodes(data){
    var node_url = data.split(",")[0];
    var data = new FormData($('#upload')[0]);
    var file_name = document.getElementById('inputGroupFile01').files[0].name;
    $.ajax({
        url: 'http://'+node_url+":8080/file" + window.location.pathname + file_name,
        type: 'POST',
        data: data,
        cache: false,
        contentType: false,
        processData: false,
        async: false,
        success: function(response){
        }
    });
}