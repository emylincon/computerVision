import time
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import cvzone
from PIL import Image, ImageDraw
import face_recognition

frame_size = {'height': 480, 'width': 640}
cap = cv2.VideoCapture(0)
cap.set(3, frame_size['width'])
cap.set(4, frame_size['height'])


class Makeup:
    def __init__(self):
        self.mustache = "images/mustache.png"
        self.bow_tie = "images/bow_tie.png"

    @staticmethod
    def ResizeWithAspectRatio(image, width=None, height=None, inter=cv2.INTER_AREA):
        dim = None
        (h, w) = image.shape[:2]

        if width is None and height is None:
            return image
        if width is None:
            r = height / float(h)
            dim = (int(w * r), height)
        else:
            r = width / float(w)
            dim = (width, int(h * r))

        return cv2.resize(image, dim, interpolation=inter)

    def bow_tie_coordinates(self, face):
        mid_top = max(face["chin"], key=lambda v: v[1])
        lip_bot = max(face["bottom_lip"], key=lambda v: v[1])
        height = mid_top[1] - lip_bot[1]
        center = (mid_top[0], mid_top[1] + height // 2)
        return center

    @staticmethod
    def put_image(image, position, width, overlay):
        new_image = cv2.imread(overlay, cv2.IMREAD_UNCHANGED)
        new_image = Makeup.ResizeWithAspectRatio(new_image, width=width)
        # img = Makeup.draw_circle(img, ox, oy)

        frame = cvzone.overlayPNG(image, new_image,
                                  [position[0] - new_image.shape[1] // 2, position[1] - new_image.shape[0] // 2])
        return frame

    def add_mustache(self, image):
        face_landmarks_list = face_recognition.face_landmarks(image)
        for face_landmarks in face_landmarks_list:
            # The face landmark detection model returns these features:
            #  - chin, left_eyebrow, right_eyebrow, nose_bridge, nose_tip, left_eye, right_eye, top_lip, bottom_lip
            a = len(face_landmarks["top_lip"])
            pos = face_landmarks["top_lip"][a // 4]
            # cv2.circle(image, pos, 20, (0, 255, 0))
            try:
                image = Makeup.put_image(image, pos, 350, self.mustache)
            except ValueError:
                print('mustache image outside frame')
        return image

    def add_bow_tie(self, image):
        face_landmarks_list = face_recognition.face_landmarks(image)
        for face_landmarks in face_landmarks_list:
            # The face landmark detection model returns these features:
            #  - chin, left_eyebrow, right_eyebrow, nose_bridge, nose_tip, left_eye, right_eye, top_lip, bottom_lip
            pos = self.bow_tie_coordinates(face_landmarks)
            try:
                image = Makeup.put_image(image, pos, 150, self.bow_tie)
            except ValueError:
                print('mustache image outside frame')
        return image

    def add_clip_art(self, image, arts):
        face_landmarks_list = face_recognition.face_landmarks(image)
        for face_landmarks in face_landmarks_list:
            # The face landmark detection model returns these features:
            #  - chin, left_eyebrow, right_eyebrow, nose_bridge, nose_tip, left_eye, right_eye, top_lip, bottom_lip
            if "mustache" in arts:
                a = len(face_landmarks["top_lip"])
                pos = face_landmarks["top_lip"][a // 4]
                # cv2.circle(image, pos, 20, (0, 255, 0))
                try:
                    image = Makeup.put_image(image, pos, 250, self.mustache)
                except ValueError:
                    print('mustache image outside frame')
            if "bow_tie" in arts:
                pos = self.bow_tie_coordinates(face_landmarks)
                try:
                    image = Makeup.put_image(image, pos, 150, self.bow_tie)
                except ValueError:
                    print('bow_tie image outside frame')
        return image


class Button:
    def __init__(self, pos, text, size=None):
        self.pos = pos
        self.text = text
        self.size = [85, 85] if size is None else size
        self.switch = 0

    @property
    def get_overlay(self):
        return f"images/{self.text}.png"

    def draw(self, image):
        cv2.rectangle(image, self.pos, (self.pos[0] + self.size[0], self.pos[1] + self.size[1]), (255, 0, 255),
                      cv2.FILLED)
        cv2.putText(img, self.text, (self.pos[0] + 20, self.pos[1] + 65), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 4)
        return image

    def get_coordinates(self):
        return (self.pos[0] - self.size[0] // 2, self.pos[1] - self.size[1] // 2), \
               (self.pos[0] + self.size[0] // 2, self.pos[1] + self.size[1] // 2)

    def draw1(self, image, width=85):
        position = self.pos
        new_image = cv2.imread(self.get_overlay, cv2.IMREAD_UNCHANGED)
        new_image = Makeup.ResizeWithAspectRatio(new_image, width=width)
        # img = Makeup.draw_circle(img, ox, oy)

        cvzone.cornerRect(image, (*self.pos, new_image.shape[1], new_image.shape[0]), 10, rt=0, colorC=(0, 0, 255))

        frame = cvzone.overlayPNG(image, new_image,
                                  [position[0], position[1]])
        return frame


class Menu:
    def __init__(self):
        self.mustache = "images/mustache.png"
        self.bow_tie = "images/bow_tie.png"
        self.raw_letters = ['bow_tie', 'mustache']
        self.letters = [Button(pos=self.get_pos(item=i), text=i) for i in self.raw_letters]
        self.pause = 0.15
        self.color = {'green': (0, 255, 0), 'red': (0, 0, 255), 'blue': (255, 0, 0)}

    def get_pos(self, item):
        pos = (frame_size['height'], (self.raw_letters.index(item) * 100) + 20)
        return pos

    def draw(self, image, my_hand, width=85):
        arts = []
        for button in self.letters:

            position = button.pos
            new_image = cv2.imread(button.get_overlay, cv2.IMREAD_UNCHANGED)
            new_image = Makeup.ResizeWithAspectRatio(new_image, width=width)
            x, y = button.get_coordinates()
            if my_hand:
                l, _, _ = detector.findDistance(my_hand[0]['lmList'][8], my_hand[0]['lmList'][12], image)
                if l < 35:
                    cursor = my_hand[0]['lmList'][8]
                    if x[0] < cursor[0] < y[0] and x[1] < cursor[1] < y[1]:
                        button.switch = button.switch ^ 1
                        time.sleep(self.pause)
            if button.switch == 0:
                color = self.color['red']
            else:
                arts.append(button.text)
                color = self.color['green']
            cvzone.cornerRect(image, (*button.pos, new_image.shape[1], new_image.shape[0]),
                              10, rt=0, colorC=color)

            image = cvzone.overlayPNG(image, new_image, [position[0], position[1]])
        image = self.draw_art(image=image, arts=arts)
        return image

    @staticmethod
    def draw_art(image, arts):
        return Makeup().add_clip_art(image=image, arts=arts)


detector = HandDetector(detectionCon=0.8)
menu = Menu()

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    hands, img = detector.findHands(img)
    img = menu.draw(img, my_hand=hands)

    cv2.imshow("Image", img)

    ch = cv2.waitKey(1)
    if ch & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
