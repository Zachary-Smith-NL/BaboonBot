from PIL import Image

def hough(image):
    #First create the image buffer
    width = image.size[0]
    height = image.size[1]
    buffer_size = pow(((width * width) + (height * height)), 0.5) * 360
    hough_image = Image.new(mode="RGB", size=(buffer_size, buffer_size))

    #Now perform edge detection