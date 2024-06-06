import cv2
import numpy as np

def create_mask_manually(image):
    # Create a black and white mask of the same size as the input image
    mask = np.zeros(image.shape[:2], dtype=np.uint8)

    # Draw a white filled rectangle as the mask (example: for a person to be inpainted)
    x1, y1, x2, y2 = 100, 100, 300, 400  # Example coordinates of the rectangle
    cv2.rectangle(mask, (x1, y1), (x2, y2), (255), -1)  # Use (255) for white in a single-channel image

    return mask

def main_exemplar():
    image_path = './assets/sisters.jpeg'

    # Load the image
    image = cv2.imread(image_path)

    # Create the mask manually
    mask = create_mask_manually(image)  # Pass the image to create_mask_manually

    # Convert the mask to a 3-channel format (for compatibility with cv2.inpaint)
    mask_color = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    # Use Navier-Stokes based Exemplar-Based Inpainting
    result = cv2.inpaint(image, mask_color, inpaintRadius=3, flags=cv2.INPAINT_NS)

    # Save the result
    cv2.imwrite('exemplar_inpainting_result.jpg', result)

if __name__ == '__main__':
    main_exemplar()
