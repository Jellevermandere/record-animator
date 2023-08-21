import cv2
import numpy as np
from skimage.io import imread_collection
import imageio

def rotate_image(image: np.array, angle: float):
    """Rotates an image by a certain amount of degrees

    Args:
        image (np.array): The input images as an cv2 Image
        angle (float): The amount of degrees to rotate the image around the center

    Returns:
        np.array: The rotated image
    """
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result

def create_blank_record(size:int = 2048, color:tuple = (20,20,20,255), bufferFraction:float = 8, pinFraction:float = 50):
    """creates a circular record image with a desired background color

    Args:
        size (int, optional): The pixel diameter of the image. Defaults to 2048.
        color (tuple, optional): The background color. Defaults to (20,20,20,255).
        bufferFraction (float, optional): The shrinking factor for the label buffer. Defaults to 8.
        pinFraction (float, optional): The shrinking factor for the center pinhole. Defaults to 50.

    Returns:
        np.array: The cv2 image of the record
    """
    
    if(len(color) == 3):
        color = np.hstack((np.array(color),255)).tolist()
        print(color)

    halfSize = int(np.floor(size/2))
    bufferSize = int(np.floor(size/bufferFraction))
    pinSize = int(np.floor(size/pinFraction))
    size = halfSize * 2
    img = np.zeros((size,size,4), dtype=np.uint8)
    circle = cv2.circle(img, (halfSize,halfSize), halfSize, color, -1)
    record = cv2.circle(circle, (halfSize,halfSize), bufferSize, (255,255,255,255), -1)
    record = cv2.circle(record, (halfSize,halfSize), pinSize, (0,0,0,0), -1)
    return record

def overlay_transparent(backgroundImg: np.array, overlayImg: np.array, x:int, y:int, overlaySize: tuple=None):
    """Overlay a transparent image on a background image

    Args:
        backgroundImg (np.array): The background
        overlayImg (np.array): The image to overlay
        x (int): the horizontal top-left corner position offset
        y (int): the vertical top-left corner position offset
        overlaySize (tuple, optional): The new image size to scale the overlay image to . Defaults to None.

    Returns:
        np.array: The combined image
    """

    bg_img = backgroundImg.copy()
    if overlaySize is not None:
        overlayImg = cv2.resize(overlayImg.copy(), overlaySize)
                
    # Extract the alpha mask of the RGBA image, convert to RGB 
    b,g,r,a = cv2.split(overlayImg)
    overlay_color = cv2.merge((b,g,r,a))
    # Apply some simple filtering to remove edge noise
    mask = cv2.medianBlur(a,5)
        
    h, w, _ = overlay_color.shape
    roi = bg_img[y:y+h, x:x+w]
    # Black-out the area behind the logo in our original ROI
    img1_bg = cv2.bitwise_and(roi.copy(),roi.copy(),mask = cv2.bitwise_not(mask))
    # Mask out the logo from the logo image.
    img2_fg = cv2.bitwise_and(overlay_color,overlay_color,mask = mask)
    # Update the original image with our new ROI
    bg_img[y:y+h, x:x+w] = cv2.add(img1_bg, img2_fg)

    return bg_img

def place_pies(recordImg: np.array, slices: list[np.array]):
    """Equally distributes the slices over a circular image

    Args:
        recordImg (np.array): The background image
        slices (list[np.array]): The list of all the slices, in order

    Returns:
        np.array: The completed image
    """

    resultImg = recordImg.copy()
    nrOfImages = len(slices)
    

    topLeftLocation = int(recordImg.shape[1]/2) - int(slices[0].shape[1]/2)
    centerLocation = int(recordImg.shape[1]/2)

    for i in range(nrOfImages):
        resultImg = overlay_transparent(resultImg, slices[i],topLeftLocation, centerLocation)
        resultImg = rotate_image(resultImg,360.0/nrOfImages)

    return resultImg

def create_animation_record(slicesPath:str, bgColor:tuple = (20,20,20), resize:int = None):
    """Creates a animation record from a given image folder and optional background color

    Args:
        slicesPath (str): the folder path containing all the images in order
        bgColor (tuple, optional): the background color. Defaults to (20,20,20).
        resize (int, optional): The new dimension of the image. Defaults to None.

    Returns:
        np.array: The completed record image
    """

    #creating a collection with the available images
    slices = imread_collection(slicesPath)
    # get the height of the slice to determine the record diameter
    blankRecordSize = int(slices[0].shape[0]*2)
    
    img = create_blank_record(blankRecordSize, bgColor)
    result = place_pies(img, slices)

    if(resize is not None):
        result = cv2.resize(result, (resize, resize))
    return result


def save_record_gif(recordImage:np.array, frames:int = 32, outputPath:str = 'output/video.gif', duration:float = 41.666):
    """Saves an animated gif of the record image

    Args:
        recordImage (np.array): the image to animate
        frames (int, optional): The amount of frames on the record. Defaults to 32.
        outputPath (str, optional): The save path, must include the .gif extension. Defaults to 'output/video.gif'.
        duration (float, optional): the duration of a single frame in milliseconds. Defaults to 41.666.
    """
    image_lst = []
    for i in range(frames):
        image_lst.append(recordImage)
        recordImage = rotate_image(recordImage,360.0/frames)

    imageio.mimsave(outputPath, image_lst, duration=duration)