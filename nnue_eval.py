from __future__ import annotations
import array
import os
import struct
import numpy as np
from numba import njit
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
    iw_flat_raw = struct.unpack_from(f"<{n_iw}f", raw, offset)
    offset += n_iw * 4
    ib_raw = struct.unpack_from(f"<{n_hidden}f", raw, offset)
    offset += n_hidden * 4
    ow_raw = struct.unpack_from(f"<{n_hidden}f", raw, offset)
    offset += n_hidden * 4
    ob, = struct.unpack_from("<f", raw, offset)
    return n_hidden, float(scale), iw_flat_raw, ib_raw, ow_raw, float(ob)
_N_HIDDEN, _SCALE, _IW_FLAT_RAW, _IB_RAW, _OW_RAW, _OB = _load_bin(_BIN_PATH)
_IW_NP = np.array(_IW_FLAT_RAW, dtype=np.float32).reshape(_N_HIDDEN, 768).T
_IB_NP = np.array(_IB_RAW, dtype=np.float32)
_OW_NP = np.array(_OW_RAW, dtype=np.float32)
_OB    = float(_OB)
_SCALE = float(_SCALE)
_OW_SC_NP = (_OW_NP * _SCALE).astype(np.float32)
_OB_SC    = float(_OB * _SCALE)
_FW_NP    = np.ascontiguousarray(_IW_NP)
@njit(fastmath=True)
def _nb_nnue_out(acc, ow_sc, ob_sc):
    s = ob_sc
    for i in range(len(acc)):
        v = acc[i]
        if v > 0.0:
            if v > 1.0:
                v = 1.0
            s += v * ow_sc[i]
    return int(s)
@njit(fastmath=True)
def _nb_full_score(ib, fw, feats_arr):
    n = len(ib)
    acc = ib.copy()
    for k in range(len(feats_arr)):
        f = feats_arr[k]
        row = fw[f]
        for i in range(n):
            acc[i] += row[i]
    return acc
@njit(fastmath=True)
def _nb_delta_2(acc, fw, add1, sub1):
    n = len(acc)
    out = np.empty(n, np.float32)
    a1 = fw[add1]; s1 = fw[sub1]
    for i in range(n):
        out[i] = acc[i] + a1[i] - s1[i]
    return out
@njit(fastmath=True)
def _nb_delta_3_sub(acc, fw, add1, sub1, sub2):
    n = len(acc)
    out = np.empty(n, np.float32)
    a1 = fw[add1]; s1 = fw[sub1]; s2 = fw[sub2]
    for i in range(n):
        out[i] = acc[i] + a1[i] - s1[i] - s2[i]
    return out
@njit(fastmath=True)
def _nb_delta_4(acc, fw, add1, add2, sub1, sub2):
    n = len(acc)
    out = np.empty(n, np.float32)
    a1 = fw[add1]; a2 = fw[add2]; s1 = fw[sub1]; s2 = fw[sub2]
    for i in range(n):
        out[i] = acc[i] + a1[i] + a2[i] - s1[i] - s2[i]
    return out
@njit(fastmath=True)
def _nb_delta_3_add(acc, fw, add1, add2, sub1):
    n = len(acc)
    out = np.empty(n, np.float32)
    a1 = fw[add1]; a2 = fw[add2]; s1 = fw[sub1]
    for i in range(n):
        out[i] = acc[i] + a1[i] + a2[i] - s1[i]
    return out
def _warmup_numba():
    _dummy_acc = _IB_NP.copy()
    _dummy_feats = np.array([0, 1], dtype=np.int64)
    _nb_nnue_out(_dummy_acc, _OW_SC_NP, _OB_SC)
    _nb_full_score(_IB_NP, _FW_NP, _dummy_feats)
    _nb_delta_2(_dummy_acc, _FW_NP, 0, 1)
    _nb_delta_3_sub(_dummy_acc, _FW_NP, 0, 1, 2)
    _nb_delta_4(_dummy_acc, _FW_NP, 0, 1, 2, 3)
    _nb_delta_3_add(_dummy_acc, _FW_NP, 0, 1, 2)
_warmup_numba()
_IB: list       = list(_IB_RAW)
_OW: tuple      = tuple(_OW_RAW)
_FW: list       = [tuple(_FW_NP[feat].tolist()) for feat in range(768)]
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
def _full_score_np(board) -> np.ndarray:
    feats = _features_from_board(board)
    if feats:
        fa = np.array(feats, dtype=np.int64)
        return _nb_full_score(_IB_NP, _FW_NP, fa)
    return _IB_NP.copy()
_full_score_fn  = _full_score_np
_nnue_out_fn    = _nb_nnue_out
def evaluate(board) -> int:
    acc = _full_score_np(board)
    cp  = _nb_nnue_out(acc, _OW_SC_NP, _OB_SC)
    return cp if board.turn == WHITE else -cp
