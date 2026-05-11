# PureChess 1.1

A high-performance, UCI-compatible chess engine written in **Python 3.10+**. Version 1.1 introduces significant enhancements to search stability, evaluation accuracy, and sophisticated move ordering.

## What’s New in 1.1
- **Enhanced Move Ordering:** Added continuation history and capture history to prioritize the best candidates faster.
- **Tuned Search:** Refined LMR (Late Move Reduction) formulas and better time-out handling.
- **Improved Evaluation:** Upgraded king safety logic (flank attacks and pawn storms) and more accurate passed pawn scoring.
- **Bug Fixes:** Resolved endgame scaling issues and optimized Zobrist hashing for speed.

## Features
- **Modern Python:** Optimized for Python 3.10+ using bitwise operations (PyPy recommended for 2-3x speedup).
- **UCI Support:** Fully compatible with the Universal Chess Interface (UCI) for use in GUIs like Arena, Cute Chess, and Banksia.
- **Bitboard Engine:** Uses 64-bit integer bitboards with precomputed attack tables for high-speed move generation.

## Technical Architecture

### 1. Board Representation & Move Generation
- **Data Structures:** Uses 64-bit integers for occupancy and piece-specific bitboards.
- **Precomputed Tables:** Fast lookups for Knights, Kings, and Pawns.
- **Move Generation:** Optimized sliding piece attacks (Bishops, Rooks, Queens) using dictionary-based lookups.
- **Zobrist Hashing:** Fast position hashing for the Transposition Table.

### 2. Evaluation Function (Tapered Eval)
PureChess uses a midgame/endgame tapered evaluation to provide smooth transitions across game phases:
- **Material & PST:** Piece-Square Tables and material values tailored for both midgame and endgame.
- **Pawn Heuristics:** Advanced logic for passed pawns (rank bonus, king distance) and pawn structure (isolated, doubled, backward).
- **King Safety:** Evaluates king ring attacks, pawn shelter, and open flank penalties.
- **Positional Bonuses:** Includes mobility, bishop pair, outposts, and space evaluation.
- **Specialized Endgames:** Dedicated handlers for complex endings like KBNK and KNNKP.

### 3. Search Algorithm
A robust **Negamax with Alpha-Beta Pruning** framework including:
- **Transposition Table (TT):** Fixed size (~4M entries, ~128 MB) for efficient analysis.
- **Selectivity:** Null-Move Pruning (NMP), Probcut, Razoring, and Static Exchange Evaluation (SEE) pruning.
- **Reductions & Pruning:** Late Move Reductions (LMR) and Late Move Pruning (LMP).
- **Extensions:** Singular extensions for high-depth search stability.
- **Move Ordering:** Optimized using TT moves, SEE-sorted captures, Killer moves, Counter moves, and History heuristics.

## Usage

### GUI Integration
1. Load the `PureChess 1.1.exe` into any UCI-compatible GUI.
2. The engine respects standard time control commands (`wtime`, `btime`, `movetime`, `depth`).

## License
This project is licensed under the **BSD 3-Clause "New" or "Revised" License**. See the `LICENSE` file for more details.
---
**Author:** NazComio
**Version:** 1.1
