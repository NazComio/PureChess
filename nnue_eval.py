from __future__ import annotations
import array
import os
import struct
from constants import WHITE, BLACK
_MAGIC    = 0x4E4E5545
_HERE     = os.path.dirname(os.path.abspath(__file__))
_BIN_PATH = os.path.join(_HERE, "purechess.bin")
def _load_bin(path: str):
    with open(path, "rb") as f:
        raw = f.read()
    magic,   = struct.unpack_from("<I", raw, 0)
    if magic != _MAGIC:
        raise ValueError(f"Bad magic in {path}: {magic:#010x} (expected {_MAGIC:#010x})")
    n_input,  = struct.unpack_from("<I", raw, 4)
    n_hidden, = struct.unpack_from("<I", raw, 8)
    scale,    = struct.unpack_from("<f", raw, 12)
    if n_input != 768:
        raise ValueError(f"Expected n_input=768, got {n_input}")
    offset = 16
    n_iw = n_hidden * n_input
    iw_flat = array.array("f", struct.unpack_from(f"<{n_iw}f", raw, offset))
    offset += n_iw * 4
    ib = array.array("f", struct.unpack_from(f"<{n_hidden}f", raw, offset))
    offset += n_hidden * 4
    ow = array.array("f", struct.unpack_from(f"<{n_hidden}f", raw, offset))
    offset += n_hidden * 4
    ob, = struct.unpack_from("<f", raw, offset)
    return n_hidden, float(scale), iw_flat, ib, ow, float(ob)
_N_HIDDEN, _SCALE, _IW_FLAT, _IB_ARR, _OW_ARR, _OB = _load_bin(_BIN_PATH)
_IB: list = list(_IB_ARR)
_OW: tuple = tuple(_OW_ARR)
_OB: float = _OB
_SCALE: float = _SCALE
def _build_fw(iw_flat: array.array, n_hidden: int, n_input: int) -> list:
    fw = []
    for feat in range(n_input):
        col = tuple(iw_flat[neuron * n_input + feat] for neuron in range(n_hidden))
        fw.append(col)
    return fw
_FW: list = _build_fw(_IW_FLAT, _N_HIDDEN, 768)
def _features_from_board(board) -> list:
    feats = []
    pieces = board.pieces
    for color in (WHITE, BLACK):
        base = color * 384
        for pc in range(6):
            base_pc = base + pc * 64
            bb = pieces[color][pc]
            while bb:
                lsb = bb & -bb
                feats.append(base_pc + lsb.bit_length() - 1)
                bb &= bb - 1
    return feats
def _forward(feats: list) -> float:
    IW  = _IW_FLAT
    IB  = _IB_ARR
    OW  = _OW_ARR
    nh  = _N_HIDDEN
    n_i = 768
    h = array.array("f", IB)
    for feat in feats:
        base = feat
        for i in range(nh):
            h[i] += IW[base]
            base += n_i
    for i in range(nh):
        v = h[i]
        if v < 0.0:   h[i] = 0.0
        elif v > 1.0: h[i] = 1.0
    out = _OB
    for i in range(nh):
        out += OW[i] * h[i]
    return out
def evaluate(board) -> int:
    feats = _features_from_board(board)
    raw   = _forward(feats)
    cp    = int(raw * _SCALE)
    return cp if board.turn == WHITE else -cp
