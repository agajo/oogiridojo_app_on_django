$(function(){
    var renda = 0;
    var jikoku = new Date;
    $(".free_vote_button").on('click',function(){
        if($("input#voice_toggle").prop('checked')){
            if(renda<19){
                nowjikoku = new Date;
                if(nowjikoku - jikoku > 5000){
                    renda=0;
                    jikoku = nowjikoku;
                }
                $("audio#sound-file1").get(0).currentTime = 0;
                $("audio#sound-file1").get(0).play();
                renda = renda+1;
            }else{
                $("audio#sound-file1").get(0).pause();
                $("audio#sound-file2").get(0).play();
                renda = 0;
            }
        }
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

    //回答の二重投稿防止。これで止めるのはボタン連打だけ。更新とかは関与しない。
    $("form#answer_form").submit(function(){
    //on click ではなく、formがsubmitされた時だけ実行。
        var me = $(this);
        //下層のfunction内にまで同じthisを渡してくれないので、変数に格納しておきます。
        me.find("input.answer_submit_button").prop("disabled",true);
        setTimeout(function(self){
            me.find("input.answer_submit_button").prop("disabled",false);
        }, 10000);
    });

    $("input#voice_toggle").on('click',function(){
        $.ajax({
            url:$(this).attr('formaction'),
            type: 'post',
            data: 'csrfmiddlewaretoken='+$(this).closest('form').find("input[name='csrfmiddlewaretoken']").val()+'&voice_toggle='+$(this).prop('checked'),
        });
    });

});
