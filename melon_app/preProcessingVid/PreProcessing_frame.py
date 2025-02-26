import cv2
import numpy as np
import time

from preProcessingVid import fuz_vid
from preProcessingVid import segment_roi_vid_frame
from preProcessingVid import sick_melon

def extract_rgb(roi):
	#img = cv2.cvtColor(roi, cv2.COLOR_RGB2BGR)
	#(B, G, R) =  cv2.split(roi.astype("float"))
	B = roi[:, :, 0]
	G = roi[:, :, 1]
	R = roi[:, :, 2]

	b = np.mean(B)
	g = np.mean(G)
	r = np.mean(R)
	# Norm process
	total = b+g+r
	
	b_norm = round(b/total*255)
	g_norm = round(g/total*255)
	r_norm = round(r/total*255)
	return b_norm, g_norm, r_norm

def put_text_on_melon(melon):

	roi_fin, masked_result = segment_roi_vid_frame.find_sample(melon)
	blobs = sick_melon.find_blob(roi_fin)
	b, g, r = extract_rgb(roi_fin)
	try:
		ind = fuz_vid.fuzzy_ripe_index(b, g, r)
		index = str(round(ind,  2))
	except:
		index = -1

	if float(index) > 0:
		if float(index) < 3.5:
			Ripness = "Under Ripe"
		elif float(index) >= 3.5 and float(index) < 6.5:
			Ripness = "About to Ripe"
		elif float(index) >= 6.5:
			Ripness = "Ripe"
	elif float(index) == -1:
		Ripness = "!!!!!!!"

	return Ripness, index, blobs, roi_fin, masked_result


def find_melon(cvNet,img):


	cvNet.setInput(cv2.dnn.blobFromImage(img, size=(480, 360), swapRB=True, crop=False))
	cvOut = cvNet.forward()

	rows = img.shape[0]
	cols = img.shape[1]


	try:
		for detection in cvOut[0,0,:,:]:
			score = float(detection[2])
			if score > 0.7:
				if detection[1] == 1:
					box = []
					print(detection[1])
					left = detection[3] * cols
					top = detection[4] * rows
					right = detection[5] * cols
					bottom = detection[6] * rows
					Confidence = str(round(detection[2], 5))
					identify_melon = 1
					melon = img[int(top):int(bottom), int(left):int(right)]
					box.append([int(left), int(top), int(right), int(bottom)])

					#print
					return melon, box
					
	except:
		melon = None
		box = []
		return melon, box
"""
"""
def final_step(cvNet, im):

	try:
		m, box = find_melon(cvNet, im)
		#x,h, y, w = box[0][0], box[0][1], box[0][2], box[0][3]

		rip, ind, b, roi_fin, masked_result = put_text_on_melon(m)

		cv2.imwrite("preProcessingVid/temp/masked_result.png",masked_result)
		cv2.imwrite("preProcessingVid/temp/roi_fin.png",roi_fin)
		#fin = cv2.rectangle(im,(x,h), (y, w), color= (0,0,0),thickness= 2)
		return rip, ind, b
	except:	
		rip, ind, b = 0, 0, 0
		return rip, ind, b


"""
cvNet = cv2.dnn.readNetFromTensorflow('ssd_melon_model_18853/frozen_inference_graph.pb'
										, 'ssd_melon_model_18853/graph_ori.pbtxt')

im = cv2.imread('test/R1.JPG')
img = cv2.resize(im, (480,360))

rip, ind, b, fin = final_step(img,cvNet)

print(rip, ind, b)

cv2.imshow("s", fin)

cv2.waitKey(0)
cv2.destroyAllWindows()

"""