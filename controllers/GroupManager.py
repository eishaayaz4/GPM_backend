import cv2
import numpy as np
from flask import Flask,request
from ultralytics import YOLO


def mergeWithGroupPhoto(userId,imageId,groupPhotoFile):
    return 'MErge photo'

def detectYolo(source):
    model = YOLO("yolov8s.pt")
    classes = [0, 1]
    conf_thresh = 0.5
    results = model.predict(source=source, classes=classes, conf=conf_thresh)
    boundingBoxes = []
    for result in results[0].boxes.data:
        boundingBoxes.append(result.tolist())
    return boundingBoxes
def removeFromGroupPhoto():
    try:
        image_path = request.files['image_path']
        x = float(request.form.get('x'))  # Convert to float first
        y = float(request.form.get('y'))  # Convert to float first
        image = cv2.imread(image_path)
        bounding_boxes = detectYolo(image)

        if bounding_boxes is not None:
            for i, bounding_box in enumerate(bounding_boxes):
                x1, y1, x2, y2 = map(int, map(float, bounding_box[:4]))

                # Print bounding box coordinates and clicked point for debugging
                print(f"Bounding Box {i}: x1={x1}, y1={y1}, x2={x2}, y2={y2}")
                print(f"Clicked Point (x, y): {x}, {y}")

                # Check if the point (x, y) is within the current bounding box
                if x1 <= round(x) <= x2 and y1 <= round(y) <= y2:
                    # Calculate width and height of the bounding box
                    w = x2 - x1
                    h = y2 - y1
                    print(f"Width of bounding box: {w}, Height of bounding box: {h}")

                    # Convert coordinates to integers
                    x, y, w, h = int(x1), int(y1), int(w), int(h)

                    # Create a binary mask for the current bounding box
                    mask = np.ones_like(image)
                    mask[y:y + h, x:x + w] = 0
                    # Convert mask to 8-bit 1-channel image
                    mask = (mask * 255).astype(np.uint8)
                    mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
                    # Invert the mask to focus inpainting only on the specified coordinates
                    mask_inv = cv2.bitwise_not(mask)
                    # Set the marked area in the result to black
                    result = image.copy()
                    result[y:y + h, x:x + w] = 0
                    # Inpainting to fill the masked area with background content
                    result = cv2.inpaint(result, mask_inv, inpaintRadius=20, flags=cv2.INPAINT_TELEA)
                    # Apply median blur to improve background quality
                    result = cv2.medianBlur(result,
                                            1)  # You can adjust the kernel size (e.g., 3, 5, 7) based on your preference

                    # Display or save the result
                    cv2.imshow('Original Image', image)
                    cv2.imshow('Result Image', result)
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()
                    cv2.imwrite('result_image.jpg', result)
                    return result
                    break  # Break out of the loop after processing the correct bounding box

        # If no bounding box contains the point (x, y), return an error response
        return {'error': 'Point (x, y) does not belong to any bounding box.'}, 404

    except Exception as e:
        print(str(e))
        return {'error': str(e)}, 500
# image_path = 'path/to/your/image.jpg'
# marked_coordinates = (100, 30, 135, 490)
# remove_person(image_path, marked_coordinates)


