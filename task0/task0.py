import cv2

img = cv2.imread('lena.png')
gaussianBlur = cv2.GaussianBlur(img, (5,5), 0)
blur = cv2.blur(gaussianBlur, (5,5))

h, w = img.shape[:2]
rotation_matrix = cv2.getRotationMatrix2D((w/2, h/2), 15, 1)
blurRot = cv2.warpAffine(blur, rotation_matrix, (w, h))

cv2.imshow('Result', blurRot)
cv2.waitKey(0)
cv2.imwrite('lena2.png', blurRot)
