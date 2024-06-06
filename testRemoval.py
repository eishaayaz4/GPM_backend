import cv2
import numpy as np

def remove_person(image_path, marked_coordinates):
    # Read the image
    image = cv2.imread('./assets/group.jpg')

    # Create a binary mask
    mask = np.ones_like(image)
    x, y, w, h = marked_coordinates
    mask[y:y+h, x:x+w] = 0

    # Convert mask to 8-bit 1-channel image
    mask = (mask * 255).astype(np.uint8)
    mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

    # Invert the mask to focus inpainting only on the specified coordinates
    mask_inv = cv2.bitwise_not(mask)

    # Set the marked area in the result to black
    result = image.copy()
    result[y:y+h, x:x+w] = 0

    # Inpainting to fill the masked area with background content
    result = cv2.inpaint(result, mask_inv, inpaintRadius=20, flags=cv2.INPAINT_TELEA)

    # Apply median blur to improve background quality
    result = cv2.medianBlur(result, 1)  # You can adjust the kernel size (e.g., 3, 5, 7) based on your preference

    # Display or save the result
    cv2.imshow('Original Image', image)
    cv2.imshow('Result Image', result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Optionally, save the result to a file
    cv2.imwrite('result_image.jpg', result)

# Example usage
image_path = './assets/sisters.jpeg'
marked_coordinates = (100, 30, 135, 490)
remove_person(image_path, marked_coordinates)
