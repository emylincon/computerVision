import cv2
from cvzone.HandTrackingModule import HandDetector
import string
import numpy as np
import cvzone
import time

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(detectionCon=0.8)


class Button:
    def __init__(self, pos, text, size=None):
        self.pos = pos
        self.text = text
        self.size = [85, 85] if size is None else size

    def draw(self, image):
        cv2.rectangle(image, self.pos, (self.pos[0] + self.size[0], self.pos[1] + self.size[1]), (255, 0, 255),
                      cv2.FILLED)
        cv2.putText(img, self.text, (self.pos[0] + 20, self.pos[1] + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
        return image


class Alphabets:
    def __init__(self):
        self.raw_letters = string.ascii_uppercase + ",.;'1234567890"
        self.raw_letters = list(self.raw_letters) + ['<', '|', 'space']
        self.text = ""
        self.letters = [Button(pos=self.pos(i), text=i) if i != "space" else Button(pos=self.pos(i), text=i, size=(220, 85)) for i in self.raw_letters]

    def pos(self, alpha):
        row_count = 11  # no of letters in a row
        no = self.raw_letters.index(alpha)
        x = 100 * ((no%row_count)+1)
        y = 100 * ((no//row_count)+1)
        return (x,y)

    @staticmethod
    def _draw(image, letter, rec_color=None):
        # cvzone.cornerRect(new_img, )
        rec_color = (255, 0, 255) if rec_color is None else rec_color
        cv2.rectangle(image, letter.pos, (letter.pos[0] + letter.size[0], letter.pos[1] + letter.size[1]),
                      rec_color, cv2.FILLED)
        cv2.putText(image, letter.text, (letter.pos[0] + 20, letter.pos[1] + 65), cv2.FONT_HERSHEY_PLAIN, 4,
                    (255, 255, 255), 4)

        return image

    @staticmethod
    def _transparent(image, new_image):
        out = image.copy()
        alpha = 0.1
        mask = new_image.astype(bool)
        out[mask] = cv2.addWeighted(image, alpha, new_image, 1-alpha, 0)[mask]

        return out

    def text_display(self, image):
        cv2.rectangle(image, (100, 550), (1200, 650), (175, 0, 175),  cv2.FILLED)
        cv2.putText(image, self.text, (110, 600), cv2.FONT_HERSHEY_PLAIN, 4,
                    (255, 255, 255), 4)

        return image

    def write_letter(self, letter):
        if letter == 'space':
            letter = " "
        elif letter == "<":
            self.text = self.text[:len(self.text)-1]
            return
        elif letter == "|":
            self.text = ""
            return

        self.text = self.text + str(letter)

    def draw(self, image, myhands=None):
        # new_img = np.zeros_like(image, np.uint8)
        new_img = image
        for letter in self.letters:
            check = 0
            # check if finger is pointing at a letter
            if myhands:
                # print(hands)
                if letter.pos[0] < myhands[0]['lmList'][8][0] < letter.pos[0] + letter.size[0] and letter.pos[1] < myhands[0]['lmList'][8][1] < letter.pos[1] + letter.size[1]:
                    l, _, _ = detector.findDistance(myhands[0]['lmList'][8], myhands[0]['lmList'][12], image)
                    if l < 37:
                        new_img = self._draw(new_img, letter, rec_color=(0, 255, 0))
                        # print(letter.text)
                        self.write_letter(letter.text)
                        time.sleep(0.15)
                    else:
                        new_img = self._draw(new_img, letter, rec_color=(175, 0, 175))

                    # print(l)
                    check = 1

            if check == 0:
                new_img = self._draw(new_img, letter)
        image = self.text_display(image=image)
        # image = self._transparent(image=image, new_image=new_img)
        return image


# q = Button(pos=(100,100), text="Q")
myLetters = Alphabets()

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img)
    # imList, bboxInfo = detector.findPosition(img)
    # img = q.draw(img)
    img = myLetters.draw(img, myhands=hands)
    cv2.imshow("Image", img)

    ch = cv2.waitKey(1)
    if ch & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
