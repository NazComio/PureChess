# PureChess 2.0

A high-performance, UCI-compatible chess engine written in pure Python, featuring an integrated NNUE (Efficiently Updatable Neural Network) evaluator.

## Version 2.0 Performance
* **Elo Progression:**
    * PureChess 1.0: 1309 Elo
    * PureChess 1.1: 1351 Elo
    * **PureChess 2.0: 1310 Elo** (vs. Bullitchess 1.0 @ 1500 Elo)
* **Match Stats (2.0 vs Bullitchess 1.0):** 174-216 (Excluding time-outs)

## Technical Architecture
* **Board Representation:** Bitboard-based with `__slots__` for memory optimization.
* **Evaluation:** Hybrid Classical + NNUE (Efficiently Updatable Neural Network).
* **Search:** Negamax with iterative deepening, Aspiration Windows, PVS, and advanced pruning (Null-Move, Razoring, Probcut, LMR).
* **UCI Support:** Fully compatible with standard GUIs (Arena, Cute Chess, Lichess).

## Key Features
1. **NNUE Integration:** Uses efficient, dependency‑free NNUE inference with Python's built‑in array module and precomputed delta updates for incremental feature calculation.
2. **Advanced Move Ordering:** Continuation history, capture history, and SEE (Static Exchange Evaluation).
3. **Optimized Search:** Singular extensions for high-depth stability.
4. **Self-Contained:** Runs on any standard Python 3.10+ environment.

## License
GNU Affero General Public License v3.0.
"Note: Previous versions (1.0–1.1) were released under the BSD 3-Clause License. All versions from 1.2 onwards are licensed under the AGPLv3 to ensure the project remains open and accessible to the community. This is the official source."
