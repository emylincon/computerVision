import time
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import cvzone
from PIL import Image, ImageDraw


frame_options = [{'height': 240, 'width': 320}, {'height': 480, 'width': 640}, {'height': 720, 'width': 1280}]
frame_size = frame_options[2]
cap = cv2.VideoCapture(0)
cap.set(3, frame_size['width'])
cap.set(4, frame_size['height'])

detector = HandDetector(detectionCon=0.8)

# https://www.youtube.com/watch?v=8gPONnGIPgw&ab_channel=Murtaza%27sWorkshop-RoboticsandAI

class Button:
    def __init__(self, pos, text, scale=3, thickness=3, colorT=(255, 255, 255),
                 colorR=(255, 0, 255), font=cv2.FONT_HERSHEY_PLAIN,
                 offset=10, border=None, colorB=(0, 255, 0)):
        self.pos = pos
        self.text = text
        self.scale = scale
        self.thickness = thickness
        self.colorT = colorT
        self.colorR = colorR
        self.colorB = colorB
        self.font = font
        self.border = border
        self.offset = offset

    @property
    def size(self):
        (w, h), _ = cv2.getTextSize(self.text, self.font, self.scale, self.thickness)
        return w, h

    def get_coordinates(self):
        w, h = self.size
        return (self.pos[0] - self.offset, self.pos[1] + self.offset), (
            self.pos[0] + w + self.offset, self.pos[1] - h - self.offset)

    def my_position(self):
        (x1, y1), (x2, y2) = self.get_coordinates()
        return [x1, y2, x2, y1]

    def putTextRect(self, img):
        """
        Creates Text with Rectangle Background
        :param img: Image to put text rect on
        :param text: Text inside the rect
        :param pos: Starting position of the rect x1,y1
        :param scale: Scale of the text
        :param thickness: Thickness of the text
        :param colorT: Color of the Text
        :param colorR: Color of the Rectangle
        :param font: Font used. Must be cv2.FONT....
        :param offset: Clearance around the text
        :param border: Outline around the rect
        :param colorB: Color of the outline
        :return: image, rect (x1,y1,x2,y2)
        """
        x, y = self.get_coordinates()

        cv2.rectangle(img, x, y, self.colorR, cv2.FILLED)
        if self.border is not None:
            cv2.rectangle(img, x, y, self.colorB, self.border)
        cv2.putText(img, self.text, self.pos, self.font, self.scale, self.colorT, self.thickness)
        # [x1, y2, x2, y1]
        return img

class Mouse:
    def __init__(self):  # TODO
        self.points = [[]]

    @staticmethod
    def _draw(image, letter, rec_color=None):
        # cvzone.cornerRect(new_img, )
        rec_color = (255, 0, 255) if rec_color is None else rec_color
        cv2.rectangle(image, letter.pos, (letter.pos[0] + letter.size[0], letter.pos[1] + letter.size[1]),
                      rec_color, cv2.FILLED)
        cv2.putText(image, letter.text, (letter.pos[0] + 20, letter.pos[1] + 65), cv2.FONT_HERSHEY_PLAIN, 4,
                    (255, 255, 255), 4)

        return image

    def draw_line(self, image):
        color = (0, 0, 255)
        thickness = 3
        for array in self.points:
            if len(array) > 0:
                for i in range(len(array)-1):
                    start_point = array[i]
                    end_point = array[i+1]
                    image = cv2.line(image, start_point, end_point, color, thickness)
        return image

    def draw(self, image, my_hands):  # TODO
        if my_hands:
            index = my_hands[0]['lmList'][8]
            thumb = my_hands[0]['lmList'][4]
            if detector.fingersUp(myHand=my_hands[0]) == [1]*5 and self.points[-1] != []:
                self.points.append([])
            l, _, _ = detector.findDistance(index, thumb, image)
            if l < 37:
                if len(self.points[-1]) == 0:
                    self.points[-1] = [index, thumb]
                else:
                    self.points[-1].append(index)
        image = self.draw_line(image)
        return image


m = Mouse()

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    hands, img = detector.findHands(img)
    # img = cv2.resize(img, (0, 0), fx=2, fy=2)
    img = m.draw(img, hands)
    cv2.imshow("Image", img)

    ch = cv2.waitKey(1)
    if ch & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
