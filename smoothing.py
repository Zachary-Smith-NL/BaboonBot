from PIL import Image

#Mean filter
def mean(filename, window):
    #The mean filter is separable and iterable, and so it will be performed in two passes
    #First get the image and copy it
    image = Image.open(filename)
    width = image.size[0]
    height = image.size[1]
    output_image = image.copy()