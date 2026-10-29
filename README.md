<div align="center">

# 🦂 Scorpion Cursor
### Luxury Edition

*A procedurally animated scorpion that hunts your mouse cursor.*

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.x-2E8B57?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-555?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-C8AA78?style=for-the-badge)

<!-- Add a screenshot or GIF here, then uncomment: -->
<!-- ![Preview](preview.gif) -->

</div>

---

## 📖 Table of Contents

- [About](#-about)
- [Features](#-features)
- [Getting Started](#-getting-started)
- [Controls](#-controls)
- [How It Works](#-how-it-works)
- [Customization](#-customization)
- [Project Structure](#-project-structure)
- [License](#-license)

---

## ✨ About

Scorpion Cursor is a small Pygame project with no image assets at all: everything you see is drawn in code, frame by frame. A 90-joint body follows the mouse like a snake, legs step realistically, claws glow while it moves, and a curled stinger sways in the back, all in a dark-gold "luxury" color theme.

## 🎯 Features

| | Feature |
|---|---|
| 🐍 | **Snake-like body**: 90 joints, each following the previous one at a fixed distance |
| 🦵 | **Stepping legs**: 4 pairs, feet stay planted and only step when the body drifts away |
| 🔥 | **Glowing claws**: the glow fades in while moving and fades out when idle |
| 🪝 | **Curled stinger**: animated with a sine wave so it gently "breathes" |
| ✨ | **Particle trail**: particles with gravity, shrinking and fading over time |
| 🎨 | **Metallic look**: every part is layered as shadow, main color, then highlight |
| 📊 | **Live FPS counter** and a subtle background grid |

## 🚀 Getting Started

**1. Clone the repository**

```bash
git clone https://github.com/<your-username>/scorpion-cursor.git
cd scorpion-cursor
```

**2. Install the dependency**

```bash
pip install pygame
```

**3. Run it**

```bash
python scorpion_cursor.py
```

> **Requirements:** Python 3.8 or newer and [Pygame](https://www.pygame.org/).

## 🎮 Controls

| Input | Action |
|:------|:-------|
| 🖱️ Move the mouse | The scorpion chases the cursor |
| `ESC` | Quit |
| ❌ Window close button | Quit |

## 🧠 How It Works

<details>
<summary><b>Body chain</b></summary>

The head moves toward the mouse with easing (slower when close, capped at a max speed, and a dead zone to avoid jitter). Every other joint is then pulled to stay exactly `D` pixels from the joint before it, which creates the smooth snake-like motion.
</details>

<details>
<summary><b>Local frames (tangent and normal)</b></summary>

For every joint, a tangent (the body direction) and a normal (rotated 90° sideways) are computed once per frame. Legs, ribs and claws all use them to know "forward" and "sideways".
</details>

<details>
<summary><b>Legs</b></summary>

Each foot has an ideal target position beside the body. The foot stays planted until it is more than 42 px away from that target, then glides to it. The knee sits halfway between hip and foot and is pushed outward to bend the leg.
</details>

<details>
<summary><b>Tail and stinger</b></summary>

The tail starts at the last joint and walks outward in small steps, rotating its direction by a growing angle each step, which produces a curl. The stinger is a thin triangle built from the tail direction and its perpendicular vector.
</details>

<details>
<summary><b>Particles</b></summary>

Each particle stores its remaining lifetime. The ratio `life / max_life` controls both its size and brightness, and a small gravity value pulls it downward every frame.
</details>

## 🛠️ Customization

Edit the constants at the top of `scorpion_cursor.py`:

| Setting | Effect |
|:--------|:-------|
| `W`, `H` | Window size |
| `N`, `D` | Number of body joints and the spacing between them (body length) |
| `FPS` | Frame-rate cap |
| `HEAD_SPEED`, `SPEED_MULTIPLIER` | How fast the scorpion chases the mouse |
| `FOOT_SMOOTH` | How quickly feet snap to new positions |
| `COLORS` | The entire color theme |

## 📁 Project Structure

```
scorpion-cursor/
├── scorpion_cursor.py   # the whole project
├── README.md
└── LICENSE
```

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.

---

<div align="center">

Made with 🐍 and Pygame

⭐ If you like it, give the repo a star!

</div>
