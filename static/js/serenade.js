const notes = document.querySelectorAll(".note"); // urutan: 0 = do ... 7 = do tinggi
const playButton = document.getElementById("play-melody");
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

let audioContext; // dibuat saat pertama kali ada klik (browser melarang suara otomatis)

// --------------------------------------------------------------------------
// LAGU: Heavy Serenade (NMIXX). Not-notnya ada di song.js (SONG, SONG_BPM),
// --------------------------------------------------------------------------

function getAudioContext() {
  if (!audioContext) {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
  }
  if (audioContext.state === "suspended") {
    audioContext.resume();
  }
  return audioContext;
}

function midiToFrequency(midi) {
  return 440 * Math.pow(2, (midi - 69) / 12);
}

// Membunyikan satu nada.
// startAt = waktu mulai (detik, jam audioContext), length = lama (detik),
// output = tujuan suara (default: speaker).
function playTone(frequency, startAt = 0, length = 0.8, output) {
  const context = getAudioContext();
  const now = Math.max(startAt, context.currentTime);
  const end = now + length + 0.5; // sisa bunyi setelah tombol dilepas

  // Volume: naik cepat lalu turun pelan, supaya bunyinya lembut seperti piano
  const volume = context.createGain();
  volume.gain.setValueAtTime(0.0001, now);
  volume.gain.exponentialRampToValueAtTime(0.2, now + 0.015);
  volume.gain.exponentialRampToValueAtTime(0.0001, end);
  volume.connect(output || context.destination);

  // Dua osilator: nada utama + nada satu oktaf di atasnya (lebih pelan)
  [
    { type: "triangle", multiplier: 1, level: 1 },
    { type: "sine", multiplier: 2, level: 0.25 },
  ].forEach(({ type, multiplier, level }) => {
    const oscillator = context.createOscillator();
    const partVolume = context.createGain();
    oscillator.type = type;
    oscillator.frequency.value = frequency * multiplier;
    partVolume.gain.value = level;
    oscillator.connect(partVolume);
    partVolume.connect(volume);
    oscillator.start(now);
    oscillator.stop(end + 0.05);
  });
}

// Membuat not menyala sebentar (class "is-playing" diatur di CSS)
function lightUp(note) {
  note.classList.add("is-playing");
  setTimeout(() => note.classList.remove("is-playing"), 450);
}

function playNote(note) {
  playTone(Number(note.dataset.freq));
  lightUp(note);
}

// --------------------------------------------------------------------------
// Main sendiri: klik / sentuh not, Enter / Spasi saat not difokus,
// atau tombol angka 1-8 di keyboard.
// --------------------------------------------------------------------------
notes.forEach((note) => {
  note.addEventListener("click", () => playNote(note));
  note.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      playNote(note);
    }
  });
});

document.addEventListener("keydown", (event) => {
  // Jangan ganggu kalau pengguna sedang mengetik di kolom input
  if (["INPUT", "TEXTAREA", "SELECT"].includes(event.target.tagName)) return;
  if (event.ctrlKey || event.metaKey || event.altKey || event.repeat) return;

  const index = Number(event.key) - 1; // tombol 1 = do, ... tombol 8 = do tinggi
  if (index >= 0 && index < notes.length) {
    playNote(notes[index]);
  }
});

// --------------------------------------------------------------------------
// Memainkan lagu. Not dijadwalkan sedikit demi sedikit (bukan sekaligus),
// supaya ringan. Tombol berganti jadi "Berhenti" selama lagu berjalan.
// Not di paranada menyala mengikuti nada yang bunyi (hanya hiasan).
// --------------------------------------------------------------------------
const PLAY_LABEL = "Mainkan Heavy Serenade";
const STOP_LABEL = "Berhenti";
const LOOKAHEAD = 1; // jadwalkan not 1 detik ke depan

let isPlaying = false;
let scheduler; // setInterval yang menjadwalkan not
let songVolume; // volume utama lagu, dipakai untuk menghentikan suara seketika
const lightTimers = [];

function stopSong() {
  clearInterval(scheduler);
  lightTimers.forEach(clearTimeout);
  lightTimers.length = 0;
  if (songVolume) {
    songVolume.gain.value = 0;
    songVolume.disconnect();
  }
  isPlaying = false;
  if (playButton) playButton.textContent = PLAY_LABEL;
}

// Not paranada yang menyala: nada rendah ke tinggi dipetakan ke do ... do tinggi
function noteForMidi(midi) {
  return notes[Math.round(((midi % 12) / 11) * (notes.length - 1))];
}

function playSong() {
  if (isPlaying) return;
  isPlaying = true;
  if (playButton) playButton.textContent = STOP_LABEL;

  const context = getAudioContext();
  songVolume = context.createGain();
  songVolume.gain.value = 0.55; // beberapa nada sering bunyi bersamaan
  songVolume.connect(context.destination);

  const secondsPerBeat = 60 / SONG_BPM;
  const startTime = context.currentTime + 0.15;
  const endTime = SONG[SONG.length - 1][0]; // ketukan mulai not terakhir
  let next = 0; // indeks not berikutnya yang belum dijadwalkan

  scheduler = setInterval(() => {
    const horizon = context.currentTime + LOOKAHEAD;
    while (next < SONG.length) {
      const [beat, midi, beats] = SONG[next];
      const at = startTime + beat * secondsPerBeat;
      if (at > horizon) break;

      playTone(midiToFrequency(midi), at, beats * secondsPerBeat, songVolume);
      const delayMs = Math.max(0, (at - context.currentTime) * 1000);
      lightTimers.push(setTimeout(() => lightUp(noteForMidi(midi)), delayMs));
      next++;
    }

    // semua not sudah dijadwalkan dan sudah selesai berbunyi
    if (next >= SONG.length && context.currentTime > startTime + endTime * secondsPerBeat + 3) {
      stopSong();
    }
  }, 200);
}

if (playButton) {
  playButton.addEventListener("click", () => {
    if (isPlaying) {
      stopSong();
    } else {
      playSong();
    }
  });
}

// --------------------------------------------------------------------------
// Saat halaman dibuka: setelah not selesai naik, mereka menyala berurutan
// satu kali (tanpa suara) sebagai pembuka. Dilewati kalau pengguna
// mengaktifkan "reduce motion" di perangkatnya.
// --------------------------------------------------------------------------
if (!reducedMotion) {
  setTimeout(() => {
    notes.forEach((note, index) => {
      setTimeout(() => lightUp(note), index * 160);
    });
  }, 3000);
}
