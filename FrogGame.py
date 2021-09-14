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


# https://www.youtube.com/watch?v=6400ShqS9BY

def bell():
    frequency = 1000
    duration = 100  # ms
    winsound.Beep(frequency=frequency, duration=duration)


class Fly:
    def __init__(self, pos, speed):
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

        return cv2.resize(image, dim, interpolation=inter)  # cv2.INTER_AREA

    def get_vertices(self):
        pos = (self.pos[0] - self.fly_image.shape[1] // 2, self.pos[1] - self.fly_image.shape[0] // 2)
        p1 = pos
        p2 = (pos[0] + self.fly_image.shape[0], pos[1])
        p3 = (pos[0] + self.fly_image.shape[0], pos[1] + self.fly_image.shape[1])
        p4 = (pos[0], pos[1] + self.fly_image.shape[1])
        return p1, p2, p3, p4

    def plot_vertices(self, image):
        for point in self.get_vertices():
            radius = 4
            image = cv2.circle(img=image, center=point, radius=radius, color=Color.red, thickness=2)
        return image

    def get_coordinates(self):
        w, h = self.fly_image.shape[0], self.fly_image.shape[1]
        off = 10
        # (self.pos[0] - self.offset, self.pos[1] + self.offset), (
        #             self.pos[0] + w + self.offset, self.pos[1] - h - self.offset)
        return (self.pos[0], self.pos[1]), (self.pos[0] + w, self.pos[1] - h)

    def my_position(self):
        (x1, y1), (x2, y2) = self.get_coordinates()
        return [x1, y2, x2, y1]

    def update_pos(self):
        x, y = self.pos[0] + random.randrange(self.speed), self.pos[1] + random.randrange(self.speed)

        xm, ym = [x - self.fly_image.shape[1] // 2, y - self.fly_image.shape[0] // 2]
        if xm + self.fly_image.shape[1] > frame_size['width']:
            x = abs(x - frame_size['width']) + self.fly_image.shape[1] // 2
        if ym + self.fly_image.shape[0] > frame_size['height']:
            y = abs(y - frame_size['height']) + self.fly_image.shape[0] // 2
        self.pos = (abs(x), abs(y))

    def put_image(self, image):
        self.update_pos()
        # image = self.plot_vertices(image)
        frame = cvzone.overlayPNG(image, self.fly_image,
                                  [self.pos[0] - self.fly_image.shape[1] // 2,
                                   self.pos[1] - self.fly_image.shape[0] // 2])

        return frame

    def draw(self, image):
        frame = cvzone.overlayPNG(image, self.fly_image,
                                  [self.pos[0] - self.fly_image.shape[1] // 2,
                                   self.pos[1] - self.fly_image.shape[0] // 2])
        return frame


class Flies:
    def __init__(self, speed=10, no_of_flies=3):
        self.speed = speed
        self.marked = None
        self.fly_sound = "images/fly_frog_game/fly-noise.wav"
        self.killed = 0
        self.no_of_flies = no_of_flies
        self.is_playing = False
        self.flies = [
            Fly((50 + random.randrange(frame_size['width']), 50 + random.randrange(frame_size['height'])), self.speed)
            for i in range(self.no_of_flies)]

    def refresh(self):
        self.killed = 0
        self.flies = [
            Fly((50 + random.randrange(frame_size['width']), 50 + random.randrange(frame_size['height'])), self.speed)
            for i in range(self.no_of_flies)]

    @staticmethod
    def is_point_in_rect(vertices, point):
        p1, p2, p3, p4 = vertices
        (x1, y1) = p1
        (x2, y2) = p2
        (x4, y4) = p4
        (x, y) = point
        p21 = (x2 - x1, y2 - y1)
        p41 = (x4 - x1, y4 - y1)

        p21magnitude_squared = p21[0] ** 2 + p21[1] ** 2
        p41magnitude_squared = p41[0] ** 2 + p41[1] ** 2

        p = (x - x1, y - y1)
        response = False

        if 0 <= p[0] * p21[0] + p[1] * p21[1] <= p21magnitude_squared:
            if 0 <= p[0] * p41[0] + p[1] * p41[1] <= p41magnitude_squared:
                response = True

        return response

    def check_image(self, my_hand, fly, image):
        def get_center(pos, obj):
            return [pos[0] + obj.shape[1] // 2, pos[1] + obj.shape[0] // 2]

        [x1, y2, x2, y1] = fly.my_position()
        x, y = (x1, y2), (x2, y1)
        if my_hand:
            l, _ = detector.findDistance(my_hand[0]['lmList'][8], my_hand[0]['lmList'][12])
            if l < 60:
                cursor = my_hand[0]['lmList'][8]
                if self.is_point_in_rect(vertices=fly.get_vertices(), point=cursor):
                    # print('Inside')
                    # print(f"a={x[0]}, b={cursor[0]}, c={y[0]}, d={x[1]}, e={cursor[1]}, f={y[1]}")
                    # if x[0] < cursor[0] < y[0] and x[1] < cursor[1] < y[1]:
                    # if x[0] < cursor[0] < y[0] and x[1] < cursor[1] < y[1]:
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
                    self.flies.remove(fly)
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
        # if self.is_playing is False:
        #     self.play_sound()
        # elif not self.is_playing.is_alive():
        #     self.play_sound()

        return image, fly_pos


class Frog:
    def __init__(self):
        self.frog_image_path = "images/fly_frog_game/frog.png"
        self.frog_sound = "images/fly_frog_game/bullfrog1.wav"
        self.frog_image = cv2.imread(self.frog_image_path, cv2.IMREAD_UNCHANGED)
        self.height = 200
        self.frog_image_small = Fly.ResizeWithAspectRatio(image=self.frog_image, height=self.height)
        self.pos = (5, frame_size['height'] - self.height)
        self.start = (self.pos[0] + round(self.frog_image_small.shape[0] * (4 / 6)), self.pos[1] + 20)
        self.points = []

    def fix_points(self, end_point):
        p1 = (self.start[0] + end_point[0]) // 2, (self.start[1] + end_point[1]) // 2
        p2 = (self.start[0] + p1[0]) // 2, (self.start[1] + p1[1]) // 2
        self.points = [end_point, p1, p2]

    def eat_animation(self, image):
        fly_pos = self.points.pop(0)
        image = cv2.line(image, self.start, fly_pos, Color.orange, 5)
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


class Level:
    def __init__(self):
        self.stage = 0
        self.stages = {1: {'speed': 10, 'number': 5}, 2: {'speed': 20, 'number': 8}, 3: {'speed': 40, 'number': 12}}

    def level_stage(self):
        self.stage += 1
        return self.stages[self.stage]


class Game:
    def __init__(self):
        self.level = Level()
        self.flies = Flies()
        self.frog = Frog()
        self.play_again = Button(pos=[round(frame_size['width'] / 2.2), 200], text="Play Again", scale=2, thickness=2,
                                 colorR=Color.black,
                                 offset=20,
                                 border=3, colorB=Color.white)
        self.display_play = None
        self.grass_path = 'images/fly_frog_game/grass2.png'
        self.grass = cv2.imread(self.grass_path, cv2.IMREAD_UNCHANGED)
        self.grass = Fly.ResizeWithAspectRatio(self.grass, width=frame_size['width'])
        self.grass_pos = (0, frame_size['height'] - self.grass.shape[0])
        self.target_pos = (random.randrange(200), random.randrange(200))

    def draw_target(self, frame):
        radius = 20
        frame = cv2.circle(img=frame, center=self.target_pos, radius=radius, color=Color.red, thickness=2)
        sv, ev = (self.target_pos[0], self.target_pos[1] - radius), (self.target_pos[0], self.target_pos[1] + radius)
        sh, eh = (self.target_pos[0] - radius, self.target_pos[1]), (self.target_pos[0] + radius, self.target_pos[1])
        frame = cv2.line(img=frame, pt1=sv, pt2=ev, color=Color.red, thickness=1)
        frame = cv2.line(img=frame, pt1=sh, pt2=eh, color=Color.red, thickness=1)
        return frame

    def target(self, my_hands, frame):
        if my_hands:
            self.target_pos = my_hands[0]['lmList'][8]
            frame = self.draw_target(frame)
        else:
            frame = self.draw_target(frame)
        return frame

    def hungry_meter(self, image):
        x1 = 250
        x2 = 1100
        y2 = 660  # 600
        bar_value = x1 + ((x2 - x1) // self.flies.no_of_flies) * self.flies.killed

        # progress
        score = round((self.flies.killed / self.flies.no_of_flies) * 100)
        if score < 35:
            color = Color.red
        elif score < 70:
            color = Color.orange
        else:
            color = Color.green
        y1 = 700  # frame_size['height'] - 80
        image = cv2.rectangle(image, (x1, y1), (bar_value, y2), color, cv2.FILLED)
        image = cv2.rectangle(image, (x1, y1), (x2, y2), Color.black, 5)
        per = f"Hungry Meter : {score}%"
        cv2.putText(image, per, (x1 + 20, y1 - 10), cv2.FONT_HERSHEY_PLAIN, 2, Color.white, 4)
        return image

    def draw_play_again(self, image, my_hands):
        if my_hands:
            [x1, y2, x2, y1] = self.play_again.my_position()
            x, y = (x1, y2), (x2, y1)
            cursor = my_hands[0]['lmList'][8]
            if x[0] < cursor[0] < y[0] and x[1] < cursor[1] < y[1]:
                self.play_again.colorR = Color.green
                fingers = detector.fingersUp(myHand=my_hands[0])
                if fingers == [1, 1, 0, 0, 0]:  # index, thumb are up
                    self.flies.refresh()
                    bell()
            else:
                self.play_again.colorR = Color.black
        image = self.play_again.putTextRect(image)
        return image

    def draw(self, image, my_hand):
        image = cvzone.overlayPNG(image, self.grass, self.grass_pos)
        image, fly_pos = self.flies.draw(image, my_hand)
        frame, pos = self.frog.draw(image, fly_pos)
        if pos:
            self.flies.marked.pos = pos
        frame = self.hungry_meter(frame)
        if self.flies.no_of_flies == self.flies.killed:
            frame = self.draw_play_again(frame, my_hand)
        # else:
        # frame = self.play_again.putTextRect(frame)
        frame = self.target(my_hands=my_hand, frame=frame)
        return frame


game = Game()

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    hands = detector.findHands(img, draw=False)
    img = game.draw(image=img, my_hand=hands)
    cv2.imshow("Game", img)

    ch = cv2.waitKey(1)
    if ch & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
