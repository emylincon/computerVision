import cv2
from Util import Button
from cvzone.HandTrackingModule import HandDetector
import random
from threading import Thread
from Util import Color
import cvzone
import winsound

frame_options = [{'height': 240, 'width': 320}, {'height': 480, 'width': 640}, {'height': 720, 'width': 1280}]
frame_size = frame_options[2]
cap = cv2.VideoCapture(0)
cap.set(3, frame_size['width'])
cap.set(4, frame_size['height'])

detector = HandDetector(detectionCon=0.8)
color = Color()

# https://www.youtube.com/watch?v=6400ShqS9BY

def bell():
    frequency = 1000
    duration = 100  # ms
    winsound.Beep(frequency=frequency, duration=duration)


class Fly:
    def __init__(self, pos, speed, fly_id):
        self.id = fly_id
        self.pos = pos
        self.speed = speed
        self.fly_image_path = "images/fly_frog_game/footer-fly.png"
        self.fly_image = cv2.imread(self.fly_image_path, cv2.IMREAD_UNCHANGED)

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

    def get_coordinates(self):
        w, h = self.fly_image.shape[0], self.fly_image.shape[1]
        return (self.pos[0], self.pos[1]), (self.pos[0] + w, self.pos[1] - h)

    def my_position(self):
        (x1, y1), (x2, y2) = self.get_coordinates()
        return [x1, y2, x2, y1]

    def update_pos(self):
        x, y = self.pos[0]+random.randrange(self.speed), self.pos[1]+random.randrange(self.speed)

        xm, ym = [x - self.fly_image.shape[1] // 2, y - self.fly_image.shape[0] // 2]
        if xm + self.fly_image.shape[1] > frame_size['width']:
            x = abs(x - frame_size['width']) + self.fly_image.shape[1] // 2
        if ym + self.fly_image.shape[0] > frame_size['height']:
            y = abs(y - frame_size['height']) + self.fly_image.shape[0] // 2
        self.pos = (abs(x), abs(y))

    def put_image(self, image):
        self.update_pos()

        frame = cvzone.overlayPNG(image, self.fly_image,
                                  [self.pos[0] - self.fly_image.shape[1] // 2, self.pos[1] - self.fly_image.shape[0] // 2])

        return frame

    def draw(self, image):
        frame = cvzone.overlayPNG(image, self.fly_image,
                                  [self.pos[0] - self.fly_image.shape[1] // 2, self.pos[1] - self.fly_image.shape[0] // 2])
        return frame


class Flies:
    def __init__(self):
        self.speed = 10
        self.marked = None
        self.fly_sound = "images/fly_frog_game/fly-noise.wav"
        self.killed = 0
        self.no_of_flies = 3
        self.is_playing = False
        self.flies = [Fly((50+random.randrange(frame_size['width']), 50+random.randrange(frame_size['height'])), 10, i) for i in range(self.no_of_flies)]

    def refresh(self):
        self.killed = 0
        self.flies = [Fly((50+random.randrange(frame_size['width']), 50+random.randrange(frame_size['height'])), 10, i) for i in range(self.no_of_flies)]

    def check_image(self, my_hand, fly, image):
        def get_center(pos, obj):
            return [pos[0] + obj.shape[1] // 2, pos[1] + obj.shape[0] // 2]
        [x1, y2, x2, y1] = fly.my_position()
        x, y = (x1, y2), (x2, y1)
        if my_hand:
            l, _, _ = detector.findDistance(my_hand[0]['lmList'][8], my_hand[0]['lmList'][12], image)
            if l < 50:
                cursor = my_hand[0]['lmList'][8]
                # print(f"a={x[0]}, b={cursor[0]}, c={y[0]}, d={x[1]}, e={cursor[1]}, f={y[1]}")
                if x[0] < cursor[0] < y[0] and x[1] < cursor[1] < y[1]:
                    # print('caught')
                    # color = (0, 255, 0)
                    # fly.pos = cursor
                    return get_center(fly.pos, fly.fly_image)

    def play_sound(self):
        def fly_play():
            winsound.PlaySound(self.fly_sound, winsound.SND_FILENAME)
        self.is_playing = Thread(target=fly_play)
        self.is_playing.start()

    def draw(self, image, my_hand):
        fly_pos = None
        for fly in self.flies:
            if fly == self.marked:
                if self.marked.pos == (-1, -1):
                    # print('deleted', len(self.flies))
                    self.flies.remove(fly)
                    # print('deleted', len(self.flies))
                    self.marked = None
                    self.killed += 1
                else:
                    image = fly.draw(image)
            else:
                image = fly.put_image(image)
            loc = self.check_image(my_hand=my_hand, fly=fly, image=image)
            if loc is not None:
                fly_pos = loc
                self.marked = fly
        if self.is_playing is False:
            self.play_sound()
        elif not self.is_playing.is_alive():
            self.play_sound()

        return image, fly_pos


class Frog:
    def __init__(self):
        self.frog_image_path = "images/fly_frog_game/frog.png"
        self.frog_sound = "images/fly_frog_game/bullfrog.wav"
        self.frog_image = cv2.imread(self.frog_image_path, cv2.IMREAD_UNCHANGED)
        self.height = 200
        self.frog_image_small = Fly.ResizeWithAspectRatio(image=self.frog_image, height=self.height)
        self.pos = (5, frame_size['height'] - self.height)
        self.start = (self.pos[0] + round(self.frog_image_small.shape[0]*(4/6)), self.pos[1]+20)
        self.points = []

    def fix_points(self, end_point):
        p1 = (self.start[0]+end_point[0])//2, (self.start[1] + end_point[1])//2
        p2 = (self.start[0] + p1[0]) // 2, (self.start[1] + p1[1]) // 2
        self.points = [end_point, p1, p2]

    def eat_animation(self, image):
        fly_pos = self.points.pop(0)
        image = cv2.line(image, self.start, fly_pos, color.orange, 5)
        return image

    def play_sound(self):
        def frog_play():
            winsound.PlaySound(self.frog_sound, winsound.SND_FILENAME)
        t1 = Thread(target=frog_play)
        t1.start()

    def draw(self, image, fly_pos=None):
        # print("fly:", fly_pos)
        pos = None
        if fly_pos is not None:
            self.fix_points(end_point=fly_pos)
        if len(self.points) > 0:
            image = self.eat_animation(image)
            if not self.points:
                pos = (-1, -1)
                self.play_sound()
            else:
                pos = self.points[0]
        frame = cvzone.overlayPNG(image, self.frog_image_small,
                                  [self.pos[0], self.pos[1]])
        return frame, pos


class Game:
    def __init__(self):
        self.flies = Flies()
        self.frog = Frog()
        self.play_again = Button(pos=[round(frame_size['width']/2.2), 200], text="Play Again", scale=2, thickness=2, colorR=color.black,
                            offset=20,
                            border=3, colorB=color.white)
        self.display_play = None

    def hungry_meter(self, image):
        x1 = 250
        x2 = 1100
        y2 = 600
        bar_value = x1 + ((x2-x1) // self.flies.no_of_flies) * self.flies.killed

        # progress
        y1 = frame_size['height'] - 80
        image = cv2.rectangle(image, (x1, y1), (bar_value, y2), color.green, cv2.FILLED)
        image = cv2.rectangle(image, (x1, y1), (x2, y2), color.black, 5)
        per = f"Hungry Meter : {round((self.flies.killed / self.flies.no_of_flies) * 100)}%"
        cv2.putText(image, per, (x1 + 20, y1 - 10), cv2.FONT_HERSHEY_PLAIN, 2, color.black, 4)
        return image

    def draw_play_again(self, image, my_hands):
        if my_hands:
            [x1, y2, x2, y1] = self.play_again.my_position()
            x, y = (x1, y2), (x2, y1)
            cursor = my_hands[0]['lmList'][8]
            if x[0] < cursor[0] < y[0] and x[1] < cursor[1] < y[1]:
                self.play_again.colorR = color.green
                fingers = detector.fingersUp(myHand=my_hands[0])
                if fingers == [1, 1, 0, 0, 0]:  # index, thumb are up
                    self.flies.refresh()
                    bell()
            else:
                self.play_again.colorR = color.black
        image = self.play_again.putTextRect(image)
        return image

    def draw(self, image, my_hand):
        image, fly_pos = self.flies.draw(image, my_hand)
        frame, pos = self.frog.draw(image, fly_pos)
        if pos:
            self.flies.marked.pos = pos
        frame = self.hungry_meter(frame)
        if self.flies.no_of_flies == self.flies.killed:
            frame = self.draw_play_again(frame, my_hand)
            # frame = self.play_again.putTextRect(frame)
        return frame


# fly = Fly((100, 100), 10)
# obj = Flies()
game = Game()

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    
    hands, img = detector.findHands(img)
    img = game.draw(image=img, my_hand=hands)
    cv2.imshow("Game", img)

    ch = cv2.waitKey(1)
    if ch & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()