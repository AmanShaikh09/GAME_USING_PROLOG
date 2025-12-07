const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const scoreEl = document.getElementById('score');
const statusEl = document.getElementById('status');

const startScreen = document.getElementById('startScreen');
const startBtn = document.getElementById('startBtn');

// Game Constants
const TILE_SIZE = 30; // Scale Prolog coordinates to Pixels
const FPS = 30;

let keys = {
    left: false,
    right: false,
    jump: false
};

// Input Handling
document.addEventListener('keydown', (e) => {
    if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' '].includes(e.key)) {
        e.preventDefault();
    }
    if (e.key === 'ArrowLeft' || e.key === 'a') keys.left = true;
    if (e.key === 'ArrowRight' || e.key === 'd') keys.right = true;
    if (e.key === 'ArrowUp' || e.key === 'w') keys.jump = true;
});

document.addEventListener('keyup', (e) => {
    if (e.key === 'ArrowLeft' || e.key === 'a') keys.left = false;
    if (e.key === 'ArrowRight' || e.key === 'd') keys.right = false;
    if (e.key === 'ArrowUp' || e.key === 'w') keys.jump = false;
});

startBtn.addEventListener('click', () => {
    startScreen.style.display = 'none';
    initGame();
});

async function initGame() {
    try {
        await fetch('/init');
        statusEl.textContent = "Running";
        gameLoop();
    } catch (e) {
        statusEl.textContent = "Error: Server not running";
        startScreen.style.display = 'block';
    }
}

async function gameLoop() {
    // Determine Action
    let action = "none";
    if (keys.jump) action = "jump";
    else if (keys.left) action = "left";
    else if (keys.right) action = "right";

    try {
        const response = await fetch('/tick', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: action })
        });
        const state = await response.json();
        render(state);

        if (state.state === 'running') {
            setTimeout(gameLoop, 1000 / FPS);
        } else {
            statusEl.textContent = state.state === 'won' ? "YOU WIN!" : "GAME OVER";
        }
    } catch (e) {
        console.error(e);
    }
}

function render(state) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw Map (Static for now, based on Prolog logic)
    ctx.fillStyle = '#654321'; // Ground Brown
    // Floor
    ctx.fillRect(0, canvas.height - TILE_SIZE, canvas.width, TILE_SIZE);
    // Platforms (Hardcoded visual match to Prolog data)
    drawBlock(10, 4, 5);
    drawBlock(20, 7, 5);

    // Draw Items
    state.items.forEach(item => {
        if (item.type === 'coin') {
            ctx.fillStyle = 'gold';
            ctx.beginPath();
            ctx.arc(toX(item.x), toY(item.y), 10, 0, Math.PI * 2);
            ctx.fill();
        } else if (item.type === 'star') {
            ctx.fillStyle = 'yellow';
            drawStar(toX(item.x), toY(item.y), 5, 10, 5);
        }
    });

    // Draw Enemies
    state.enemies.forEach(enemy => {
        ctx.fillStyle = 'red';
        ctx.fillRect(toX(enemy.x) - 15, toY(enemy.y) - 15, 30, 30);

        // Eyes
        ctx.fillStyle = 'white';
        ctx.fillRect(toX(enemy.x) - 10, toY(enemy.y) - 5, 8, 8);
        ctx.fillRect(toX(enemy.x) + 2, toY(enemy.y) - 5, 8, 8);
        ctx.fillStyle = 'black';
        ctx.fillRect(toX(enemy.x) - 8, toY(enemy.y) - 3, 4, 4);
        ctx.fillRect(toX(enemy.x) + 4, toY(enemy.y) - 3, 4, 4);
    });

    // Draw Mario
    ctx.fillStyle = 'red'; // Shirt
    const mx = toX(state.mario.x);
    const my = toY(state.mario.y);
    ctx.fillRect(mx - 10, my - 20, 20, 20);
    ctx.fillStyle = 'blue'; // Overalls
    ctx.fillRect(mx - 10, my, 20, 10);

    // Update UI
    const currentScore = parseInt(scoreEl.textContent);
    if (state.score > currentScore) {
        spawnParticles(mx, my, 'gold');
    }
    scoreEl.textContent = state.score;

    updateAndDrawParticles();
}

// Particles
let particles = [];
function spawnParticles(x, y, color) {
    for (let i = 0; i < 10; i++) {
        particles.push({
            x: x,
            y: y,
            vx: (Math.random() - 0.5) * 10,
            vy: (Math.random() - 0.5) * 10,
            life: 1.0,
            color: color
        });
    }
}

function updateAndDrawParticles() {
    for (let i = particles.length - 1; i >= 0; i--) {
        let p = particles[i];
        p.x += p.vx;
        p.y += p.vy;
        p.life -= 0.05;

        if (p.life <= 0) {
            particles.splice(i, 1);
        } else {
            ctx.globalAlpha = p.life;
            ctx.fillStyle = p.color;
            ctx.fillRect(p.x, p.y, 5, 5);
            ctx.globalAlpha = 1.0;
        }
    }
}

// Coordinate Conversion (Prolog Grid -> Canvas Pixels)
// Prolog: Y=1 is bottom, X=1 is left.
function toX(x) {
    return x * TILE_SIZE;
}
function toY(y) {
    return canvas.height - (y * TILE_SIZE);
}

function drawBlock(x, y, width) {
    ctx.fillStyle = '#8B4513';
    ctx.fillRect(toX(x), toY(y), width * TILE_SIZE, TILE_SIZE);
}

function drawStar(cx, cy, spikes, outerRadius, innerRadius) {
    let rot = Math.PI / 2 * 3;
    let x = cx;
    let y = cy;
    let step = Math.PI / spikes;

    ctx.beginPath();
    ctx.moveTo(cx, cy - outerRadius);
    for (let i = 0; i < spikes; i++) {
        x = cx + Math.cos(rot) * outerRadius;
        y = cy + Math.sin(rot) * outerRadius;
        ctx.lineTo(x, y);
        rot += step;

        x = cx + Math.cos(rot) * innerRadius;
        y = cy + Math.sin(rot) * innerRadius;
        ctx.lineTo(x, y);
        rot += step;
    }
    ctx.lineTo(cx, cy - outerRadius);
    ctx.closePath();
    ctx.fill();
}

// Start
initGame();
