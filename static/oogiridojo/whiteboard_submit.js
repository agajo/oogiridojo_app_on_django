$(function(){
    $("form#whiteboard_submit_form").on('submit',function(){
        if(!confirm("投稿します。いいですか？")){return false;}
        var canvas = document.getElementById("myCanvas");
        var datauri = canvas.toDataURL("image/jpeg",0.5);
        $('<input>')
        .attr('type','hidden')
        .attr('name','datauri')
        .attr('value', datauri)
        .appendTo('form#whiteboard_submit_form');
    });
});
