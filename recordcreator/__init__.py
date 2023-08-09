import cv2
import numpy as np


def resize_pie():
    # resizes and pads the image into the desired size
    pass

def place_pies(pies):
    # equally distributes the pies parts over a circular image

    img = np.zeros((2048,2048,3), dtype=np.uint8)

    cv2.circle(img, (1024,1024), 1024)

    for pie in pies:
        pass