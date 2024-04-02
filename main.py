from harvesters.core import Harvester
from harvesters.core import DeviceInfo
from harvesters.core import Component2DImage
from harvesters.util.pfnc import mono_location_formats
from PIL import Image 
import numpy as np
import cv2
import matplotlib.pyplot as plt
from ultralytics import YOLO
import supervision as sv

def white_balance(img):
    result = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l_channel, a, b = cv2.split(result)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl = clahe.apply(l_channel)
    limg = cv2.merge((cl,a,b))
    enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    # avg_a = np.average(result[:, :, 1])
    # avg_b = np.average(result[:, :, 2])
    # result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.1)
    # result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.1)
    # result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
    return enhanced_img

def to_gray(img):
    """
    Converts the input in grey levels
    Returns a one channel image
    """
    grey_img = np.zeros(cv2.GetSize(img), img.depth, 1)
    cv2.CvtColor(img, grey_img, cv2.CV_RGB2GRAY )
    
    return grey_img   
    
def grey_histogram(img, nBins=64):
    """
    Returns a one dimension histogram for the given image
    The image is expected to have one channel, 8 bits depth
    nBins can be defined between 1 and 255 
    """
    hist_size = [nBins]
    h_ranges = [0, 255]
    hist = cv2.CreateHist(hist_size , cv2.CV_HIST_ARRAY, [[0, 255]], 1)
    cv2.CalcHist([img], hist)

    return hist

def extract_bright(grey_img, histogram=False):
    """
    Extracts brightest part of the image.
    Expected to be the LEDs (provided that there is a dark background)
    Returns a Thresholded image
    histgram defines if we use the hist calculation to find the best margin
    """
    ## Searches for image maximum (brightest pixel)
    # We expect the LEDs to be brighter than the rest of the image
    [minVal, maxVal, minLoc, maxLoc] = cv2.MinMaxLoc(grey_img)
    print ("Brightest pixel val is %d" %(maxVal))
    
    #We retrieve only the brightest part of the image
    # Here is use a fixed margin (80%), but you can use hist to enhance this one    
    if 0:
        ## Histogram may be used to wisely define the margin
        # We expect a huge spike corresponding to the mean of the background
        # and another smaller spike of bright values (the LEDs)
        hist = grey_histogram(img, nBins=64)
        [hminValue, hmaxValue, hminIdx, hmaxIdx] = cv2.GetMinMaxHistValue(hist) 
        margin = 0# statistics to be calculated using hist data    
    else:  
        margin = 0.8
        
    thresh = int( maxVal * margin) # in pix value to be extracted
    print ("Threshold is defined as %d" %(thresh))

    thresh_img = cv2.CreateImage(cv2.GetSize(img), img.depth, 1)
    cv2.Threshold(grey_img, thresh_img , thresh, 255, cv2.CV_THRESH_BINARY)
    
    return thresh_img

def find_leds(thresh_img):
    """
    Given a binary image showing the brightest pixels in an image, 
    returns a result image, displaying found leds in a rectangle
    """
    contours = cv2.FindContours(thresh_img, 
                               cv2.CreateMemStorage(), 
                               mode=cv2.CV_RETR_EXTERNAL , 
                               method=cv2.CV_CHAIN_APPROX_NONE , 
                               offset=(0, 0))

    regions = []
    while contours:
        pts = [ pt for pt in contours ]
        x, y = zip(*pts)    
        min_x, min_y = min(x), min(y)
        width, height = max(x) - min_x + 1, max(y) - min_y + 1
        regions.append((min_x, min_y, width, height))
        contours = contours.h_next()

        out_img = cv2.CreateImage(cv2.GetSize(grey_img), 8, 3)
    for x,y,width,height in regions:
        pt1 = x,y
        pt2 = x+width,y+height
        color = (0,0,255,0)
        cv2.Rectangle(out_img, pt1, pt2, color, 2)

    return out_img, regions

def leds_positions(regions):
    """
    Function using the regions in input to calculate the position of found leds
    """
    centers = []
    for x, y, width, height in regions:
        centers.append( [x+ (width / 2),y + (height / 2)])

    return centers


h = Harvester()

h.add_file('C:\\Program Files\\MATRIX VISION\\mvIMPACT Acquire\\bin\\x64\\mvGenTLProducer.cti')
h.update()
ia = h.create(0)
print(dir(ia.remote_device.node_map))
print((ia.remote_device.node_map._get_nodes))
ia.remote_device.node_map.RGain.value = 260
ia.remote_device.node_map.GGain.value = 200
ia.remote_device.node_map.BGain.value = 300
ia.remote_device.node_map.Gain.value = 6

ia.remote_device.node_map.Saturation.value = 100
ia.remote_device.node_map.Contrast.value = 100
ia.remote_device.node_map.Height.value = 1080
ia.remote_device.node_map.Width.value = 1920

model = YOLO("yolov8n.pt")
model.to('cuda')
# ia.remote_device.node_map.PixelFormat.value = 'BayerGB8'
print(ia.remote_device.node_map.Gain.value)

print(dir(ia.remote_device.node_map))
ia.start()
while True:
    with ia.fetch() as buffer:


        component = buffer.payload.components[0]
        _2d = component.data.reshape(component.height, component.width, int(component.num_components_per_pixel))
        img = _2d
        img = cv2.cvtColor(img, cv2.COLOR_BayerGR2RGB)
        img = cv2.resize(img,(1600,900))

        grey_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(grey_img, (5, 5), 
                       cv2.BORDER_DEFAULT)
        ret,thresh1 = cv2.threshold(blur,127,255,cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(thresh1, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        # cv2.drawContours(img, contours, -1, (0,255,0), 3)
        # blank = np.zeros(thresh1.shape[:2], 
        #          dtype='uint8')
 
        # cv2.drawContours(blank, contours, -1, 
        #                 (255, 0, 0), 1)
        (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(blur)
        cv2.circle(img, maxLoc, 5, (255, 0, 0), 2)
        ci = 0
        prevM = cv2.moments(contours[0])
        prevCx = int(prevM['m10']/prevM['m00'])
        prevCy = int(prevM['m01']/prevM['m00'])
        lineSum = 0
        for i in contours:
            M = cv2.moments(i)
            if M['m00'] != 0:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                cv2.drawContours(img, [i], -1, (0, 255, 0), 2)
                cv2.circle(img, (cx, cy), 7, (0, 0, 255), -1)
                cv2.putText(img, str(ci), (cx - 20, cy - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                ci += 1
                if abs(prevCx - cx) < 800:
                    cv2.line(img, (prevCx, prevCy), (cx, cy), (0, 255, 0), thickness=3, lineType=8)
                    cv2.putText(img, str(abs(prevCx - cx)), (((prevCx + cx) // 2), cy - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                # cv2.line(img, (prevCx, prevCy), (cx, cy), (0, 255, 0), thickness=3, lineType=8)

                prevCx = cx
                prevCy = cy
                # print(f"x: {cx} y: {cy}")
            
        cv2.imshow('right',img)

        # img = white_balance(img)q
        # results = model.predict(img, imgsz=640, conf=0.5, stream=True, verbose=True, stream_buffer=False)
        # for result in results:
        #     detections = sv.Detections.from_ultralytics(result)
        #     bounding_box_annotator = sv.BoundingBoxAnnotator()
        #     label_annotator = sv.LabelAnnotator()

        #     labels = [
        #         model.model.names[class_id]
        #         for class_id
        #         in detections.class_id
        #     ]

        #     annotated_image = bounding_box_annotator.annotate(
        #         scene=img, detections=detections)
        #     annotated_image = label_annotator.annotate(
        #         scene=annotated_image, detections=detections, labels=labels)
        # cv2.imshow('right',annotated_image)
        # img = cv2.cvtColor(_2d, cv2.COLOR_BayerRG2BGR)
        
        # img = cv2.resize(img, (1920, 1080))
       
        # # balance_img = white_balance(img)
        # cv2.imshow('right',img)
        # cv2.waitKey(10)
        # payload = buffer.payload
        # component = payload.components[0]
        # data = component.data
        # data1 = data.astype(np.uint16)

        # result = np.zeros(data.size*2//3, np.uint16)
        # result[0::2] = ((data1[1::3] & 15) << 8) | data1[0::3]
        # result[1::2] = (data1[1::3] >> 4) | (data1[2::3] << 4)
        # bayer_im = np.reshape(result, (rows, cols))
        # bgr = cv2.cvtColor(bayer_im, cv2.COLOR_BayerBG2BGR)
        # cv2.imshow('bgr', bgr*16)
        # test!
        if cv2.waitKey(1) & 0xFF == ord('w'):
            ia.remote_device.node_map.WBOnce.execute()
        if cv2.waitKey(1) & 0xFF == ord('e'):
            ia.remote_device.node_map.ExposureAuto.value = 'On'
        if cv2.waitKey(1) & 0xFF == ord('r'):
            ia.remote_device.node_map.ExposureAuto.value = 'Off'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
# with ia.fetch() as buffer:
#     print(buffer)

#     component = buffer.payload.components[0]

#     _2d = component.data.reshape(component.height,component.width, int(component.num_components_per_pixel))
#     img = _2d
#     cv2.imwrite("savedImage.jpg", img) 
            # Do any processing on the image data here...
ia.stop()
ia.destroy()
h.reset()
