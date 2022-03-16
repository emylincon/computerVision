import cv2
from cvzone.HandTrackingModule import HandDetector
from FrogGame import Game
from Util import Button, Color
from VirtualQuestion import Menu


frame_options = [{'height': 240, 'width': 320}, {'height': 480, 'width': 640}, {'height': 720, 'width': 1280}]
frame_size = frame_options[2]


class DemoMenu:
    def __init__(self):
        self.game = Game()
        self.q_a_menu = Menu(detector_=detector)
        self.game_button = Button(pos=(100,100), text="Game")
        self.q_a_button = Button(pos=(100, 200), text="Quiz")
        self.button_list = [self.game_button, self.q_a_button]
        self.status = -1

    def draw_menu(self, image, my_hands):
        for i in range(2):
            button = self.button_list[i]
            if my_hands:
                [x1, y2, x2, y1] = button.my_position()
                x, y = (x1, y2), (x2, y1)
                cursor = my_hands[0]['lmList'][8]
                if x[0] < cursor[0] < y[0] and x[1] < cursor[1] < y[1]:
                    button.colorR = Color.green
                    fingers = detector.fingersUp(myHand=my_hands[0])
                    if fingers == [1, 1, 0, 0, 0]:  # index, thumb are up
                        self.status = i

                else:
                    button.colorR = Color.black
            image = button.putTextRect(image)
        return image

    def menu(self, image, my_hands):
        if self.status == -1:
            image = self.draw_menu(image, my_hands)
        elif self.status == 0:
            image = self.game.draw(image, my_hands)
        else:
            image = self.q_a_menu.draw(image, my_hands)
        return image


if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    cap.set(3, frame_size['width'])
    cap.set(4, frame_size['height'])

    detector = HandDetector(detectionCon=0.8)

    demo_menu = DemoMenu()

    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)

        hands = detector.findHands(img, draw=False)
        img = demo_menu.menu(image=img, my_hands=hands)
        cv2.imshow("Virtual Reality", img)

        ch = cv2.waitKey(1)
        if ch & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()