import base64
import os
from operator import or_
import dbHandler as db
from models import Template as t
from io import BytesIO
import cv2
import numpy as np
from PIL import Image
from flask import request, jsonify
from rembg import remove


def merge_images(foreground, background,y=0):
    foreground_img = np.array(foreground)
    bg_img = np.array(background)
    foreground_ratio = foreground_img.shape[1] / foreground_img.shape[0]
    background_ratio = bg_img.shape[1] / bg_img.shape[0]

    if foreground_ratio > background_ratio:  # Landscape foreground
        new_width = bg_img.shape[1]
        new_height = int(new_width / foreground_ratio)
    else:  # Portrait or square foreground
        new_height = bg_img.shape[0]
        new_width = int(new_height * foreground_ratio)

    foreground_resized = cv2.resize(foreground_img, (new_width, new_height), interpolation=cv2.INTER_AREA)

    # Calculate x_offset and y_offset for centering foreground on background
    x_offset = (bg_img.shape[1] - new_width) // 2
    y_offset = (bg_img.shape[0] - new_height) // 2+y

    result = Image.new("RGBA", (bg_img.shape[1], bg_img.shape[0]))
    result.paste(Image.fromarray(bg_img), (0, 0))
    result.paste(Image.fromarray(foreground_resized), (x_offset, y_offset), Image.fromarray(foreground_resized))

    return result


def ChangeBackground():
    try:
        background_img = cv2.imread('./assets/snow_bg.jpg')
        image_data = cv2.imread('./assets/group.jpg')
        img = remove(image_data)
        if img is None:
            print("Background Not Removed")
            return

        foreground = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
        background = cv2.cvtColor(background_img, cv2.COLOR_BGR2RGBA)
        result_image = merge_images(foreground, background)

        if result_image is None:
            print("Error in merging images")
            return

        result_image.save(os.path.join("./results", "changed_bg.png"))
        print("Background changed successfully!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

ChangeBackground()
