# Game Development Report: Infinite Robot Runner

## 1. Project Overview
**Infinite Robot Runner** is a 2D side-scrolling platformer game developed in Python using the `pygame` library. The player controls a robot character who must jump over gaps, avoid patrolling enemies, and collect coins in an infinitely generating world.

## 2. Key Features
-   **Infinite Procedural Generation**: The level generates endlessly as the player moves right. New platforms, enemies, and coins are created dynamically in "chunks".
-   **Physics Engine**: Custom physics logic for gravity, jumping, and collision detection ensures smooth player movement.
-   **Dynamic Camera**: The game world scrolls relative to the player, creating a seamless runner experience.
-   **Score System**: Players earn points by collecting coins (+100) and surviving.
-   **Game Over & Restart**: A dedicated Game Over screen allows players to instantly restart the session by pressing 'R'.
-   **Visual Effects**:
    -   Custom drawn Robot Sprite (using Pygame primitives).
    -   Particle effects (gold explosions) when collecting coins.
    -   Parallax-style scrolling effect.

## 3. Technical Architecture
The game is built using Object-Oriented Programming (OOP) principles in a single `game.py` file.

### Core Classes
1.  **`Player`**: Manages the robot's state, including position, velocity (`change_x`, `change_y`), and interaction with the level. Implements gravity and jump mechanics.
2.  **`Level`**: Handles the procedural generation logic. It maintains groups of sprites (`platform_list`, `enemy_list`, `coin_list`) and manages the "world shift" to simulate camera movement.
3.  **`Enemy`**: A basic AI agent that patrols a set distance back and forth on platforms.
4.  **`Platform` / `Coin` / `Particle`**: Static and dynamic game objects inheriting from `pygame.sprite.Sprite`.

### Algorithms
-   **Chunk Generation**: As the player approaches the edge of the current map, the `Level` class generates a new segment of platforms with randomized width, height, and enemy placement.
-   **Cleanup**: Objects that scroll off the left side of the screen are automatically removed (`kill()`) to prevent memory leaks and maintain performance.

## 4. How to Run
### Prerequisites
-   Python 3.x
-   Pygame library (`pip install pygame`)

### Execution
Run the following command in the terminal:
```bash
python game.py
```

### Controls
-   **Arrow Keys / WASD**: Move Left/Right, Jump (Up).
-   **R**: Restart Game (on Game Over screen).

## 5. Development History
-   **Phase 1**: Initial prototype using Prolog for logic and ASCII rendering.
-   **Phase 2**: Web-based version using Prolog as a backend server and HTML5 Canvas for rendering.
-   **Phase 3 (Final)**: Ported to Python/Pygame for native performance, infinite scrolling, and robust desktop gameplay.
