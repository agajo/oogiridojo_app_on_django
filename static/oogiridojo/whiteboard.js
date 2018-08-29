
var canvas, stage;
var drawingCanvas;
var oldPt;
var oldMidPt;
var title;
var color;
var stroke;

init();

function init() {
    canvas = document.getElementById("myCanvas");

    //check to see if we are running in a browser with touch support
    stage = new createjs.Stage(canvas);
    stage.autoClear = false;
    stage.enableDOMEvents(true);

    createjs.Touch.enable(stage);
    createjs.Ticker.framerate = 24;

    drawingCanvas = new createjs.Shape();

    stage.addEventListener("stagemousedown", handleMouseDown);
    stage.addEventListener("stagemouseup", handleMouseUp);

    title = new createjs.Text("ここに描く", "36px Arial", "#777777");
    title.x = 60;
    title.y = 130;
    stage.addChild(title);

    stage.addChild(drawingCanvas);
    stage.update();
}

function handleMouseDown(event) {
    if (!event.primary) { return; }
    if (stage.contains(title)) {
        stage.clear();
        stage.removeChild(title);
        //背景色を透明から白に
        var bg_shape = new createjs.Shape();
        bg_shape.graphics.f("white").dr(0,0,300,300);
        stage.addChild(bg_shape);
        stage.update();
        stage.removeChild(bg_shape);
        $("div#html_canvas").append('<input type="hidden" id="canvas_drawn">');
        // ↑何かが書かれたという証拠を残す。この要素がいない時は、絵を投稿しない。
    }
    color = "rgba(" + $("input[name=color]:checked").val() + "," + $("input[name=alpha]").val() + ")";
    stroke = $("input[name=thickness]:checked").val();
    oldPt = new createjs.Point(stage.mouseX, stage.mouseY);
    oldMidPt = oldPt.clone();
    stage.addEventListener("stagemousemove", handleMouseMove);
}

function handleMouseMove(event) {
    if (!event.primary) { return; }
    var midPt = new createjs.Point(oldPt.x + stage.mouseX >> 1, oldPt.y + stage.mouseY >> 1);

    drawingCanvas.graphics.clear().setStrokeStyle(stroke, 'round', 'round').beginStroke(color).moveTo(midPt.x, midPt.y).curveTo(oldPt.x, oldPt.y, oldMidPt.x, oldMidPt.y);

    oldPt.x = stage.mouseX;
    oldPt.y = stage.mouseY;

    oldMidPt.x = midPt.x;
    oldMidPt.y = midPt.y;

    stage.update();
}

function handleMouseUp(event) {
    if (!event.primary) { return; }
    stage.removeEventListener("stagemousemove", handleMouseMove);
}


