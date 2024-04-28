import base64
import cv2
import numpy as np
from flask import Flask, request, jsonify
from ultralytics import YOLO
from rembg import remove

def detectYolo(source):
    model = YOLO("yolov8s.pt")
    classes = [0, 1]
    conf_thresh = 0.5
    results = model.predict(source=source, classes=classes, conf=conf_thresh)
    boundingBoxes = []
    for result in results[0].boxes.data:
        boundingBoxes.append(result.tolist())
    return boundingBoxes


def addToGroup():
    try:
        groupImage_path = request.files['groupImage']
        individualImage_path = request.files['individualImage']
        x = float(request.form.get('x'))
        y = float(request.form.get('y'))

        group_image = cv2.imread(groupImage_path)
        cv2.imwrite('received_group_image.jpg', group_image)

        individual_image = cv2.imread(individualImage_path)
        cv2.imwrite('received_individual_image.jpg', individual_image)

        individual_img = cv2.imencode(".jpg", individual_image)[1].tobytes()
        output = remove(individual_img)
        with open("removed_bg.png", "wb") as output_file:
            output_file.write(output)
        individual_image = cv2.imread("removed_bg.png")


        bounding_boxes = detectYolo(group_image)
        if bounding_boxes is not None:
            total_height = 0
            total_width = 0
            num_persons = len(bounding_boxes)
            if num_persons == 0:
                return None

            for bounding_box in bounding_boxes:
                x1, y1, x2, y2 = map(int, bounding_box[:4])
                width = x2 - x1
                height = y2 - y1

                total_width += width
                total_height += height

            avg_width = total_width / num_persons
            avg_height = total_height / num_persons
            average_aspect_ratio = avg_width / avg_height
            if average_aspect_ratio is not None:
                target_width = int(avg_height * average_aspect_ratio)
                target_height = int(avg_height)
                resized_individual = cv2.resize(individual_image, (target_width, target_height))

                individual_width = resized_individual.shape[1]
                individual_height = resized_individual.shape[0]
                target_x1 = int(x - individual_width / 2)
                target_y1 = int(y - individual_height / 2)
                target_x2 = target_x1 + individual_width
                target_y2 = target_y1 + individual_height

                target_x1 = max(0, target_x1)
                target_y1 = max(0, target_y1)
                target_x2 = min(group_image.shape[1], target_x2)
                target_y2 = min(group_image.shape[0], target_y2)
                resized_individual = cv2.resize(individual_image, (target_x2 - target_x1, target_y2 - target_y1))
                blended_image = group_image.copy()
                blended_image[target_y1:target_y2, target_x1:target_x2] = resized_individual
                result_image_base64 = image_to_base64(blended_image)

                # Return the result image as Base64
                return {'result_image_base64': result_image_base64}
            else:
                return "No persons detected in the group image.",404
        else:
            return "No bounding boxes detected in the group image.",404
    except Exception as e:
        print(f"An error occurred: {e}")
        return {'error': str(e)}, 500




def image_to_base64(image):
    _, buffer = cv2.imencode('.jpg', image)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    return image_base64

def convert_coordinates(x, y, actual_image_width, actual_image_height, image_width, image_height):
    actual_x = int(x / float(image_width) * float(actual_image_width))
    actual_y = int(y / float(image_height) * float(actual_image_height))
    return actual_x, actual_y

def remove_person_helper(image, bounding_boxes, actual_x, actual_y):
    try:
        for bounding_box in bounding_boxes:
            x1, y1, x2, y2 = map(int, map(float, bounding_box[:4]))
            if x1 <= round(actual_x) <= x2 and y1 <= round(actual_y) <= y2:

                w = x2 - x1
                h = y2 - y1

                x, y, w, h = int(x1), int(y1), int(w), int(h)

                mask = np.ones_like(image)
                mask[y:y + h, x:x + w] = 0
                mask = (mask * 255).astype(np.uint8)
                mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
                mask_inv = cv2.bitwise_not(mask)

                result = image.copy()
                result[y:y + h, x:x + w] = 0
                result = cv2.inpaint(result, mask_inv, inpaintRadius=20, flags=cv2.INPAINT_TELEA)
                result = cv2.medianBlur(result, 1)

                return result
        return None

    except Exception as e:
        return {'error': str(e)}, 500

def removeFromGroupPhoto():
    try:
        image_file = request.files['image']
        x = int(float(request.form.get('x')))
        y = int(float(request.form.get('y')))
        actual_image_width = int(request.form.get('actualImageWidth'))
        actual_image_height = int(request.form.get('actualImageHeight'))
        image_width = int(float(request.form.get('imageWidth')))
        image_height = int(float(request.form.get('imageHeight')))

        actual_x, actual_y = convert_coordinates(x, y, actual_image_width, actual_image_height, image_width, image_height)

        file_stream = image_file.stream
        file_stream.seek(0)
        file_bytes = np.asarray(bytearray(file_stream.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        resultedImage = remove_person_helper(image,detectYolo(image),actual_x,actual_y)
        cv2.imwrite("ResuledImage.png", resultedImage)

        return jsonify({'success': 'Done'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500



