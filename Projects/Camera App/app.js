const DB_NAME = 'PolaroidDB';
const STORE_NAME = 'photos';
const DEVELOPMENT_TIME_MS = 4 * 60 * 60 * 1000; // 4 Hours

// --- Globals ---
let db;
let videoStream;

// --- DOM Elements ---
const videoEl = document.getElementById('camera-feed');
const galleryBtn = document.getElementById('gallery-btn');
const backBtn = document.getElementById('back-btn');
const shutterBtn = document.getElementById('shutter-btn');
const cameraView = document.getElementById('camera-view');
const galleryView = document.getElementById('gallery-view');
const canvas = document.getElementById('capture-canvas');
const developingGrid = document.getElementById('developing-grid');
const developedGrid = document.getElementById('developed-grid');

// --- Initialization ---
async function init() {
    // Register Service Worker for Offline Support
    if ('serviceWorker' in navigator) {
        try {
            await navigator.serviceWorker.register('sw.js');
            console.log('Service Worker Registered');
        } catch (e) {
            console.error('Service Worker Failed', e);
        }
    }

    await initDB();
    setupCamera();
    setupEventListeners();
    // Load gallery on start to be ready
    loadGallery();

    // Start a ticker to update countdowns
    setInterval(updateCountdowns, 1000);
}

// --- Database (IndexedDB) ---
function initDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, 1);

        request.onerror = (event) => {
            console.error("DB Error", event);
            reject(event);
        };

        request.onupgradeneeded = (event) => {
            db = event.target.result;
            if (!db.objectStoreNames.contains(STORE_NAME)) {
                db.createObjectStore(STORE_NAME, { keyPath: 'id' });
            }
        };

        request.onsuccess = (event) => {
            db = event.target.result;
            resolve(db);
        };
    });
}

function savePhotoToDB(photo) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction([STORE_NAME], 'readwrite');
        const store = transaction.objectStore(STORE_NAME);
        const request = store.add(photo);

        request.onsuccess = () => resolve();
        request.onerror = (e) => reject(e);
    });
}

function getPhotosFromDB() {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction([STORE_NAME], 'readonly');
        const store = transaction.objectStore(STORE_NAME);
        const request = store.getAll();

        request.onsuccess = () => resolve(request.result);
        request.onerror = (e) => reject(e);
    });
}

// --- Camera ---
async function setupCamera() {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        try {
            videoStream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: 'environment', // Rear camera preferably
                    aspectRatio: { ideal: 4 / 3 }
                },
                audio: false
            });
            videoEl.srcObject = videoStream;
        } catch (err) {
            console.error("Camera access denied or error", err);
            alert("Camera access required for the Polaroid experience!");
        }
    }
}

// --- Sound FX ---
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
function playShutterSound() {
    // Synthetic "Click-Clack"
    if (audioCtx.state === 'suspended') audioCtx.resume();

    const t = audioCtx.currentTime;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    const noise = audioCtx.createBufferSource();

    // Quick burst of white noise for the mechanical "Clack"
    const bufferSize = audioCtx.sampleRate * 0.1; // 0.1s
    const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
        data[i] = Math.random() * 2 - 1;
    }
    noise.buffer = buffer;
    noise.connect(gain);
    gain.connect(audioCtx.destination);

    noise.start(t);
    gain.gain.setValueAtTime(1, t);
    gain.gain.exponentialRampToValueAtTime(0.01, t + 0.1);
}

// --- Actions ---
shutterBtn.addEventListener('click', async () => {
    // 0. Sound
    playShutterSound();

    // 1. Mechanical Animation
    // Target the specific blade div inside the layout
    const shutterMechanism = document.querySelector('.shutter-mechanism');
    shutterMechanism.classList.add('shutter-active');

    // Remove class after animation finishes (0.25s in CSS)
    setTimeout(() => shutterMechanism.classList.remove('shutter-active'), 300);

    // 2. Capture (slightly delayed to match closure point)
    setTimeout(() => capturePhoto(), 125);
});

function capturePhoto() {
    const context = canvas.getContext('2d');

    // Set canvas dimensions to video dimensions
    const vWidth = videoEl.videoWidth;
    const vHeight = videoEl.videoHeight;

    // We want a square crop for the "Polaroid Image" part
    // Cropping from center
    const size = Math.min(vWidth, vHeight);
    const startX = (vWidth - size) / 2;
    const startY = (vHeight - size) / 2;

    canvas.width = 600; // Resolution for storage
    canvas.height = 600;

    // Draw video frame to canvas
    context.drawImage(videoEl, startX, startY, size, size, 0, 0, 600, 600);

    // Convert to Base64 (JPEG)
    // Quality 0.8 is fine for "bar pics"
    const dataUrl = canvas.toDataURL('image/jpeg', 0.8);

    const photo = {
        id: Date.now().toString(),
        timestamp: Date.now(),
        imageData: dataUrl
    };

    savePhotoToDB(photo).then(() => {
        console.log("Photo saved!");
        loadGallery(); // Refresh gallery logic
    }).catch(e => console.error("Save failed", e));
}

// --- Navigation ---
galleryBtn.addEventListener('click', () => {
    loadGallery();
    cameraView.classList.remove('active');
    galleryView.classList.add('active');
    // Optional: Pause camera stream to save battery
});

backBtn.addEventListener('click', () => {
    galleryView.classList.remove('active');
    cameraView.classList.add('active');
});

// --- Gallery Logic ---
async function loadGallery() {
    const photos = await getPhotosFromDB();
    // Sort Newest -> Oldest
    photos.sort((a, b) => b.timestamp - a.timestamp);

    developingGrid.innerHTML = '';
    developedGrid.innerHTML = '';

    const now = Date.now();

    photos.forEach(photo => {
        const timeDiff = now - photo.timestamp;
        const isDeveloped = timeDiff >= DEVELOPMENT_TIME_MS;

        const card = document.createElement('div');
        card.className = 'polaroid-card';
        // Add random rotation for organic feel
        // Hash the ID to make rotation consistent for same photo
        const randomRot = (parseInt(photo.id.slice(-3)) % 10) - 5;
        card.style.setProperty('--rotation', `${randomRot}deg`);

        if (isDeveloped) {
            // DEVELOPED
            card.innerHTML = `
                <img src="${photo.imageData}" alt="Polaroid">
                <div>${new Date(photo.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
            `;
            developedGrid.appendChild(card);
        } else {
            // DEVELOPING
            card.classList.add('developing');
            card.dataset.timestamp = photo.timestamp; // For timer update

            // Calculate remaining
            const remainingMs = DEVELOPMENT_TIME_MS - timeDiff;
            const hours = Math.floor(remainingMs / (1000 * 60 * 60));
            const minutes = Math.floor((remainingMs % (1000 * 60 * 60)) / (1000 * 60));

            card.innerHTML = `
                <img src="${photo.imageData}" alt="Developing...">
                <div class="timer-overlay">${hours}h ${minutes}m</div>
                <div>Developing...</div>
            `;
            developingGrid.appendChild(card);
        }
    });

    // Check empty states
    if (developingGrid.children.length === 0) developingGrid.innerHTML = '<p style="text-align:center; grid-column: 1/-1; color: #555;">No photos developing.</p>';
    if (developedGrid.children.length === 0) developedGrid.innerHTML = '<p style="text-align:center; grid-column: 1/-1; color: #555;">No developed photos.</p>';
}

function updateCountdowns() {
    // Only fetch elements if gallery is potentially visible
    const developingCards = document.querySelectorAll('.polaroid-card.developing');
    const now = Date.now();
    let needsReload = false;

    developingCards.forEach(card => {
        const ts = parseInt(card.dataset.timestamp);
        const timeDiff = now - ts;
        const remainingMs = DEVELOPMENT_TIME_MS - timeDiff;

        if (remainingMs <= 0) {
            needsReload = true; // Timer finished!
        } else {
            const hours = Math.floor(remainingMs / (1000 * 60 * 60));
            const minutes = Math.floor((remainingMs % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((remainingMs % (1000 * 60)) / 1000);

            // Optional: Show seconds if < 1h
            const timerText = hours > 0
                ? `${hours}h ${minutes}m`
                : `${minutes}m ${seconds}s`;

            const timerOverlay = card.querySelector('.timer-overlay');
            if (timerOverlay) timerOverlay.textContent = timerText;
        }
    });

    if (needsReload) {
        loadGallery();
    }
}

// Start
window.addEventListener('load', init);
