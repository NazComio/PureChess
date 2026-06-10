# PureChess 2.1

A high‑performance, UCI‑compatible chess engine written in Python, featuring a JIT‑accelerated NNUE evaluator and an advanced search with modern pruning techniques.

## Version 2.1 Performance
* **Elo Progression:**
    * PureChess 1.0: 1309 Elo
    * PureChess 1.1: 1351 Elo
    * PureChess 2.0: 1310 Elo
    * **PureChess 2.1:** ~1506 Elo (237 wins - 223 losses - 40 draws vs. Bullitchess 1.0 @ 1500 Elo)

## Technical Architecture
* **Board Representation:** Bitboard‑based with `__slots__` for minimal memory overhead.
* **Evaluation:** Hybrid classical + NNUE (Efficiently Updatable Neural Network) with **Numba JIT** acceleration.
* **Search:** Negamax with iterative deepening, aspiration windows, principal variation search (PVS), plus:
    * Null‑move pruning (NMP)
    * Razoring
    * Probcut
    * Futility pruning
    * Late move reduction (LMR)
    * Quiescence search (with delta pruning)
    * Singular extensions
* **UCI Support:** Full UCI 2.0 protocol (Arena, Cute Chess, Lichess compatible).

## Key Improvements in 2.1
1. **NNUE Acceleration:** Leverages Numba’s `@njit` for near‑native inference speed, while retaining pure‑Python portability.
2. **Transposition Table (TT):** Configurable hash table (default 256 MB) with exact/lower/upper bounds and move storage.
3. **Advanced Move Ordering:** Continuation history, capture history, killer moves, counter‑moves, and static exchange evaluation (SEE).
4. **Improved Time Management:** Adaptive thinking time based on game phase, increment, and remaining clock.
5. **Opening Book:** Built‑in UCI‑configurable book with dozens of common lines.
6. **Draw Detection:** Threefold repetition, 50‑move rule, and insufficient material (KvK, KBNvK, KNvKP).

## Requirements
- Python 3.10 or newer
- `numba` and `numpy` (see `requirements.txt`)

## License
GNU Affero General Public License v3.0.
"Note: Previous versions (1.0–1.1) were released under the BSD 3-Clause License. All versions from 1.2 onwards are licensed under the AGPLv3 to ensure the project remains open and accessible to the community. This is the official source."
