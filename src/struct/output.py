# -*- coding: UTF-8 -*-
# -*- write by yangle -*-
import json
import ctypes


class BaseOutput:
    def __init__(self):
        self.transcode_time = -1
        self.score = -1
        self.output_bitrate = -1


class BaseOutputArray:
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

    def append(self, BaseInput):
        if self._n == self._capacity:
            self._resize(2 * self._capacity)

        self._A[self._n] = BaseInput
        self._n += 1

    def _resize(self, c):
        B = self._make_array(c)
        for k in range(self._n):
            B[k] = self._A[k]
            self._A = B
            self._capacity = c

    def _make_array(self, c):
        return (c * ctypes.py_object)()

    def convert2json(self):
        json = {}
        for i in range(0, self._n):
            # one file deel
            output = self.__getitem__(i)
            json[i] = output.__dict__

        return json

