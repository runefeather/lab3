function callingAllFunctions(){
	startTime();
	chooseQuote();
}


function startTime() {
    var today = new Date();
    var h = today.getHours();
    var m = today.getMinutes();
    var s = today.getSeconds();
    h = checkTime(h);
    m = checkTime(m);
    s = checkTime(s);

    var hour = h.toString();
    var minute = m.toString();
    var second = s.toString();

    var color = hour + minute + second;

    document.getElementById('time').innerHTML =
    "#" + hour + minute + second;
    document.body.style.background = "#" + color;
}
var t = setInterval(function(){ startTime() }, 200);

function checkTime(i) {
    if (i < 10) {i = "0" + i};  // add zero in front of numbers < 10
    return i;
}

var longQuote1 = "Are we human because we gaze at the stars?" + "<br/>" + "Or do we gaze at them because we are human?";
var longQuote2 = "And space and time sigh and laugh and" + "<br/>" + "continue dancing into the future.";
var longQuote3 = "But nothing here wants us," + "<br/>" + "knows what to say, nor begins by asking.";
var longQuote4 = "While I'm gone, dream me the world." + "<br/>" + "Something new for every night.";

var quotes = ["Anything's possible if you've got enough nerve.",
                "It unscrews the other way",
                "That's all there is.",
                "And the snakes start to sing.",
                "When you have nothing to say, set something on fire.",
                longQuote1,
                "Know yourself and go in swinging.",
                "I solemnly swear that I am upto no good.",
                "Of cabbages and kings.",
                "You are exploding stars and tragically forgotten truths.",
                "Esse quam videri.",
                longQuote2,
                "Tempted by control, controlled by temptation.",
                "And, I swear in that moment, we were infinite.",
                "No limits, Jonathan?.",
                "Doubt not the soul of the song that waits.",
                "Do you know where the wild things go?.",
                "You only live forever in the lights you make.",
                "D'Arvit!",
                longQuote3,
                "Trust me. I'm a genius.",
                "Rex corvus, parate regis corvi.",
                "This is sempiternal.",
                "I think the asking is whether we get back up again.",
                "Atra du evarinya ono varda.",
                longQuote4,
                "Pray to strange gods and receive strange answers."]

function chooseQuote(){
    //Random number between min (included) and max(excluded)
    var max = quotes.length;
    var min = 0;
    var num =   Math.floor(Math.random() * (max - min)) + min;
	var quote = quotes[num];
    document.getElementById('quote').innerHTML = quote;
    //Changes every seven minutes.
	var t = setTimeout(chooseQuote, 420000);
}
