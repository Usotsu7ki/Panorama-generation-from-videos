"""Extract key frames from video using SIFT feature matching and RANSAC."""
import cv2
import numpy as np
import argparse
import os


def is_blurry(image, threshold=30.0):
    # Check if image is blurry using Laplacian variance
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var < threshold


def clear_directory(directory):
    # Clear all files in directory or create if not exists
    if os.path.exists(directory):
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error clearing directory: {str(e)}")
                return False
    else:
        os.makedirs(directory)
    return True


def main(videofile, stride=10):
    # Extract key frames from video file
    if not clear_directory('key_frames'):
        print("Failed to prepare key_frames directory")
        return

    vid = cv2.VideoCapture(videofile)
    sift = cv2.xfeatures2d.SIFT_create()

    # Get first frame
    success, last = vid.read()
    if success and not is_blurry(last):
        cv2.imwrite('key_frames/frame0.jpg', last)
        print("Captured frame0.jpg")
        count = 1
        frame_num = 1
    else:
        print("First frame is blurry or invalid, trying next frame...")
        count = 0
        frame_num = 0

    w = int(last.shape[1] * 2 / 3)  # Region for matching points
    min_num = 100  # Min matches for good stitching
    max_num = 600  # Max matches to avoid redundancy

    while success:
        if count % stride == 0:
            if is_blurry(image):
                print(f"Frame {count} is blurry, skipping...")
                success, image = vid.read()
                count += 1
                continue

            # Get keypoints and descriptors
            kp1, des1 = sift.detectAndCompute(last[:, -w:], None)
            kp2, des2 = sift.detectAndCompute(image[:, :w], None)

            if des1 is None or des2 is None or len(kp1) < 10 or len(kp2) < 10:
                print(f"Frame {count} has insufficient keypoints, skipping...")
                success, image = vid.read()
                count += 1
                continue

            # Match keypoints
            bf = cv2.BFMatcher(normType=cv2.NORM_L2)
            matches = bf.knnMatch(des1, des2, k=2)

            # Filter matches
            match_ratio = 0.6
            valid_matches = []
            for m1, m2 in matches:
                if m1.distance < match_ratio * m2.distance:
                    valid_matches.append(m1)

            if len(valid_matches) > 4:
                img1_pts = []
                img2_pts = []
                for match in valid_matches:
                    img1_pts.append(kp1[match.queryIdx].pt)
                    img2_pts.append(kp2[match.trainIdx].pt)

                img1_pts = np.float32(img1_pts).reshape(-1, 1, 2)
                img2_pts = np.float32(img2_pts).reshape(-1, 1, 2)

                # Compute homography
                _, mask = cv2.findHomography(img1_pts, img2_pts, cv2.RANSAC, 5.0)

                if min_num < np.count_nonzero(mask) < max_num:
                    last = image
                    print(f"Captured frame{frame_num}.jpg")
                    cv2.imwrite(f'key_frames/frame{frame_num}.jpg', last)
                    frame_num += 1
        success, image = vid.read()
        count += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?', default='video.mp4')
    parser.add_argument('--stride', type=int, default=10)
    args = parser.parse_args()

    main(args.file, stride=args.stride)
