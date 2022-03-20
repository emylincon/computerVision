import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import cvzone

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(detectionCon=0.8)


class Box:
    def __init__(self, pos=None, size=None):
        self.pos = (100, 100) if pos is None else pos
        self.size = (100, 100) if size is None else size

    def get_coordinates(self):
        return (self.pos[0]-self.size[0]//2, self.pos[1]-self.size[1]//2), \
               (self.pos[0]+self.size[0]//2, self.pos[1]+self.size[1]//2)

    def draw(self, image, my_hand):
        color = (255, 0, 255)   # (175, 0, 175)
        x,y = self.get_coordinates()
        if my_hand:
            l, _, _ = detector.findDistance(my_hand[0]['lmList'][8], my_hand[0]['lmList'][12], image)
            if l < 35:
                cursor = my_hand[0]['lmList'][8]
                if x[0] < cursor[0] < y[0] and x[1] < cursor[1] < y[1]:
                    color = (0, 255, 0)
                    self.pos = cursor
                    x, y = self.get_coordinates()

        cv2.rectangle(image, x, y, color,  cv2.FILLED)

        return image


class Boxes:
    def __init__(self):
        self.box_list = [Box(pos=(100*i, 100)) for i in range(1,6)]

    def draw(self, image, my_hand):
        for each_box in self.box_list:
            color = (255, 0, 255)  # (175, 0, 175)
            x, y = each_box.get_coordinates()
            if my_hand:
                l, _, _ = detector.findDistance(my_hand[0]['lmList'][8], my_hand[0]['lmList'][12], image)
                if l < 35:
                    cursor = my_hand[0]['lmList'][8]
                    if x[0] < cursor[0] < y[0] and x[1] < cursor[1] < y[1]:
                        color = (0, 255, 0)
                        each_box.pos = cursor
                        x, y = each_box.get_coordinates()

            cv2.rectangle(image, x, y, color, cv2.FILLED)
            cvzone.cornerRect(image, (*x, *each_box.size), 30, rt=0)
        return image

    def draw_transparent(self, image, my_hand):
        img_new = np.zeros_like(img, np.uint8)
        for each_box in self.box_list:
            color = (255, 0, 255)  # (175, 0, 175)
            x, y = each_box.get_coordinates()
            if my_hand:
                l, _, _ = detector.findDistance(my_hand[0]['lmList'][8], my_hand[0]['lmList'][12], image)
                if l < 35:
                    cursor = my_hand[0]['lmList'][8]
                    if x[0] < cursor[0] < y[0] and x[1] < cursor[1] < y[1]:
                        color = (0, 255, 0)
                        each_box.pos = cursor
                        x, y = each_box.get_coordinates()

            cv2.rectangle(img_new, x, y, color, cv2.FILLED)
            cvzone.cornerRect(img_new, (*x, *each_box.size), 30, rt=0)
        out = image.copy()
        alpha = 0.5
        mask = img_new.astype(bool)
        out[mask] = cv2.addWeighted(img, alpha, img_new, 1-alpha, 0)[mask]
        return out

# box = Box()
box_list = Boxes()

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img)
    img = box_list.draw_transparent(img, hands)
    cv2.imshow("Image", img)

    ch = cv2.waitKey(1)
    if ch & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()