"""This file contains Yolov5's IModel implementation in ONNX.
This model (onnx-backend) performs inference using ONNXRUNTIME,
on a given input numpy array, and returns result after performing
nms and other backend specific postprocessings.

Model expects normalized inputs (data-format=channels-first) with
batch axis. Model does not apply letterboxing to given inputs.
"""
import os
from typing import List

import importlib
import numpy as np
import onnxruntime

from ....interface.model import IModel
from ....utils.general import get_path
from ....detector.yolov5.backends.common import download_weights
from ....postprocess.nms.yolov5 import non_max_suppression_np


class Yolov5(IModel):
    """Implements IModel for Yolov5 using ONNX.

    This model (onnx-backend) performs inference, using ONNXRUNTIME,
    on a numpy array, and returns result after performing NMS.

    Inputs are expected to be normalized in channels-first order
    with/without batch axis.
    """

    def __init__(self, weight, device: str = 'auto') -> None:
        """Initiate Model

        Args:
            weight (str, optional): path to onnx weight file. Alternatively,
            it also accepts identifiers (such as yolvo5s, yolov5m, etc.) to load
            pretrained models. Defaults to "yolov5s".

            device (str, optional): name of the device to be used. Valid devices can be
            "cpu", "gpu", "auto". Defaults to "auto" which tries to use the device
            best suited for selected backend and the hardware avaibility.
        """
        self._model = weight  # None
        self._device = device

        # self._load_model(weight)

    def _load_model(self, weight: str) -> None:
        """Internally loads ONNX

        Args:
            weight (str): path to ONNX weight file or predefined-identifiers
            (such as yolvo5s, yolov5m, etc.)
        """

        # load model
        if self._device == "cpu":
            # load model on cpu
            self._model = onnxruntime.InferenceSession(
                weight, providers=["CPUExecutionProvider"])
            return

        if self._device == "gpu":
            # load model on gpu
            self._model = onnxruntime.InferenceSession(
                weight, providers=['CUDAExecutionProvider'])
            return

    def __call__(self, inputs: np.ndarray) -> np.ndarray:
        """Performs model inference on given inputs, and returns
        inference's output after NMS.

        Args:
            inputs (np.ndarray): normalized in channels-first format,
            with batch axis.

        Returns:
            np.ndarray: inference's output after NMS
        """
        outputs = self._model.run([self._model.get_outputs()[0].name],
                                  {self._model.get_inputs()[0].name: inputs})
        return self._postprocess(outputs, conf_thres=0.2, iou_thres=0.2)[0]

    def __repr__(self) -> str:
        """Returns Model Information

        Returns:
            str: information string
        """
        return f"Yolov5s ONNX-{self._device}"

    @staticmethod
    def _postprocess(outputs: np.ndarray, conf_thres, iou_thres) -> List[np.ndarray]:
        """Post-process outputs from model inference.
            - Non-Max-Supression

        Args:
            outputs (np.ndarray): model inference's output

        Returns:
           List[np.ndarray]: post-processed output
        """
        # apply nms
        outputs = non_max_suppression_np(outputs[0], conf_thres=conf_thres, iou_thres=iou_thres)
        return outputs
