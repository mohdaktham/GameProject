# GameProject

A simple **Ping Pong** game built with **Python** and **Pygame**.

## Overview

- **Easy Ping Pong** – single-player vs AI: paddle, ball, score, menu, pause, and game over.
- Implemented in `PINGgame/` (Python + Pygame).

## Requirements

- Python 3.x
- Pygame

```bash
pip install pygame
```

## Project Layout

```
GameProject/
├── PINGgame/
│   ├── Script.py         # Main game logic (Easy Ping Pong)
│   └── Collection game.py
├── .gitignore
└── README.md
```

## How to Run

From the project root:

```bash
python PINGgame/Script.py
```

Or from inside `PINGgame/`:

```bash
cd PINGgame
python Script.py
```

## Gameplay

- **Menu** – start game or quit
- **Playing** – move paddle (e.g. W/S or arrow keys), play against AI
- **Pause** – pause/resume
- **Game over** – score display and return to menu

---

*Unity project* in the repo name refers to a separate or planned Unity version; the current playable game is the Pygame version in `PINGgame/`.
