$(function(){
    $(document).on('click',"button#answer_submit_button",function(){
        let datauri = "";
        if($("#myCanvas").length>0){
            if(!confirm("投稿します。いいですか？")){return false;}
            var canvas = document.getElementById("myCanvas");
            datauri = canvas.toDataURL("image/jpeg",0.7);
            if($("input#canvas_drawn").length==0){//何も書いてない時は絵を投稿しない処理
                datauri="";
            }
        }
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
                location.href = $("input#destination_input").val();
            }else{
                $("div#answer_text_row").next("p.error_message").remove();//返ったメッセージを表示する機構をindexとodai_detailに2018-08-29
                setTimeout(function(){
                    $("div#answer_text_row").after("<p class='error_message'>"+return_json["error"]+"</p>");
                },100);
            };
        });
    });
});
