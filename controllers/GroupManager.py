import cv2
import numpy as np
from flask import Flask, render_template,jsonify,request
def mergeWithGroupPhoto(userId,imageId,groupPhotoFile):
    return 'MErge photo'

def removeFromGroupPhoto():
    try:
        image_path = request.files['image_path']
        x = int(request.form.get('x'))
        y = int(request.form.get('y'))
        w = int(request.form.get('w'))
        h = int(request.form.get('h'))
        # Read the image
        image = cv2.imdecode(np.fromstring(image_path.read(), np.uint8), cv2.IMREAD_COLOR)
        # Create a binary mask
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
        result = cv2.medianBlur(result, 1)  # You can adjust the kernel size (e.g., 3, 5, 7) based on your preference

            # Display or save the result
        cv2.imshow('Original Image', image)
        cv2.imshow('Result Image', result)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        cv2.imwrite('result_image.jpg', result)
        return {"Message": "image saved successfully"}, 200


    except Exception as e:
        return {'error': str(e)}, 500

    # Example usage
# image_path = 'path/to/your/image.jpg'
# marked_coordinates = (100, 30, 135, 490)
# remove_person(image_path, marked_coordinates)


