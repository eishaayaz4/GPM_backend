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

    print("Asspect of group",aspect_ratio_group)
    return resized

def resize_group_to_individual_aspect_ratio(group_image, individual_image):
    group_h, group_w = group_image.shape[:2]
    individual_h, individual_w = individual_image.shape[:2]

    aspect_ratio = individual_w / individual_h
    print("aspect ratio of individual",aspect_ratio)
    resized_group = resize_with_aspect_ratio(group_image, width=int(group_h * aspect_ratio))

    return resized_group

group_image = cv2.imread('assets/group.jpg')
group_height,group_widht = group_image.shape[:2]
individual_image = cv2.imread('assets/individual.jpg')
bounding_boxes = detectYolo(group_image)

if bounding_boxes is not None:
    for i, bounding_box in enumerate(bounding_boxes):
        x1, y1, x2, y2 = map(int, bounding_box[:4])
        person_image = group_image[y1:y2, x1:x2]
        resized_person = resize_group_to_individual_aspect_ratio(person_image, individual_image)
        cv2.imshow(f"Person {i + 1}", resized_person)

cv2.waitKey(0)
cv2.destroyAllWindows()