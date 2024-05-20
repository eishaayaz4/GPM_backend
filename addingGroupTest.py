import cv2
from flask import jsonify
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


def add_to_group():
    try:
        group_image = cv2.imread('assets/group.jpg')
        individual = cv2.imread('assets/ali.jpg')
        individual_img_byte = cv2.imencode(".jpg", individual)[1].tobytes()
        output = remove(individual_img_byte)
        with open("removed_bg.png", "wb") as output_file:
            output_file.write(output)
        individual_with_alpha = cv2.imread("removed_bg.png", cv2.IMREAD_UNCHANGED)
        bounding_boxes = detectYolo(group_image)
        if bounding_boxes is not None:
            total_height = 0
            total_width = 0
            num_persons = len(bounding_boxes)
            if num_persons == 0:
                return jsonify({'No person detected'})
            for bounding_box in bounding_boxes:
                x1, y1, x2, y2 = map(int, bounding_box[:4])
                width = x2 - x1
                height = y2 - y1
                total_width += width
                total_height += height

            avg_width = total_width / num_persons
            avg_height = total_height / num_persons

            aspect_ratio = avg_width / avg_height
            if aspect_ratio is not None:
                width_multiplier = 3.5
                height_multiplier = 1.5
                target_width = int(avg_height * aspect_ratio * width_multiplier)
                target_height = int(avg_height * height_multiplier)
                resized_individual = cv2.resize(individual_with_alpha, (target_width, target_height))

                midpoint_x, midpoint_y = 670.60965347290039, 282.82403564453125
                blended_image_with_alpha = blend_image_with_alpha(resized_individual, group_image, midpoint_x, midpoint_y)

                cv2.imwrite("BlendedImage.png", blended_image_with_alpha)

        else:
            print("No persons detected in the group image.")
    except Exception as e:
        print(f"An error occurred: {e}")

add_to_group()


