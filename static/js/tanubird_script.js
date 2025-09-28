const canvas = document.getElementById('game-canvas');
const ctx = canvas.getContext('2d');
const overlay = document.getElementById('overlay');
const title = document.getElementById('title');
const instructions = document.getElementById('instructions');

const IMAGE_URLS = ASSET_URLS;

const images = {};
let assetsLoaded = 0;
const totalAssets = Object.keys(IMAGE_URLS).length;

Object.keys(IMAGE_URLS).forEach(key => {
    images[key] = new Image();
    images[key].src = IMAGE_URLS[key];
    images[key].onload = () => {
        assetsLoaded++;
        if (assetsLoaded === totalAssets) {
            allAssetsLoaded();
        }
    };
    images[key].onerror = () => {
        console.error(`Failed to load image: ${key} at path ${IMAGE_URLS[key]}`);
        instructions.innerText = `Error loading: ${key}`;
    };
});

const flapSound = document.getElementById('flap-sound');
const scoreSound = document.getElementById('score-sound');
const hitSound = document.getElementById('hit-sound');

function playSound(sound) {
    sound.currentTime = 0;
    sound.playbackRate = 1;
    sound.play().catch(e => console.warn("Audio play failed:", e));
}

let bird, pipes, score, gravity, lift, gameSpeed, isGameOver, frameCount, floorOffset;
const floorHeightRatio = 0.15;

function setupGame() {
    setCanvasSize();
    initializeVars();
}

function showStartScreen() {
    title.innerText = 'Tanu Bird';
    instructions.innerHTML = "Click or Press Space to Start";
    setupGame();
    isGameOver = true; 
    draw();
}

function allAssetsLoaded() {
    instructions.innerHTML = "Click or Press Space to Start";
    setupGame(); 
    isGameOver = true;
    draw();
    setupEventListeners();
}

function setCanvasSize() {
    const container = document.getElementById('game-container');
    canvas.width = container.clientWidth;
    canvas.height = container.clientHeight;
}

function initializeVars() {
    const birdHeight = (canvas.width / 15) * 0.9;
    const birdAspectRatio = images.bird.width / images.bird.height;
    bird = {
        x: canvas.width / 4,
        y: canvas.height / 2,
        width: birdHeight * birdAspectRatio,
        height: birdHeight,
        velocity: 0,
        rotation: 0,
    };
    pipes = [];
    score = 0;
    gravity = canvas.height * 0.0004;
    gameSpeed = canvas.width * 0.005;
    const jumpPower = (canvas.height + canvas.width) / 2 * 0.015;
    const maxJump = 12; 
    lift = -Math.min(jumpPower, maxJump);
    isGameOver = false;
    frameCount = 0;
    floorOffset = 0;
    pipes.push(createPipe());
}

function createPipe() {
    const pipeWidth = canvas.width / 7;
    const gapHeight = canvas.height / 4.0; 
    const minHeight = canvas.height / 10;
    const topPipeHeight = Math.random() * (canvas.height - gapHeight - (minHeight * 2) - (canvas.height * floorHeightRatio)) + minHeight;
    return { x: canvas.width, width: pipeWidth, topHeight: topPipeHeight, bottomY: topPipeHeight + gapHeight, passed: false };
}

function flap() {
    if (!isGameOver) {
        bird.velocity = lift;
        playSound(flapSound);
    }
}

function resetGame() {
    setupGame();
    overlay.classList.add('hidden');
    gameLoop();
}

function update() {
    if (isGameOver) return;
    frameCount++;
    bird.velocity += gravity;
    bird.y += bird.velocity;
    bird.rotation = Math.min(Math.PI / 4, bird.velocity * 0.05);
    floorOffset -= gameSpeed;
    if (floorOffset <= -images.floor.width) { floorOffset = 0; }
    pipes.forEach(pipe => pipe.x -= gameSpeed);
    if (pipes.length > 0 && pipes[pipes.length - 1].x < canvas.width / 1.8) { pipes.push(createPipe()); }
    pipes = pipes.filter(pipe => pipe.x + pipe.width > 0);
    const currentPipe = pipes.find(p => !p.passed && p.x + p.width < bird.x);
    if (currentPipe) {
        currentPipe.passed = true;
        score++;
        playSound(scoreSound);
    }
    const floorCollisionY = canvas.height * (1 - floorHeightRatio);
    if (bird.y + bird.height / 2 > floorCollisionY || bird.y - bird.height / 2 < 0) {
        endGame();
        return;
    }
    for (let pipe of pipes) {
        if (bird.x + bird.width / 2 > pipe.x && bird.x - bird.width / 2 < pipe.x + pipe.width) {
            if (bird.y - bird.height / 2 < pipe.topHeight || bird.y + bird.height / 2 > pipe.bottomY) {
                endGame();
                return;
            }
        }
    }
}

// <<<<<<<< DRAW FUNCTION WITHOUT INVERT >>>>>>>>
function draw() {
    const floorY = canvas.height * (1 - floorHeightRatio);
    
    // Background
    ctx.drawImage(images.background, 0, 0, canvas.width, floorY);

    // Pipes (no invert logic)
    pipes.forEach(pipe => {
        // Top pipe
        ctx.drawImage(images.pipeTop, pipe.x, 0, pipe.width, pipe.topHeight);

        // Bottom pipe
        const bottomPipeHeight = floorY - pipe.bottomY;
        ctx.drawImage(images.pipeBottom, pipe.x, pipe.bottomY, pipe.width, bottomPipeHeight);
    });

    // Floor
    const floorPattern = ctx.createPattern(images.floor, 'repeat-x');
    ctx.fillStyle = floorPattern;
    ctx.save();
    ctx.translate(floorOffset, 0);
    ctx.fillRect(-floorOffset, floorY, canvas.width - floorOffset + images.floor.width, canvas.height * floorHeightRatio);
    ctx.restore();

    // Bird
    ctx.save();
    ctx.translate(bird.x, bird.y);
    ctx.rotate(bird.rotation);
    ctx.drawImage(images.bird, -bird.width / 2, -bird.height / 2, bird.width, bird.height);
    ctx.restore();

    // Score
    ctx.fillStyle = 'white';
    ctx.strokeStyle = 'black';
    ctx.lineWidth = 2;
    ctx.font = `${canvas.width / 8}px 'Press Start 2P'`;
    ctx.textAlign = 'center';
    ctx.fillText(score, canvas.width / 2, canvas.height / 8);
    ctx.strokeText(score, canvas.width / 2, canvas.height / 8);
}

function endGame() {
    if (isGameOver) return;
    isGameOver = true;
    playSound(hitSound);
    title.innerText = 'Game Over';
    instructions.innerHTML = `Score: ${score}<br>Click to Restart`;
    overlay.classList.remove('hidden');
}

function gameLoop() {
    update();
    draw();
    if (!isGameOver) {
        requestAnimationFrame(gameLoop);
    }
}

function setupEventListeners() {
    const handleUserInput = (event) => {
        if (isGameOver) {
            if (title.innerText.includes('Game Over')) {
                showStartScreen();
            } else {
                resetGame();
            }
        } else {
            flap();
        }
    };
    const handleTouchEvent = (event) => {
        event.preventDefault();
        handleUserInput(event);
    };
    overlay.addEventListener('click', handleUserInput);
    canvas.addEventListener('mousedown', handleUserInput);
    canvas.addEventListener('touchstart', handleTouchEvent);
    document.addEventListener('keydown', (e) => {
        if (e.code === 'Space') {
            handleUserInput(e);
        }
    });
    window.addEventListener('resize', () => {
        setupGame();
        if(!isGameOver) {
            endGame();
            title.innerText = 'Resized!';
            instructions.innerHTML = `Score: ${score}<br>Click to Restart`;
        } else {
            showStartScreen();
        }
    });
}
