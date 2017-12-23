$(function(){
    $(".judge_button").on('click',function(){
        if($(this).prev("input").val()!=""){
            $(this).prop("disbled",true);
            $.ajax({
                url:$(this).closest('form').attr('action'),
                type:'post',
                data:'csrfmiddlewaretoken='+$(this).closest('form').find("input[name='csrfmiddlewaretoken']").val()+'&answer_id='+$(this).closest('form').find("input[name='answer_id']").val()+'&judgement_score='+$(this).closest('form').find("input[name='judgement_score']:checked").val()+'&judgement_text='+$(this).closest('form').find("input[name='judgement_text']").val(),
                dataType:"json",
                context:$(this),
            }).done(function(return_judgement){
                if("score" in return_judgement){
                    $(this).closest("form").after(return_judgement["score"]).after(return_judgement["text"]);
                    $(this).closest("form").remove();
                }else if("error" in return_judgement){
                    $(this).after("<p>失敗</p>");
                };
            });
        };
    });

});
