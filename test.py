import cv2
from ultralytics import YOLO

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

        total_width += width
        total_height += height

    avg_width = total_width / num_persons
    avg_height = total_height / num_persons

    aspect_ratio = avg_width / avg_height

    return aspect_ratio, avg_width, avg_height

def resize_individual_image(individual_image, average_aspect_ratio, avg_height, avg_width):
    target_width = int(avg_height * average_aspect_ratio)
    target_height = int(avg_height)
    resized_individual = cv2.resize(individual_image, (target_width, target_height))

    return resized_individual

def blend_image(resized_individual, midpoint_x, midpoint_y, group_image):
    individual_width = resized_individual.shape[1]
    individual_height = resized_individual.shape[0]
    target_x1 = int(midpoint_x - individual_width / 2)
    target_y1 = int(midpoint_y - individual_height / 2)
    target_x2 = target_x1 + individual_width
    target_y2 = target_y1 + individual_height

    target_x1 = max(0, target_x1)
    target_y1 = max(0, target_y1)
    target_x2 = min(group_image.shape[1], target_x2)
    target_y2 = min(group_image.shape[0], target_y2)

    resized_individual = cv2.resize(individual_image, (target_x2 - target_x1, target_y2 - target_y1))

    blended_image = group_image.copy()
    blended_image[target_y1:target_y2, target_x1:target_x2] = resized_individual

    # Create a mask for the white background of the individual image
    mask = cv2.cvtColor(resized_individual, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(mask, 240, 255, cv2.THRESH_BINARY)

    # Inpaint the group image using the mask and blended individual image
    inpainted_group = cv2.inpaint(group_image, mask, 3, cv2.INPAINT_TELEA)

    # Replace the inpainted group image in the blended image
    blended_image = inpainted_group

    return blended_image

group_image = cv2.imread('assets/img.png')
individual_image = cv2.imread('assets/individual.jpg')
bounding_boxes = detectYolo(group_image)

if bounding_boxes is not None:
    average_aspect_ratio, avg_width, avg_height = calculate_average_aspect_ratio(bounding_boxes)
    if average_aspect_ratio is not None:
        resized_individual = resize_individual_image(individual_image, average_aspect_ratio, avg_height, avg_width)

        midpoint_x, midpoint_y = 110, 360
        blended_image = blend_image(resized_individual, midpoint_x, midpoint_y, group_image)

        cv2.imshow("Blended Image", blended_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("No persons detected in the group image.")
else:
    print("No bounding boxes detected in the group image.")
