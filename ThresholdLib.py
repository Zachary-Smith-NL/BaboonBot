from PIL import Image

class Thresholding:

    @staticmethod
    def global_threshold(threshold = [], filename = None):
        if(filename == None or len(threshold) != 3):
            return #Raise an exception later
        
        image = Image.open(filename)
        width = image.size[0]
        height = image.size[1]
        output_image = image.copy()

        for x in range(width):
            for y in range(height):
                pixel = image.getpixel((x,y))
                output_image.setpixel((x,y), Thresholding.threshold_pixel(threshold, pixel))
        return output_image

    @staticmethod
    def adaptive_mean_C(filename = None, window = 7, offset = 10):
        if(filename == None):
            return
        image = Image.open(filename)
        width = image.size[0]
        height = image.size[1]
        threshold = [0,0,0]
        w = window // 2
        output_image = image.copy()

        #Getting the mean of an image is both separable, and iterable
        #Therefore, the adaptive mean-C thresholding is also separable and iterable
        #So it will be done in two passes

        #Vertical pass
        for x in range(width):
            #Initialize an array to store the sums of the red (0), green (1), and blue (2) channels
            rgb_sums = [0,0,0]

            #Load in values to calculate an initial mean so that the pixels at the edge of the image can be calculated
            #Pixels outside the image are treated to have the same values as the closest inside pixel
            for u in range(-w, w + 1):
                if(u < 0):
                    pixel = image.getpixel((x,0))
                else:
                    pixel = image.getpixel((x,u))
                for i in range(3):
                    rgb_sums[i] += pixel[i]
            
            #Get the mean for the first pixel in each column before starting the main iterability loop
            new_pixel = [0,0,0]
            for i in range(3):
                new_pixel[i] = rgb_sums[i] / 2 * w + 1
            output_image.putpixel((x,0), (int(new_pixel[0]), int(new_pixel[1]), int(new_pixel[2])))

            #Now starting the iterability loop
            #Starts at 1 because 0 was just done
            for y in range(1, height):
                #If a pixel is out of bounds, set it to be the closest in-bounds
                if(y + w >= height):
                    y_coord_1 = height - 1
                else:
                    y_coord_1 = y + w
                if(y - w - 1 < 0):
                    y_coord_2 = 0
                else:
                    y_coord_2 = y - w - 1
                #Now use the coordinates generated to get two pixels
                #The reason for this is outlined in the theory of iterability in kernels
                pixel1 = image.getpixel((x,y_coord_1))
                pixel2 = image.getpixel((x,y_coord_2))

                #Tally up the sums
                for i in range(3):
                    rgb_sums[i] += (pixel1[i] - pixel2[i])
                    new_pixel[i] = rgb_sums[i] / (2 * w + 1)
                #Store the value in the output image
                output_image.putpixel((x,y), (int(new_pixel[0]), int(new_pixel[1]), int(new_pixel[2])))
        
        #Now begin the horizontal filter
        for y in range(height):
            #Again, init an array for the rgb_sums
            rgb_sums = [0,0,0]

            #And again, read in initial values for the boundary pixels
            for u in range(-w, w + 1):
                if(u < 0):
                    pixel = image.getpixel((0,y))
                else:
                    pixel = image.getpixel((u,y))
                for i in range(3):
                    rgb_sums[i] += pixel[i]
            #Since this is the final pass, we can now begin to actually finalize the changes in the output image
            #Same as before, perform this first for the 0th pixel in the row
            storedPixel = output_image.getpixel((0,y))
            for i in range(3):
                threshold[i] = int((((rgb_sums[i] / (2 * w + 1)) + storedPixel[i]) / 2) - offset)
            new_pixel = Thresholding.threshold_pixel(threshold, image.getpixel((0,y)))
            output_image.putpixel((0,y), new_pixel)

            #Now begin the iteration
            #Once again, start at 1 since the 0th pixel has been done
            for x in range(1, width):
                #If a pixel is out of bounds, set it to be the closest in bounds
                if(x + w >= width):
                    xCoord1 = width - 1
                else:
                    xCoord1 = x + w
                if(x - w - 1 < 0):
                    xCoord2 = 0
                else:
                    xCoord2 = x - w - 1
                #Getting the two pixels
                pixel1 = image.getpixel((xCoord1, y))
                pixel2 = image.getpixel((xCoord2, y))
                
                storedPixel = output_image.getpixel((x,y))
                for i in range(3):
                    rgb_sums[i] += (pixel1[i] - pixel2[i])
                    threshold[i] = int((((rgb_sums[i] / (2 * w + 1)) + storedPixel[i]) / 2) - offset)
                new_pixel = Thresholding.threshold_pixel(threshold, image.getpixel((x,y)))
                output_image.putpixel((x,y), new_pixel)
        output_image.save(filename)
        return filename


    @staticmethod
    def threshold_pixel(threshold, pixel):
        if(len(pixel) != 3):
            return (0,0,0)
        new_pixel = [0,0,0]
        for i in range(3):
            if pixel[i] > threshold[i]:
                new_pixel[i] = 255
            elif pixel[i] < threshold[i]:
                new_pixel[i] = 0
        return (new_pixel[0], new_pixel[1] , new_pixel[2])