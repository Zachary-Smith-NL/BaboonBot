from PIL import Image

#Mean filter
def mean(filename, window):
    #The mean filter is separable and iterable, and so it will be performed in two passes
    #First get the image and copy it
    image = Image.open(filename)
    width = image.size[0]
    height = image.size[1]
    output_image = image.copy()

    w = window // 2
    new_pixel = [0,0,0]
    #Horizontal pass
    for x in range(width):
        #Create an array to store the values of the sums in
        sums = [0,0,0]

        for u in range(-w, w + 1):
            if u < 0:
                pixel = image.getpixel((x,0))
            else:
                pixel = image.getpixel((x,u))
            for i in range(3):
                sums[i] += pixel[i]

        for i in range(3):
            new_pixel[i] = int(sums[i] / (2 * w + 1))
        output_image.putpixel((x,0), (new_pixel[0], new_pixel[1], new_pixel[2]))

        #Iterating
        for y in range(1, height):
            #Set the bounds
            if y + w >= height:
                y_coord_1 = height - 1
            else:
                y_coord_1 = y + w
            if y - w - 1 < 0:
                y_coord_2 = 0
            else:
                y_coord_2 = y - w - 1

            # Now use the coordinates generated to get two pixels
            # The reason for this is outlined in the theory of iterability in kernels
            pixel1 = image.getpixel((x, y_coord_1))
            pixel2 = image.getpixel((x, y_coord_2))

            # Tally up the sums
            for i in range(3):
                sums[i] += pixel1[i] - pixel2[i]
                new_pixel[i] = int(sums[i] / (2 * w + 1))
            # Store the value in the output image
            output_image.putpixel((x, y), (new_pixel[0], new_pixel[1], new_pixel[2]))

    #Now doing the horizontal pass
    for y in range(height):
        #Creating an array to store the sums in
        sums = [0,0,0]
        for u in range(-w,w+1):
            if u < 0:
                pixel = image.getpixel((0,y))
            else:
                pixel = image.getpixel((u,y))
            for i in range(3):
                sums[i] += pixel[i]
        saved_pixel = output_image.getpixel((0,y))
        for i in range(3):
            divided = sums[i] / (2 * w + 1)
            new_pixel[i] = int((divided + saved_pixel[i]) / 2)
        output_image.putpixel((0,y), (new_pixel[0], new_pixel[1], new_pixel[2]))

        #Beginning to iterate
        for x in range(1, width):
            # If a pixel is out of bounds, set it to be the closest in bounds
            if x + w >= width:
                xCoord1 = width - 1
            else:
                xCoord1 = x + w
            if x - w - 1 < 0:
                xCoord2 = 0
            else:
                xCoord2 = x - w - 1
            # Getting the two pixels
            pixel1 = image.getpixel((xCoord1, y))
            pixel2 = image.getpixel((xCoord2, y))
            saved_pixel = output_image.getpixel((x,y))
            for i in range(3):
                sums[i] += pixel1[i] - pixel2[i]
                divided = sums[i] / (2 * w + 1)
                new_pixel[i] = int((divided + saved_pixel[i]) / 2)
            output_image.putpixel((x,y), (new_pixel[0], new_pixel[1], new_pixel[2]))
    
    output_image.save(filename)
    return filename