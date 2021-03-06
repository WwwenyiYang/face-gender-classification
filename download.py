import urllib
import os
import logging
# this line is crucial to fix imread as PIL is not being maintained anymore
import PIL as pillow
from scipy.misc import imread
from scipy.misc import imresize
from pylab import imsave

logger = logging.getLogger(__name__)

def timeout(func, args=(), kwargs={}, timeout_duration=1, default=None):
    '''From:
    http://code.activestate.com/recipes/473878-timeout-function-using-threading/'''
    import threading
    class InterruptableThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.result = None

        def run(self):
            try:
                self.result = func(*args, **kwargs)
            except:
                self.result = default

    it = InterruptableThread()
    it.start()
    it.join(timeout_duration)
    if it.isAlive():
        return False
    else:
        return it.result

testfile = urllib.URLopener()

def rgb2gray(rgb):
    '''Return the grayscale version of the RGB image rgb as a 2D numpy array
    whose range is 0..1
    Arguments:
    rgb -- an RGB image, represented as a numpy array of size n x m x 3. The
    range of the values is 0..255'''
    
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b

    return gray/255.
        
def get_crop_pictures(list, act):
    
    for a in act:
        name = a.split()[1].lower()
        i = 0
        for line in open(list):
            if a in line:
                filename = name + str(i) + '.' + line.split()[4].split('.')[-1]
                # timeout is used to stop downloading images which take too long to download
                timeout(testfile.retrieve, (line.split()[4], "dataset/uncropped/" + filename), {}, 30)
                                
                # check if picture was copied
                if not os.path.isfile("dataset/uncropped/" + filename):
                    continue
                    
                url = line.split()[4]
                # check if image is valid
                try:
                    im = imread("dataset/uncropped/" + filename)
                except IOError:
                    logger.warn("Image from {} is corrupted".format(url))
                    continue
                    
                
                # retrieve bounded box coordinates
                x1 = int(line.split()[5].split(",")[0])
                y1 = int(line.split()[5].split(",")[1])
                x2 = int(line.split()[5].split(",")[2])
                y2 = int(line.split()[5].split(",")[3])
                
                # check if pictures are already gray-scale (2D)
                
                try:
                    im = im[y1:y2, x1:x2, :]
                
                except IndexError:
                    try:
                        im = im[y1:y2, x1:x2]
                    except IndexError:
                        logger.warn("Image from {} either does not exist ".format(url))
                        print(y1, y2, x1, x2)
                        continue
                    else:
                        logger.info("Image from {} is already gray-scaled".format(url))
                        logger.info("Copied {} from {}".format(filename, url))
                        im = imresize(im, (32,32)) #add 3
                        imsave("dataset/cropped/" + filename, im)
                        i += 1
                        continue
                    
                # check if picture is blank (has no pixels)
                try:     
                    im = imresize(im, (32,32)) 
                except IOError:
                    logger.warn("Image from {} is blank".format(url))
                    continue
                # except ValueError:  
                #     logger.warn("There is no image on {}".format(url)) 
                #     continue
                    
                logger.info("Copied {} from {}".format(filename, url))   
                    
                im = rgb2gray(im)
                im = imresize(im, (32,32)) #add 3
                imsave("dataset/cropped/" + filename, im)
                
                i += 1

    return