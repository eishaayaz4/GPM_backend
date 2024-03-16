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

def resize_with_aspect_ratio(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    h, w = image.shape[:2]

    if width is None and height is None:
        return image

    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
        aspect_ratio_group = int(w * r) / height
    else:
        r = width / float(w)
        dim = (width, int(h * r))
        aspect_ratio_group = width / int(h * r)

    resized = cv2.resize(image, dim, interpolation=inter)

    print("Aspect of group", aspect_ratio_group)
    return resized

def calculate_average_aspect_ratio(boundingBoxes):
    total_aspect_ratio = 0
    num_persons = len(boundingBoxes)
    if num_persons == 0:
        return None

    for bounding_box in boundingBoxes:
        x1, y1, x2, y2 = map(int, bounding_box[:4])
        width = x2 - x1
        height = y2 - y1
        aspect_ratio = width / height
        total_aspect_ratio += aspect_ratio

    average_aspect_ratio = total_aspect_ratio / num_persons
    return average_aspect_ratio

def resize_individual_image(individual_image, average_aspect_ratio):
    individual_h, individual_w = individual_image.shape[:2]
    target_width = int(individual_h * average_aspect_ratio)
    resized_individual = cv2.resize(individual_image, (target_width, individual_h))
    return resized_individual

group_image = cv2.imread('assets/friends.jpg')
individual_image = cv2.imread('assets/individual.jpg')
bounding_boxes = detectYolo(group_image)

if bounding_boxes is not None:
    average_aspect_ratio = calculate_average_aspect_ratio(bounding_boxes)
    if average_aspect_ratio is not None:
        resized_individual = resize_individual_image(individual_image, average_aspect_ratio)
        cv2.imshow("Resized Individual Image", resized_individual)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("No persons detected in the group image.")
else:
    print("No bounding boxes detected in the group image.")
