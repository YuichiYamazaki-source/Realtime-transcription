function startRecognition(){
    eel.start_recognition();
}

function stopRecognition(){
    eel.stop_recognition();
}

eel.expose(updateTranscript);
function updateTranscript(text){
    document.getElementById("transcript").innerHTML += text + "<br>"
}