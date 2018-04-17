# -*- coding: UTF-8 -*-
# -*- write by yangle -*-
import json
import ctypes

RC_CRF = 1
RC_2_PASS = 2

# ======================baseMediaParams======================
class baseMediaParams:
    def __init__(self):
        self.stream_select = ''
        self.vencoder_params = ''
        self.vfilter_params = ''
        self.format_params = ''
        self.aencoder_params = ''

class baseMediaParamsArray:
    def __init__(self):
        self._n = 0
        self._capacity = 20
        self._A = self._make_array(self._capacity)  # low-level array

    def __len__(self):
        return self._n

    def __getitem__(self, k):
        if not 0 <= k < self._n:
            raise IndexError('invalid index')
        return self._A[k]

    def append(self, baseMediaParams):
        if self._n == self._capacity:
            self._resize(2 * self._capacity)

        self._A[self._n] = baseMediaParams
        self._n += 1

    def _resize(self, c):
        B = self._make_array(c)
        for k in range(self._n):
            B[k] = self._A[k]
            self._A = B
            self._capacity = c

    def _make_array(self, c):
        return (c * ctypes.py_object)()


# ======================baseVideoBitrate======================
class baseVideoBitrate:
    def __init__(self):
        self.rc_mode = RC_CRF
        self.ref_mode = -1
        self.start_delta = -1
        self.gap_delta = -1
        self.end_delta = -1

class baseVideoBitrateArray:
    def __init__(self):
        self._n = 0
        self._capacity = 20
        self._A = self._make_array(self._capacity)  # low-level array

    def __len__(self):
        return self._n

    def __getitem__(self, k):
        if not 0 <= k < self._n:
            raise IndexError('invalid index')
        return self._A[k]

    def append(self, baseVideoBitrate):
        if self._n == self._capacity:
            self._resize(2 * self._capacity)

        self._A[self._n] = baseVideoBitrate
        self._n += 1

    def _resize(self, c):
        B = self._make_array(c)
        for k in range(self._n):
            B[k] = self._A[k]
            self._A = B
            self._capacity = c

    def _make_array(self, c):
        return (c * ctypes.py_object)()