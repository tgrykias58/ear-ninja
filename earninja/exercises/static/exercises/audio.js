const audioContext = new AudioContext();
let mainGainNode = null;


const playAudio = async (url, numRetries = 8) => {
    const response = await fetch(url);

    if (response.status == 404 && numRetries > 0) {
        // maybe celery task that generates this audio file hasn't finished yet
        // retry
        setTimeout(() => {
            playAudio(url, numRetries - 1);
        }, 500);
        return;
    }

    const buffer = await audioContext.decodeAudioData(await response.arrayBuffer());
    const source = audioContext.createBufferSource();
    source.buffer = buffer;

    source.connect(mainGainNode);
    source.start()
}

const changeVolume = () => {
    const volumeControl = document.querySelector("input[name='volume']");
    mainGainNode.gain.value = volumeControl.value;
    window.localStorage.setItem("volume", volumeControl.value);
}

const setupVolumeControl = () => {
    const volumeControl = document.querySelector("input[name='volume']");
    volumeControl.addEventListener("change", changeVolume, false);

    mainGainNode = audioContext.createGain();
    mainGainNode.connect(audioContext.destination);

    let volume = window.localStorage.getItem("volume");
    volume = volume ? volume : 0.5;
    volumeControl.setAttribute("value", volume);

    changeVolume();
}
