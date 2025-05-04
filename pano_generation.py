import cv2
import argparse
import os
import numpy as np


def remove_black_borders(img):
    # Create a 10 pixel border surrounding the image
    stitched = cv2.copyMakeBorder(img, 10, 10, 10, 10,
                                 cv2.BORDER_CONSTANT, (0, 0, 0))
    
    # Convert the image to grayscale and threshold it
    gray = cv2.cvtColor(stitched, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)[1]
    
    # Find all external contours in the threshold image
    _, cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                 cv2.CHAIN_APPROX_SIMPLE)
    
    if not cnts:
        return img
    
    # Find the largest contour
    c = max(cnts, key=cv2.contourArea)
    
    # Create a mask for the rectangular bounding box
    mask = np.zeros(thresh.shape, dtype="uint8")
    (x, y, w, h) = cv2.boundingRect(c)
    cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)
    
    # Create two copies of the mask
    minRect = mask.copy()
    sub = mask.copy()
    
    # Keep eroding until we find the minimum rectangular region
    while cv2.countNonZero(sub) > 0:
        # Erode the minimum rectangular mask
        minRect = cv2.erode(minRect, None)
        # Subtract the thresholded image from the minimum rectangular mask
        sub = cv2.subtract(minRect, thresh)
    
    # Find contours in the minimum rectangular mask
    _, cnts, _ = cv2.findContours(minRect.copy(), cv2.RETR_EXTERNAL,
                                 cv2.CHAIN_APPROX_SIMPLE)
    
    if not cnts:
        return img
    
    # Get the bounding box of the largest contour
    c = max(cnts, key=cv2.contourArea)
    (x, y, w, h) = cv2.boundingRect(c)
    
    # Extract the final image
    cropped = stitched[y:y + h, x:x + w]
    
    return cropped

def main(panorama_name="panorama"):
    # Create a list to store all images
    images = []

    key_frame_num = len([f for f in os.listdir("key_frames")])
    
    # Read all images
    for i in range(key_frame_num):
        img_path = 'key_frames/frame{}.jpg'.format(i)
        if os.path.exists(img_path):
            img = cv2.imread(img_path)
            if img is not None:
                images.append(img)
                print(f"Loaded frame{i}.jpg")
    
    if not images:
        print("No valid images found!")
        return

    # Create a stitcher object for OpenCV 3.4.2.17
    stitcher = cv2.createStitcher(False)  # False for panorama mode
    
    # Perform stitching
    print("Starting panorama stitching...")
    status, result = stitcher.stitch(images)
    
    if status == cv2.Stitcher_OK:
        # Remove black borders
        print("Removing black borders...")
        result = remove_black_borders(result)
        
        # Save the result with the specified name
        output_path = f'{panorama_name}.jpg'
        cv2.imwrite(output_path, result)
        print(f"Panorama saved as {output_path}!")
    else:
        print("Stitching failed!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, default='panorama')
    args = parser.parse_args()
    main(args.name)
