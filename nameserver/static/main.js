button = document.getElementById('sent-button')
form = document.getElementById('uploadFileModal')

button.addEventListener("click", function(){
    $('#uploadFileModal').modal('hide');
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
    // var ndata = {method: CREATE, not_create: true, file_name: file_name, path: window.location.pathname.substring(5)};
    // console.log(JSON.stringify(ndata));
    var ndata = new FormData();
    ndata.append("method", "CREATE");
    ndata.append("not_create", "true");
    ndata.append("file_name", file_name);
    ndata.append("path", window.location.pathname.substring(5));
    $.ajax({
        url: 'http://' + window.location.hostname+ ':5000/file/',
        type: 'POST', 
        dataType: 'json', 
        data: ndata,
        cache: false, 
        contentType: false,
        processData: false, 
        async: false,
        success: function(response){
        }
    });
}