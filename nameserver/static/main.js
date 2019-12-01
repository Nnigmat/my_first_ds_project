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
    node_url = data.split(" ")[0]

    $.ajax({
        url: 'http://'+node_url+":8080"+"/file/",
        type: 'post',
        dataType: 'json',
        data: new FormData($('upload').closest('form')[0]),
        cache: false,
        contentType: false,
        processData: false,
        success: function(response){
        }
    });
}