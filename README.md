# PureChess 1.0

A high-performance, UCI-compatible chess engine written in **Python 3.10+**. PureChess utilizes a bitboard-based board representation and an advanced search algorithm with modern pruning techniques.

## Features
- **Modern Python:** Leverages Python 3.10+ features and optimized bitwise operations.
- **UCI Support:** Fully compatible with the Universal Chess Interface (UCI) for use in GUIs like Arena, Cute Chess, and Banksia.
- **Bitboard Engine:** Uses 64-bit integer bitboards with precomputed attack tables for high-speed move generation.

## Technical Architecture

### 1. Board Representation & Move Generation
- **Data Structures:** Uses 64-bit integers for occupancy and piece-specific bitboards.
- **Precomputed Tables:** Fast lookups for Knights, Kings, and Pawns. Sliding piece attacks (Bishops, Rooks, Queens) are handled via optimized dictionary-based attack tables.
- **Move Encoding:** Moves are packed into 32-bit integers for memory efficiency.
- **Legal Move Logic:** High-performance check and pin detection to ensure only legal moves are considered during search.

### 2. Evaluation Function (Tapered Eval)
PureChess uses a midgame/endgame tapered evaluation to provide smooth transitions across game phases:
- **Material & PST:** Piece-Square Tables (PST) and material values tailored for both midgame and endgame.
- **Pawn Heuristics:** Advanced logic for passed pawns (rank bonus, king distance), isolated/doubled/backward pawns, and pawn chains.
- **King Safety:** Evaluates king ring attacks, safe checks, pawn shelter, and open flank penalties.
- **Positional Bonuses:** Includes mobility, bishop pair, rook batteries, outposts, and space evaluation.
- **Specialized Endgames:** Dedicated handlers for KBNK and KNNKP (Troitzky) endgames.

### 3. Search Algorithm
A robust **Negamax with Alpha-Beta Pruning** framework including:
- **Transposition Table (TT):** ~4M entries (22-bit) using Zobrist hashing.
- **Selectivity:** Null-Move Pruning (NMP), Probcut, Razoring, and Reverse Futility Pruning.
- **Reductions & Pruning:** Late Move Reductions (LMR), Late Move Pruning (LMP), and SEE (Static Exchange Evaluation) pruning.
- **Extensions:** Singular extensions for high-depth search stability.
- **Move Ordering:** Optimized using TT moves, SEE-sorted captures, Killer moves, Counter moves, and History heuristics.

## Usage
PureChess is a command-line engine. To integrate it:
1. Load the compiled .exe into any UCI-compatible GUI.
2. The engine supports standard time control commands (`wtime`, `btime`, `movetime`, `depth`).

## License
This project is licensed under the **BSD 3-Clause "New" or "Revised" License**. See the `LICENSE` file for more details.

---
**Author:** NazComio.
**Version:** 1.0
