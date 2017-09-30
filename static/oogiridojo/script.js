$(function(){
    $(".free_vote_button").on('click',function(){
        event.preventDefault();
        $.ajax({
            url:$(this).parent('form').attr('action'),
            type: 'post',
            data: 'csrfmiddlewaretoken=' + $(this).closest('form').find("input[name='csrfmiddlewaretoken']").val() + '&free_vote_button=' + $(this).val()
        });
        location.reload();
    });
});
