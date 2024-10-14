from rembg import remove
from PIL import Image, ImageEnhance
import cv2
import numpy as np
import io


def create_gradient(width, height):
    # Create a new image with RGBA mode
    gradient_image = Image.new('RGBA', (width, height))

    for y in range(height):
        # Calculate the color for this row
        # Lighter sky blue (175, 226, 255) to medium sky blue (70, 130, 180)
        r = int(175 - (105 * (y / height)))  # Red decreases from 175 to 70
        g = int(226 - (96 * (y / height)))   # Green decreases from 226 to 130
        b = int(255 - (75 * (y / height)))   # Blue decreases from 255 to 180
        for x in range(width):
            gradient_image.putpixel((x, y), (r, g, b, 255))  # Set pixel color

    return gradient_image




def remove_background_and_center_face(input_image, output_image_path=None):
    # Step 1: Remove background using rembg
    output_image = remove(input_image)
    img = Image.open(io.BytesIO(output_image))

    if img.mode != 'RGBA':  # Ensure the image has an alpha channel for transparency
        img = img.convert('RGBA')

    # Convert image to numpy array for OpenCV face detection
    img_np = np.array(img)

    # Load OpenCV face detector (Haar Cascade)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Convert RGB image to grayscale
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGBA2GRAY)

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        print("No face detected in the image.")
        return None

    # Get the first detected face
    (x, y, w, h) = faces[0]

    # Calculate the center and size of the square crop
    face_center_x = x + w // 2
    face_center_y = y + h // 2
    crop_size = max(w, h)
    half_crop_size = crop_size // 1

    # Ensure the crop is within image bounds
    crop_box = (
        max(face_center_x - half_crop_size, 0),
        max(face_center_y - half_crop_size, 0),
        min(face_center_x + half_crop_size, img.width),
        min(face_center_y + half_crop_size, img.height)
    )

    # Step 4: Crop the image
    cropped_img = img.crop(crop_box)
    resized_img = cropped_img.resize((500, 500), Image.Resampling.LANCZOS)

    # Step 5: Enhance the image
    # Enhance Sharpness
    enhancer_sharpness = ImageEnhance.Sharpness(resized_img)
    enhanced_img = enhancer_sharpness.enhance(2)  # Increase sharpness

    # Enhance Contrast
    enhancer_contrast = ImageEnhance.Contrast(enhanced_img)
    enhanced_img = enhancer_contrast.enhance(1.0)  # Increase contrast

    # Enhance Brightness
    enhancer_brightness = ImageEnhance.Brightness(enhanced_img)
    enhanced_img = enhancer_brightness.enhance(1.1)  # Increase brightness

    # Step 6: Create a new white background image with the same size
    background = create_gradient(500, 500) # Create a white background

    # Step 7: Composite the transparent image onto the white background
    final_img = Image.alpha_composite(background, enhanced_img)

    if output_image_path:
        final_img.save(output_image_path, 'PNG')  # Save if path is provided

    return final_img  # Return the final image
