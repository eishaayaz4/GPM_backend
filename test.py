import cv2
from rembg import remove

img = cv2.imread("assets/20240115012404_image.jpg")

img_bytes = cv2.imencode(".jpg", img)[1].tobytes()

output = remove(img_bytes)

with open("resultImage11.png", "wb") as output_file:
    output_file.write(output)
