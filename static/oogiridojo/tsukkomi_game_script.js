$(function(){
    $("#tsukkomi_game_start_button").on('click',function(){
        $(this).animate({opacity:0},500);
        $.ajax({//お題を一つ取得します。
            url:$(this).attr('formaction'),//APIのURLはボタンのformaction属性に記述しておく。
            type:'get',
            dataType:"json",
        }).done(function(return_odai){
            odai = return_odai["odai"];
            odai_id = return_odai["odai_id"];
            answers = return_odai["answers"];
            setTimeout(function(){$("#tsukkomi_game_start_button").remove();},500);
            setTimeout(countdown,400);
        });
    });
});

function countdown(){//3,2,1のカウントダウン。
    n = 3;//カウントダウンする秒数
    $("div#game_area").html("<p>お題："+odai+"</p>");
    id = setInterval(function(){
        $("div#game_area").append("<p class='countdown'>"+n+"</p>");
        n = n-1;
        if(n<0){//カウントダウンが終わったらいろいろ準備します。
            clearInterval(id);
            $("p.countdown").remove();//カウントダウン用DOM要素の削除
            m=0;//回答の数制御
            tsukkomis = new Array(5);//ツッコミを格納する配列
            main_game_start();
        };
    },1000);
}

function main_game_start(){
    $("div#game_area").append("<p>"+answers[m]["answer_text"]+"</p>");
    $("div#game_area").append("<input type='text' id='tsukkomi_input'>");
    $("input#tsukkomi_input").focus();
    n=15;//一つの回答の制限時間
    $("div#game_area").append("<p id='time_count'>"+n+"</p>");
    $("p#time_count").html(n);
    id = setInterval(function(){
        n = n-1;
        $("p#time_count").html(n);
        if(n<=0){
            clearInterval(id);
            $("p#time_count").remove();
            tsukkomis[m] = $("input#tsukkomi_input").val();
            $("input#tsukkomi_input").remove();
            $("div#game_area").append("<p>"+tsukkomis[m]+"</p>");
            m++;
            if(m>=5){//所定の回数だけツッコミを得たら、次にいきます。
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
    score = tsukkomis[0].length + tsukkomis[1].length + tsukkomis[2].length + tsukkomis[3].length + tsukkomis[4].length;
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
    append_text = "<p id='your_score_is'>今回の点数は：</p>"+
        "<p id='score'>"+score+"点です。</p>"+
        "<p id='comment'>"+comment+"</p>"+
        "<p>それぞれのツッコミを修正して投稿しましょう。</p>"+
        "<p>お題："+odai+"</p>"+
        "<ul class='list-group'>"+
        "<li class='list-group-item'>"+
        "<p>回答1："+answers[0].answer_text+"</p>"+
        "<p>ツッコミ："+tsukkomis[0]+"</p>"+
        "<input type='text' id='answer1' class='form-control' value='"+tsukkomis[0]+"'>"+
        "</li>"+
        "<li class='list-group-item'>"+
        "<p>回答2："+answers[1].answer_text+"</p>"+
        "<p>ツッコミ："+tsukkomis[1]+"</p>"+
        "<input type='text' id='answer2' class='form-control' value='"+tsukkomis[1]+"'>"+
        "</li>"+
        "<li class='list-group-item'>"+
        "<p>回答3："+answers[2].answer_text+"</p>"+
        "<p>ツッコミ："+tsukkomis[2]+"</p>"+
        "<input type='text' id='answer3' class='form-control' value='"+tsukkomis[2]+"'>"+
        "</li>"+
        "<li class='list-group-item'>"+
        "<p>回答4："+answers[3].answer_text+"</p>"+
        "<p>ツッコミ："+tsukkomis[3]+"</p>"+
        "<input type='text' id='answer4' class='form-control' value='"+tsukkomis[3]+"'>"+
        "</li>"+
        "<li class='list-group-item'>"+
        "<p>回答5："+answers[4].answer_text+"</p>"+
        "<p>ツッコミ："+tsukkomis[4]+"</p>"+
        "<input type='text' id='answer5' class='form-control' value='"+tsukkomis[4]+"'>"+
        "</li>"+
        "<button id='tsukkomi_game_submit_button' type='button' class='btn btn-danger'>投稿する</button>"+
        "強化のコツ"+
        "<ul>"+
        "<li>知ってるけど聞きなれない表現に言い換えてみましょう。</li>"+
        "<li>大げさなことを言ってみましょう。</li>"+
        "<li>複数解釈の余地を残さないようにしましょう。</li>"+
        "</ul>";
    $("div#game_area").append(append_text);
}

$(function(){
    $(document).on('click',"#tsukkomi_game_submit_button",function(){
        $.ajax({
            url:$("input#tsukkomi_game_submit_url").attr('formaction'),//APIのURLはformaction属性に記述しておく。
            type:'post',
            data:{
                "csrfmiddlewaretoken":$("input[name='csrfmiddlewaretoken']").val(),
                "aid1":answers[0].id,
                "aid2":answers[1].id,
                "aid3":answers[2].id,
                "aid4":answers[3].id,
                "aid5":answers[4].id,
                "answer1":$("input#answer1").val(),
                "answer2":$("input#answer2").val(),
                "answer3":$("input#answer3").val(),
                "answer4":$("input#answer4").val(),
                "answer5":$("input#answer5").val(),
            },
            dataType:"json",
        }).done(function(return_json){
            if("ok" in return_json){
                $("div#game_area").html("");
                $("div#game_area").css("text-align","center");
                $("div#game_area").append("<p>投稿しました。</p>");
                url = $("input#tsukkomi_game_url").attr('formaction');
                $("div#game_area").append("<a href='"+url+"'><button id='play_again' type='button' class='btn btn-danger'>もう一度プレイ</button></a>");
            }else{
                $("button#tsukkomi_game_submit_button").next("p.error_message").remove();
                setTimeout(function(){
                    $("button#tsukkomi_game_submit_button").after("<p class='error_message'>"+return_json["error"]+"</p>");
                },100);
            };
        });
    });
});
