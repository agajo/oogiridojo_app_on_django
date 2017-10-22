$(function(){
    $(".free_vote_button").on('click',function(){
        event.preventDefault();
        $.ajax({
            url:$(this).closest('form').attr('action'),
            type: 'post',
            data: 'csrfmiddlewaretoken=' + $(this).closest('form').find("input[name='csrfmiddlewaretoken']").val() + '&free_vote_button=' + $(this).val(),
            dataType:"json",
            context:$(this),
        }).done(function(newscore){
            $(this).prev("span").children("strong.free_vote_score").text(newscore["newscore"]);
        });
    });

    $(".tsukkomi_submit_button").on('click',function(){
        // only if the form is not empty, then submit
        if($(this).prev("input").val()!=""){
            $.ajax({
                url:$(this).attr('formaction'),
                type: 'post',
                data: 'csrfmiddlewaretoken='+$(this).closest('form').find("input[name='csrfmiddlewaretoken']").val()+'&answer_id='+$(this).val()+'&tsukkomi_text='+$(this).prev("input").val(),
                dataType:"json",
                context:$(this),
            }).done(function(return_tsukkomi){
                $(this).closest('div').next('ul.tsukkomi_list').append('<li class="tsukkomi_text">'+return_tsukkomi["return_tsukkomi"]);
                $(this).prev("input").val("");
            });
        }
    });

});
