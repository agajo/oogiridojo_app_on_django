$(function(){
    $(document).on('click',"button#answer_submit_button",function(){
        if(!confirm("投稿します。いいですか？")){return false;}
        var canvas = document.getElementById("myCanvas");
        var datauri = canvas.toDataURL("image/jpeg",0.7);
        $.ajax({
            url:$("button#answer_submit_button").attr('formaction'),//APIのURLはformaction属性に記述しておく。
            type:'post',
            data:{
                "csrfmiddlewaretoken":$("input[name='csrfmiddlewaretoken']").val(),
                "odai_id":$("input#odai_id_input").val(),
                "answer1":$("input#answer_text_input").val(),
                "datauri":datauri,
            },
            dataType:"json",
        }).done(function(return_json){
            if("ok" in return_json){
                location.href='../';
            }else{
                $("div#answer_text_row").next("p.error_message").remove();
                setTimeout(function(){
                    $("div#answer_text_row").after("<p class='error_message'>"+return_json["error"]+"</p>");
                },100);
            };
        });
    });
});
