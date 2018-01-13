$(function(){
    $("#answer_game_start_button").on('click',function(){
        $(this).animate({opacity:0},500);
        $.ajax({//お題を一つ取得します。
            url:$(this).attr('formaction'),//APIのURLはボタンのformaction属性に記述しておく。
            type:'get',
            dataType:"json",
        }).done(function(return_odai){
            odai = return_odai["odai"];
            odai_id = return_odai["odai_id"];
            setTimeout(function(){$("#answer_game_start_button").remove();},500);
            setTimeout(countdown,400);
        });
    });
});

function countdown(){//3,2,1のカウントダウン。
    n = 3;//カウントダウンする秒数
    id = setInterval(function(){
        $("div#game_area").html("<p id='countdown'>"+n+"</p>");
        n = n-1;
        if(n<0){//カウントダウンが終わったらいろいろ準備します。
            clearInterval(id);
            $("p#countdown").remove();//カウントダウン用DOM要素の削除
            $("div#game_area").html("<p id='odai'>"+odai+"</p>");//お題の表示
            m=0;//回答の数制御
            answer = new Array(3);//回答を格納する配列
            main_game_start();
        };
    },1000);
}

function main_game_start(){
    $("div#game_area").append("<input type='text' id='answer_input'>");
    $("input#answer_input").focus();
    n=2;//一つの回答の制限時間
    $("div#game_area").append("<p id='time_count'>"+n+"</p>");
    $("p#time_count").html(n);
    id = setInterval(function(){
        n = n-1;
        $("p#time_count").html(n);
        if(n<=0){
            clearInterval(id);
            $("p#time_count").remove();
            answer[m] = $("input#answer_input").val();
            $("input#answer_input").remove();
            $("div#game_area").append("<p>"+answer[m]+"</p>");
            m++;
            if(m>=3){//所定の回数だけ回答を得たら、次にいきます。
                $("div#game_area").animate({"opacity":0},1000,function(){
                    $("div#game_area").html("");
                    saitenchu();
                });
            }else{
                main_game_start();
            };
        };
    },1000);
}

function saitenchu(){
    $("div#game_area").css("opacity",1);
    $("div#game_area").append("<p id='saitenchu'>採点中…</p>");
    $("p#saitenchu").css("opacity",0);
    $("p#saitenchu").animate({"opacity":1},1500,function(){
        $("p#saitenchu").animate({"opacity":0},1500,function(){
            $("div#game_area").html("");
            enforce();
        });
    });
}

function enforce(){
    score = answer[0].length + answer[1].length + answer[2].length;
    if(score == 0){
        comment = "いやいや。何か入力してください。";
    }else if(score < 30){
        comment = "もう少しがんばりましょう。";
    }else if(score < 60){
        comment = "うん。いい感じです。";
    }else if(score < 100){
        comment = "おお！結構頑張りましたね！";
    }else{
        comment = "素晴らしい〜〜〜〜！！！！";
    };
    $("div#game_area").css("text-align","left");
    $("div#game_area").append("<p id='your_score_is'>今回の点数は：</p>");
    $("div#game_area").append("<p id='score'>"+score+"点です。</p>");
    $("div#game_area").append("<p id='comment'>"+comment+"</p>");
    $("div#game_area").append("<p>それぞれの回答をしっかり強化して、投稿しましょう。</p>");
    $("div#game_area").append("<ul class='list-group'>");
    $("div#game_area").append("<li class='list-group-item'>");
    $("div#game_area").append("<p>"+answer[0]+"</p>");
    $("div#game_area").append("<input type='text' id='answer1' class='form-control' value='"+answer[0]+"'>");
    $("div#game_area").append("</li>");
    $("div#game_area").append("<li class='list-group-item'>");
    $("div#game_area").append("<p>"+answer[1]+"</p>");
    $("div#game_area").append("<input type='text' id='answer2' class='form-control' value='"+answer[1]+"'>");
    $("div#game_area").append("</li>");
    $("div#game_area").append("<li class='list-group-item'>");
    $("div#game_area").append("<p>"+answer[2]+"</p>");
    $("div#game_area").append("<input type='text' id='answer3' class='form-control' value='"+answer[2]+"'>");
    $("div#game_area").append("</li>");
    $("div#game_area").append("<button id='answer_game_submit_button' type='button' class='btn btn-danger'>投稿する</button>");
    $("div#game_area").append("<p>強化のコツ</p>");
    $("div#game_area").append("<ul>");
    $("div#game_area").append("<li>知ってるけど聞きなれない表現に言い換えてみましょう。</li>");
    $("div#game_area").append("<li>大げさなことを言ってみましょう。</li>");
    $("div#game_area").append("<li>複数解釈の余地を残さないようにしましょう。</li>");
    $("div#game_area").append("</ul>");
}

$(function(){
    $(document).on('click',"#answer_game_submit_button",function(){
        $.ajax({
            url:$("input#answer_game_submit_url").attr('formaction'),//APIのURLはformaction属性に記述しておく。
            type:'post',
            data:{
                "csrfmiddlewaretoken":$("input[name='csrfmiddlewaretoken']").val(),
                "odai_id":odai_id,
                "answer1":$("input#answer1").val(),
                "answer2":$("input#answer2").val(),
                "answer3":$("input#answer3").val(),
            },
            dataType:"json",
        }).done(function(return_json){
            if("ok" in return_json){
                $("div#game_area").html("");
                $("div#game_area").append("<p>投稿しました。</p>");
                url = $("input#answer_game_url").attr('formaction');
                $("div#game_area").append("<a href='"+url+"'><button id='play_again' type='button' class='btn btn-danger'>もう一度プレイ</button></a>");
            }else{
                $("button#answer_game_submit_button").next("p.error_message").remove();
                setTimeout(function(){
                    $("button#answer_game_submit_button").after("<p class='error_message'>"+return_json["error"]+"</p>");
                },100);
            };
        });
    });
});
