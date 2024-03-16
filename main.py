import cv2
import numpy as np

def remove_person(image_path, marked_coordinates):
    # Read the image
    image = cv2.imread('./assets/friends.jpg')

    # Create a binary mask
    mask = np.ones_like(image)
    x, y, w, h = marked_coordinates
    mask[y:y+h, x:x+w] = 0

    # Apply the mask
    result = image * mask

    # Display or save the result
    cv2.imshow('Original Image', image)
    cv2.imshow('Result Image', result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Optionally, save the result to a file
    cv2.imwrite('result_image.jpg', result)

# # Example usage
# image_path = 'path/to/your/image.jpg'
# marked_coordinates = (143, 90, 70, 290)
# remove_person(image_path, marked_coordinates)