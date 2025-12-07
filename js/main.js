import { breeds, facts } from './breeds.js';
import { quizQuestions, results } from './quiz.js';

// --- State Management ---
const state = {
    dailyCat: null,
    pet: {
        hunger: 80,
        happiness: 60,
        lastInteracted: Date.now()
    },
    quizAnswers: []
};

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    loadState();
    initDailyCat();
    initBreeds();
    initFacts();
    initPet();
    initQuiz();
    initGallery();
    setupNavigation();
});

// --- Local Storage ---
function loadState() {
    const savedPet = localStorage.getItem('neonpurr_pet');
    if (savedPet) {
        state.pet = JSON.parse(savedPet);
        // Decay stats based on time passed
        const now = Date.now();
        const hoursPassed = (now - state.pet.lastInteracted) / (1000 * 60 * 60);
        state.pet.hunger = Math.max(0, state.pet.hunger - (hoursPassed * 5));
        state.pet.happiness = Math.max(0, state.pet.happiness - (hoursPassed * 5));
    }
}

function saveState() {
    state.pet.lastInteracted = Date.now();
    localStorage.setItem('neonpurr_pet', JSON.stringify(state.pet));
}

// --- Cat of the Day ---
async function initDailyCat() {
    const imgEl = document.querySelector('#daily-cat-img');
    const nameEl = document.querySelector('#daily-cat-name');
    const factEl = document.querySelector('#daily-cat-fact');

    // Simple random selection from local breeds for reliability
    const randomBreed = breeds[Math.floor(Math.random() * breeds.length)];
    const randomFact = facts[Math.floor(Math.random() * facts.length)];

    // Simulate loading
    setTimeout(() => {
        imgEl.innerHTML = `<img src="${randomBreed.image}" alt="${randomBreed.name}">`;
        nameEl.textContent = randomBreed.name;
        factEl.textContent = randomFact;
    }, 1000);
}

// --- Breed Explorer ---
function initBreeds() {
    const grid = document.getElementById('breed-grid');
    const buttons = document.querySelectorAll('.filter-btn');

    function renderBreeds(filter = 'all') {
        grid.innerHTML = '';
        const filtered = filter === 'all' 
            ? breeds 
            : breeds.filter(b => b.tags.includes(filter));

        filtered.forEach(breed => {
            const card = document.createElement('div');
            card.className = 'breed-card';
            card.innerHTML = `
                <img src="${breed.image}" class="breed-img" alt="${breed.name}">
                <h3>${breed.name}</h3>
                <p>${breed.temperament}</p>
            `;
            grid.appendChild(card);
        });
    }

    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            buttons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderBreeds(btn.dataset.filter);
        });
    });

    renderBreeds();
}

// --- Fun Facts ---
function initFacts() {
    const btn = document.getElementById('new-fact-btn');
    const text = document.querySelector('.fact-text');

    btn.addEventListener('click', () => {
        const randomFact = facts[Math.floor(Math.random() * facts.length)];
        text.style.opacity = 0;
        setTimeout(() => {
            text.textContent = randomFact;
            text.style.opacity = 1;
        }, 300);
    });
}

// --- Virtual Pet ---
function initPet() {
    const hungerBar = document.getElementById('hunger-bar');
    const happinessBar = document.getElementById('happiness-bar');
    const avatar = document.getElementById('pet-avatar');
    const controls = document.querySelectorAll('.control-btn');

    function updateStats() {
        hungerBar.style.width = `${state.pet.hunger}%`;
        happinessBar.style.width = `${state.pet.happiness}%`;
        
        // Change color based on status
        hungerBar.style.backgroundColor = state.pet.hunger < 30 ? '#ff0054' : '#00b4d8';
        
        saveState();
    }

    controls.forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.dataset.action;
            handlePetAction(action);
            avatar.classList.add('bounce');
            setTimeout(() => avatar.classList.remove('bounce'), 500);
        });
    });

    function handlePetAction(action) {
        if (action === 'feed') {
            state.pet.hunger = Math.min(100, state.pet.hunger + 20);
            playSound('purr');
        } else if (action === 'play') {
            state.pet.happiness = Math.min(100, state.pet.happiness + 15);
            state.pet.hunger = Math.max(0, state.pet.hunger - 5);
            playSound('meow');
        } else if (action === 'pet') {
            state.pet.happiness = Math.min(100, state.pet.happiness + 5);
            playSound('purr');
        }
        updateStats();
    }

    // Loop to decrease stats over time while page is open
    setInterval(() => {
        state.pet.hunger = Math.max(0, state.pet.hunger - 1);
        state.pet.happiness = Math.max(0, state.pet.happiness - 1);
        updateStats();
    }, 10000); // Every 10 seconds

    updateStats();
}

// --- Sound Synth (No assets needed) ---
function playSound(type) {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    const ctx = new AudioContext();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.connect(gain);
    gain.connect(ctx.destination);

    if (type === 'meow') {
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(800, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(400, ctx.currentTime + 0.3);
        gain.gain.setValueAtTime(0.1, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.3);
        osc.start();
        osc.stop(ctx.currentTime + 0.3);
    } else if (type === 'purr') {
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(50, ctx.currentTime);
        // Tremolo for purr
        const lfo = ctx.createOscillator();
        lfo.type = 'sine';
        lfo.frequency.value = 25;
        const lfoGain = ctx.createGain();
        lfoGain.gain.value = 500;
        lfo.connect(lfoGain);
        lfoGain.connect(gain.gain);
        
        gain.gain.setValueAtTime(0.05, ctx.currentTime);
        osc.start();
        lfo.start();
        osc.stop(ctx.currentTime + 1);
        lfo.stop(ctx.currentTime + 1);
    }
}

// --- Quiz ---
function initQuiz() {
    window.startQuiz = () => {
        let currentQuestion = 0;
        state.quizAnswers = [];
        const container = document.getElementById('quiz-container');

        function showQuestion(idx) {
            if (idx >= quizQuestions.length) {
                showResults();
                return;
            }

            const q = quizQuestions[idx];
            container.innerHTML = `
                <div class="quiz-question">${q.question}</div>
                <div class="quiz-options">
                    ${q.options.map((opt, i) => `
                        <button class="quiz-btn" data-type="${opt.type}">${opt.text}</button>
                    `).join('')}
                </div>
            `;

            container.querySelectorAll('.quiz-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    state.quizAnswers.push(e.target.dataset.type);
                    showQuestion(idx + 1);
                });
            });
        }

        function showResults() {
            // Count frequencies
            const counts = {};
            state.quizAnswers.forEach(type => {
                counts[type] = (counts[type] || 0) + 1;
            });
            
            // Find max
            const resultType = Object.keys(counts).reduce((a, b) => counts[a] > counts[b] ? a : b);
            const result = results[resultType];

            container.innerHTML = `
                <div class="quiz-result">
                    <img src="${result.image}" alt="${result.title}" style="width: 200px; border-radius: 50%; margin-bottom: 1rem;">
                    <h3>${result.title}</h3>
                    <p>${result.desc}</p>
                    <button class="quiz-btn" onclick="startQuiz()">Retake Quiz</button>
                </div>
            `;
            
            // Save result
            localStorage.setItem('neonpurr_quiz_result', resultType);
        }

        showQuestion(0);
    };
}

// --- Gallery Placeholders ---
function initGallery() {
    const gallery = document.getElementById('gallery-grid');
    gallery.innerHTML = '';
    
    // Just reuse some breed images for now
    const images = breeds.map(b => b.image).slice(0, 4);
    
    images.forEach(src => {
        const item = document.createElement('div');
        item.className = 'gallery-item';
        item.innerHTML = `<img src="${src}" style="width:100%; height:100%; object-fit:cover;" loading="lazy">`;
        gallery.appendChild(item);
    });
}

// --- Navigation ---
function setupNavigation() {
    const toggle = document.querySelector('.menu-toggle');
    const nav = document.querySelector('.nav-links');
    
    toggle.addEventListener('click', () => {
        nav.style.display = nav.style.display === 'flex' ? 'none' : 'flex';
        // Simple toggle for mobile - in real app would use class
        if (window.innerWidth <= 768) {
            if (nav.style.display === 'flex') {
                nav.style.flexDirection = 'column';
                nav.style.position = 'absolute';
                nav.style.top = '70px';
                nav.style.left = '0';
                nav.style.width = '100%';
                nav.style.background = 'rgba(16, 0, 43, 0.95)';
                nav.style.padding = '2rem';
            }
        }
    });
}
