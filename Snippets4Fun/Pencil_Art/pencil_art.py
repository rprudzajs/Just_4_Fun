##Important to install: pip install opencv-python
##Must be done in the correct environment
##All files should be in the same folder

import cv2

# Load .jpg file
image = cv2.imread("example_image.jpg")  #Insert the name of your own file

# Convert the image to grayscale
image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
image_invert = 255 - image_gray

# Apply Gaussian Blur
blurred = cv2.GaussianBlur(image_invert, (21, 21), 0)

# Invert the blurred image
inverted_blurred = 255 - blurred

# Create the pencil sketch
pencil_sketch = cv2.divide(image_gray, inverted_blurred, scale=256.0)

# Display the original and sketch images
cv2.imshow("Original", image)
cv2.imshow("Sketch", pencil_sketch)

# Save the sketch image
cv2.imwrite("pencil_sketch_output2.jpg", pencil_sketch)

cv2.waitKey(0)
