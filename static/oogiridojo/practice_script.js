$(function(){
    $(".practice_submit_button").on('click',function(){
        // only if the form is not empty, then submit
        if($(this).prev("input").val()!=""){
            $.ajax({
                url:$(this).closest('form').attr('action'),
                type: 'post',
                data: 'csrfmiddlewaretoken='+$(this).closest('form').find("input[name='csrfmiddlewaretoken']").val()+'&article_id='+$(this).val()+'&practice_text='+$(this).prev("input").val(),
                dataType:"json",
                context:$(this),
            }).done(function(return_practice){
                $(this).parent().parent().next('ul.practice_list').prepend('<li class="practice_text list-group-item">'+return_practice["return_practice"]);
                $(this).prev("input").val("");
                ga('send', 'event', "practice", "practice_submit");
            });
        }
    });
});
