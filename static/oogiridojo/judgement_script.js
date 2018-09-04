$(function(){
    $("button.judge_button").on('click',function(){
      const answer_id = $(this).val();
      //同じclassを持つボタンやinputは複数あるので、特定するためにanswer_idを使う
        if($("input#judgement_text_"+answer_id).val()!=""){
            $(this).prop("disabled",true);
            $.ajax({
                url:$(this).attr('formaction'),
                type:'post',
                data:{
                  'csrfmiddlewaretoken':$("input[name='csrfmiddlewaretoken']").val(),
                  'answer_id':answer_id,
                  'judgement_score':$("input[name='judgement_score_"+answer_id+"']:checked").val(),
                  'judgement_text':$("input#judgement_text_"+answer_id).val(),
                },
                dataType:"json",
                context:$(this),//done以降で$(this)を使うために必要らしい？
            }).done(function(return_judgement){
                if("score" in return_judgement){
                    $("div#input_container_"+answer_id).after("<div>"+return_judgement["score"]+"点。"+return_judgement["text"]+"</div>");
                    $("div#input_container_"+answer_id).remove();
                }else if("error" in return_judgement){
                    $(this).after("<p>サーバー側でエラー。"+return_judgement["error"]+"</p>");
                    $(this).prop("disabled",false);
                };
            });
        };
    });

});
