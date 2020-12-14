from PIL import Image
import math

#Mean filter
def mean(image, window):
    #The mean filter is separable and iterable, and so it will be performed in two passes
    #First get the image and copy it
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
    
    return output_image

def triangle(image, window):
    #Separable, so done in two passes
    #Not iterable though
    width = image.size[0]
    height = image.size[1]
    output_image = image.copy()

    w = window // 2
    kernel = []
    counter = 1
    for i in range(-w, w + 1):
        if(i < 0):
            kernel.append(counter)
            counter += 1
        else:
            kernel.append(counter)
            counter -= 1
    kernel_sum = 0
    for i in range(len(kernel)):
        kernel_sum += kernel[i]
    #Horizontal pass
    for x in range(width):
        for y in range(height):
            #Create an array to store sums
            sums = [0,0,0]
            counter = 0
            for u in range(-w, w + 1):
                if y + u < 0:
                    yCoord = 0
                elif y + u >= height:
                    yCoord = height - 1
                else:
                    yCoord = y + u
                pixel = image.getpixel((x,yCoord))
                for i in range(3):
                    sums[i] += kernel[counter] * pixel[i]
                counter += 1
            for i in range(3):
                sums[i] /= kernel_sum
                sums[i] = int(sums[i])
            output_image.putpixel((x,y), (sums[0], sums[1], sums[2]))
    #Vertical pass
    for y in range(height):
        for x in range(width):
            #Sum array
            sums = [0,0,0]
            counter = 0
            for u in range(-w, w + 1):
                if x + u < 0:
                    xCoord = 0
                elif x + u >= width:
                    xCoord = width - 1
                else:
                    xCoord = x + u
                pixel = image.getpixel((xCoord,y))
                for i in range(3):
                    sums[i] += kernel[counter] * pixel[i]
                counter += 1
            saved_pixel = output_image.getpixel((x,y))
            for i in range(3):
                sums[i] /= kernel_sum
                sums[i] = int((sums[i] + saved_pixel[i]) / 2)
            output_image.putpixel((x,y), (sums[0], sums[1], sums[2]))
            return output_image

#Returns a 1D DoG kernel of desired size
def DoG(w, sigma):
    kernel = []
    for u in range(-w, w + 1):
        value = (-u / (math.sqrt(2 * math.pi) * pow(sigma, 3))) * (math.exp(-pow(u, 2) / (2 * pow(sigma,2))))
        kernel.append(value)
    return kernel

#Returns a 1D gaussian kernel of desired size
def gaussian_kernel(w, sigma):
    kernel = []
    for u in range(-w, w + 1):
        value = (1 / (math.sqrt(2 * math.pi) * sigma)) * (math.exp(-pow(u, 2) / (2 * pow(sigma,2))))
        kernel.append(value)
    return kernel

def gaussian(image, window, sigma, derivative = False):
    w = window // 2
    width = image.size[0]
    height = image.size[1]
    output_image = image.copy()
    #Allow selection of derivative of gaussian, or just normal gaussian
    #Derivative will only be called internally, so default to false
    if derivative:
        kernel = DoG(w, sigma)
    else:
        kernel = gaussian_kernel(w, sigma)
    #Storage for values, explained later
    storage = []
    #When using floating point calculation, it is separable, therefore do two passes
    #Horizontal
    for x in range(width):
        storage.append([])
        for y in range(height):
            storage[x].append([0,0,0])
            sums = [0,0,0]
            for u in range(-w, w + 1):
                if y + u < 0:
                    yCoord = 0
                elif y + u >= height:
                    yCoord = height - 1
                else:
                    yCoord = y + u
                pixel = image.getpixel((x,yCoord))
                for i in range(3):
                    #u + w should go from 0 -> 2 * w + 1
                    sums[i] += kernel[u + w] * pixel[i]
            for i in range(3):
                #Since using floating point calculation, cannot store the values in the image
                #Use an extra array to store these values instead
                storage[x][y][i] = sums[i]
    #Vertical
    for y in range(height):
        for x in range(width):
            sums = [0,0,0]
            for u in range(-w, w + 1):
                if x + u < 0:
                    xCoord = 0
                elif x + u >= width:
                    xCoord = width - 1
                else:
                    xCoord = x + u
                pixel = image.getpixel((xCoord,y))
                for i in range(3):
                    sums[i] += kernel[u + w] * pixel[i]
            new_pixel = [0,0,0]
            for i in range(3):
                new_pixel[i] = int((sums[i] + storage[x][y][i]) / 2)
            output_image.putpixel((x,y), (new_pixel[0], new_pixel[1], new_pixel[2]))
    return output_image