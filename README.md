# 🦂 Scorpion Cursor

A small, procedural animation built with **Python** and **Pygame**: a scorpion that chases your mouse cursor across the screen, with a tapered body, a curved tail, and four pairs of legs.

<!-- Add a screenshot or GIF here: -->
<!-- ![Demo](assets/demo.gif) -->

## ✨ Features

- **Chain-based body:** the scorpion is a chain of joints, each one following the joint ahead of it, which gives smooth, organic movement.
- **Procedural shape:** body and tail thickness are computed with math functions (sine curve for the body, power curve for the tail), not drawn from images.
- **Eight legs:** four pairs, each with its own reach.
- **Speed that adapts:** the scorpion speeds up when the cursor is far away and slows down as it gets close.
- **No assets needed:** everything is drawn in code.

## 🚀 Getting Started

### Requirements

- Python 3.8 or newer
- [Pygame](https://www.pygame.org/)

### Installation

```bash
git clone https://github.com/ka707neki/scorpion-cursor.git
cd scorpion-cursor
pip install -r requirements.txt
```

### Run

```bash
python scorpion.py
```

Move your mouse and watch the scorpion follow.

## ⚙️ Configuration

The main settings are at the top of `scorpion.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `W, H`   | `900, 650` | Window width and height |
| `N`      | `110` | Number of body segments |
| `D`      | `6` | Distance between segments |

Try changing `N` for a longer scorpion, or `D` for a tighter or looser body.

## 🧠 How It Works

1. The **head** moves toward the mouse, with speed proportional to the distance (capped at a maximum).
2. Each following **joint** is pulled toward the one in front of it, keeping a fixed distance `D`. This is a simple form of *follow-the-leader* kinematics.
3. `width(i)` returns the thickness at each joint: a sine curve for the body, then a power curve that tapers into the tail.
4. Each **leg** is attached to a joint and reaches out to the side, using the body's direction (`frame_at`) to find the forward and perpendicular axes.

## 🗂️ Project Structure

```
scorpion-cursor/
├── scorpion.py
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

## 🛣️ Ideas for Improvement

- [ ] Add a stinger animation when the cursor stops
- [ ] Add color themes
- [ ] Add multiple scorpions

## 📄 License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.

## 👤 Author

**ka707neki** · [GitHub](https://github.com/ka707neki)

If you like this project, a ⭐ is appreciated!
