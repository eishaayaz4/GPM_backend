import base64
import os
from io import BytesIO
from operator import or_
import cv2
import numpy as np
from flask import jsonify
from ultralytics import YOLO
from rembg import remove
from flask import Flask, render_template,jsonify,request
import dbHandler as db
from models import Template as t,User as u


def getAllCelebrities():
    try:
        session = db.return_session()
        result = session.query(t.Template).filter_by(type='celebrity').all()
        temp_list = []

        for temp in result:
            temp_info = {
                "id": temp.id,
                "name": temp.name,
                "type": temp.type,
                "category": temp.category,
                "image": temp.image,  # assuming this is the image filename
            }

            temp_list.append(temp_info)

        if temp_list:
            for temp_info in temp_list:
                image_filename = temp_info['image']
                image_path = os.path.join("templates", image_filename)

                if os.path.exists(image_path):
                    with open(image_path, "rb") as image_file:
                        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                        temp_info['image'] = encoded_image

                        # Calculate image width and height using OpenCV
                        img = cv2.imread(image_path)
                        height, width, _ = img.shape
                        temp_info['width'] = width
                        temp_info['height'] = height
                else:
                    temp_info['image'] = None
                    temp_info['width'] = None
                    temp_info['height'] = None

            return temp_list, 200
        else:
            return {"Message": "No template found"}, 404
    except Exception as e:
        return {'error': str(e)}, 500

def getCelebrityBySearch(text):
    try:
        print(text)
        session = db.return_session()
        result = session.query(t.Template).filter(
            t.Template.type == 'celebrity',
            or_(t.Template.category.like(f'%{text}%'), t.Template.name.like(f'%{text}%'))
        ).all()
        celeb_list = []

        for celeb in result:
            celeb_info = {
                "id": celeb.id,
                "name": celeb.name,
                "type": celeb.type,
                "category": celeb.category,
                "image": celeb.image,
                # Add other attributes as needed
            }
            celeb_list.append(celeb_info)

        if celeb_list:
            for temp_info in celeb_list:
                image_filename = temp_info['image']
                image_path = os.path.join("templates", image_filename)

                if os.path.exists(image_path):
                    with open(image_path, "rb") as image_file:
                        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                        temp_info['image'] = encoded_image

                        # Calculate image width and height using OpenCV
                        img = cv2.imread(image_path)
                        height, width, _ = img.shape
                        temp_info['width'] = width
                        temp_info['height'] = height
                else:
                    temp_info['image'] = None
                    temp_info['width'] = None
                    temp_info['height'] = None

            return celeb_list, 200
        else:
            return {"Message": "No celebrities found "}, 404
    except Exception as e:
        return {'error': str(e)}, 500

def getCelebrityById(id):
    try:
        session = db.return_session()
        result = session.query(t.Template).filter(
            t.Template.id == id
        ).one()

        session.close()

        if result:
            image_filename = result.image
            image_path = os.path.join("templates", image_filename)

            if os.path.exists(image_path):
                return image_path, 200
            else:
                return {"Message": "No template found "}, 404
        else:
            return {"Message": "No template found "}, 404
    except Exception as e:
        return {'error': str(e)}, 500


def detectYolo(source):
    model = YOLO("yolov8s.pt")
    classes = [0, 1]
    conf_thresh = 0.5
    results = model.predict(source=source, classes=classes, conf=conf_thresh)
    boundingBoxes = []
    for result in results[0].boxes.data:
        boundingBoxes.append(result.tolist())
    return boundingBoxes

def convert_coordinates(x, y, actual_image_width, actual_image_height, image_width, image_height):
    actual_x = int(x / float(image_width) * float(actual_image_width))
    actual_y = int(y / float(image_height) * float(actual_image_height))
    return actual_x, actual_y

def image_to_base64(image):
    _, buffer = cv2.imencode('.jpg', image)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    return image_base64

def blend_image_with_alpha(resized_individual, group_image, midpoint_x, midpoint_y):
    individual_width = resized_individual.shape[1]
    individual_height = resized_individual.shape[0]

    target_x1 = int(midpoint_x - individual_width / 2)
    target_y1 = int(midpoint_y - individual_height / 2)
    target_x2 = int(midpoint_x + individual_width / 2)
    target_y2 = int(midpoint_y + individual_height / 2)

    target_x1 = max(0, target_x1)
    target_y1 = max(0, target_y1)
    target_x2 = min(group_image.shape[1], target_x2)
    target_y2 = min(group_image.shape[0], target_y2)

    resized_individual = cv2.resize(resized_individual, (target_x2 - target_x1, target_y2 - target_y1))

    alpha = resized_individual[:, :, 3] / 255.0
    alpha_inv = 1.0 - alpha

    blended_image = group_image.copy()
    for c in range(0, 3):
        blended_image[target_y1:target_y2, target_x1:target_x2, c] = (
            alpha * resized_individual[:, :, c] + alpha_inv * blended_image[target_y1:target_y2, target_x1:target_x2, c]
        )

    return blended_image


def MergeWithCelebrity():
    try:
        id = int(float(request.form.get('id')))
        individualImage_path = request.files['image']
        x = int(float(request.form.get('x')))
        y = int(float(request.form.get('y')))
        image_width = int(float(request.form.get('imageWidth')))
        image_height = int(float(request.form.get('imageHeight')))
        actual_image_width = int(request.form.get('actualImageWidth'))
        actual_image_height = int(request.form.get('actualImageHeight'))


        actual_x, actual_y = convert_coordinates(x, y, actual_image_width, actual_image_height, image_width,
                                                 image_height)

        image_path, status_code = getCelebrityById(id)
        celebrity_image = cv2.imread(image_path)
        individual_image = cv2.imread(individualImage_path)
        individual_img_byte = cv2.imencode(".jpg", individual_image)[1].tobytes()
        output = remove(individual_img_byte)
        with open("removed_individual.png", "wb") as output_file:
            output_file.write(output)
        individual_with_alpha = cv2.imread("removed_individual.png", cv2.IMREAD_UNCHANGED)
        bounding_boxes = detectYolo(celebrity_image)
        if bounding_boxes is not None:
            total_height = 0
            total_width = 0
            num_persons = len(bounding_boxes)
            for bounding_box in bounding_boxes:
                x1, y1, x2, y2 = map(int, bounding_box[:4])
                width = x2 - x1
                height = y2 - y1
                total_width += width
                total_height += height

            avg_width = total_width  / num_persons
            avg_height = total_height / num_persons

            aspect_ratio = avg_width / avg_height
            if aspect_ratio is not None:
                width_multiplier = 3.5
                height_multiplier = 1.1
                target_width = int(avg_height * aspect_ratio * width_multiplier)
                target_height = int(avg_height * height_multiplier)
                resized_individual = cv2.resize(individual_with_alpha, (target_width, target_height))
                blended_image_with_alpha = blend_image_with_alpha(resized_individual, celebrity_image, actual_x, actual_y)
                result_image_base64=image_to_base64(blended_image_with_alpha)
                cv2.imwrite("addWithCelebrity_result.png", blended_image_with_alpha)
                return {'result_image_base64': result_image_base64}
                return jsonify({'success': 'Done'})

        else:
            return "No celebrity detected.",404
    except Exception as e:
        print(f"An error occurred: {e}")
        return {'error': str(e)}, 500




