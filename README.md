# 🧠 AI-Based Connect Four Game

A Python implementation of the classic Connect Four game enhanced with an AI opponent. This project uses the **Minimax algorithm with alpha-beta pruning** to enable the AI to make strategic decisions, offering a challenging experience for players.

## 🎮 Game Overview

Connect Four is a two-player connection game where players take turns dropping colored discs into a vertical grid. The goal is to be the first to form a horizontal, vertical, or diagonal line of four discs.

In this AI-enhanced version:

- **Single Player Mode**: Play against an AI that uses the Minimax algorithm.
- **Graphical Interface**: Built with **Pygame** for an interactive visual experience.

## 🧠 AI Implementation

- **Minimax Algorithm**: Simulates future game states to choose optimal moves.
- **Alpha-Beta Pruning**: Optimizes the Minimax algorithm by skipping unnecessary branches in the decision tree to improve performance.

## 📁 Project Structure

AI-BASED---CONNECT-FOUR-GAME/
├── assests/ # Game assets like images and sounds
├── Project_Tutorial.mp4 # Tutorial video showing gameplay
├── projectmain.py # Main script to run the game
└── README.md # Project documentation


## 🛠️ Installation

To run the game locally:

1. **Clone the repository:**

```bash
git clone https://github.com/fakhurdin/AI-BASED---CONNECT-FOUR-GAME.git
cd AI-BASED---CONNECT-FOUR-GAME

    (Optional) Create a virtual environment:

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

    Install dependencies:

pip install pygame numpy

🚀 Usage

Run the game using:

python projectmain.py

How to Play

    Click on a column to drop your disc.

    The AI will automatically respond.

    First to align four discs horizontally, vertically, or diagonally wins.

📹 Tutorial

For a quick demo, watch the included video:

📁 Project_Tutorial.mp4

    Make sure your system supports .mp4 playback.

👥 Contributors

    Fakhur Ul Din

    Ayesha Siquqe

    Hasnain Memon

🤝 Contributing

Contributions are welcome! To contribute:

    Fork the repo

    Create your branch:

git checkout -b feature/YourFeature

    Make your changes and commit:

git commit -m "Add your feature"

    Push to your fork:

git push origin feature/YourFeature

    Submit a Pull Request on GitHub

📄 License

Licensed under the MIT License.
📬 Contact

    GitHub Issues: Submit a bug or suggestion

    Email: fakhurdin987@gmail.com

Enjoy the game and feel free to contribute!


Let me know if you’d also like a `requirements.txt` or a GitHub Actions workflow file!
