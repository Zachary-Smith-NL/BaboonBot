from PIL import Image
from smoothing import gaussian

def canny(image, gaussian_window, sigma):
    width = image.size[0]
    height = image.size[1]
    w = gaussian_window // 2
    #Apply DoG horizontally and vertically
    output_image = gaussian(image, gaussian_window, sigma, True)
    #Now calculate the gradient magnitude and direction
