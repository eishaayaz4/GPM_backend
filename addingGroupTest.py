import cv2
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
def calculate_average_aspect_ratio(boundingBoxes):
    total_height = 0
    total_width = 0
    num_persons = len(boundingBoxes)
    if num_persons == 0:
        return None

    for bounding_box in boundingBoxes:
        x1, y1, x2, y2 = map(int, bounding_box[:4])
        width = x2 - x1
        height = y2 - y1

        total_width+=width
        total_height += height

    avg_width=total_width/num_persons
    avg_height=total_height/num_persons


    aspect_ratio = avg_width / avg_height

    return aspect_ratio, avg_width, avg_height

def resize_individual_image(individual_image, average_aspect_ratio, avg_height, avg_width):
    width_multiplier = 3.5
    height_multiplier = 1.5
    target_width = int(avg_height * average_aspect_ratio * width_multiplier)
    target_height = int(avg_height * height_multiplier)
    resized_individual = cv2.resize(individual_image, (target_width, target_height))

    return resized_individual


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
    group_image = cv2.imread('assets/group.jpg')
    individual = cv2.imread('assets/ali.jpg')
    individual_img_byte = cv2.imencode(".jpg", individual)[1].tobytes()
    output = remove(individual_img_byte)
    with open("removed_bg.png", "wb") as output_file:
        output_file.write(output)
    individual_with_alpha = cv2.imread("removed_bg.png", cv2.IMREAD_UNCHANGED)
    bounding_boxes = detectYolo(group_image)
    if bounding_boxes is not None:
        average_aspect_ratio,avg_width,avg_height = calculate_average_aspect_ratio(bounding_boxes)
        if average_aspect_ratio is not None:
            resized_individual = resize_individual_image(individual_with_alpha,average_aspect_ratio,avg_height,avg_width)
            midpoint_x, midpoint_y = 670.60965347290039 ,282.82403564453125
            blended_image_with_alpha = blend_image_with_alpha(resized_individual, group_image, midpoint_x,midpoint_y)

            cv2.imwrite("BlendedImage.png", blended_image_with_alpha)

        else:
            print("No persons detected in the group image.")
    else:
        print("No bounding boxes detected in the group image.")

