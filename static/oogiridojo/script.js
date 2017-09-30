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
            $(this).prev("strong").text("--"+newscore["newscore"]);
        });
    });
});
