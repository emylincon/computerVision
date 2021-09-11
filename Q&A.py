import time
import cv2
from cvzone.HandTrackingModule import HandDetector
import requests
import random
from urllib.parse import unquote
import winsound
import cvzone

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


class Menu:
    def __init__(self):
        self.page = 0
        self.options = {'level': 'Random'}
        self.start = Button(pos=[round(frame_size["width"] // 2.4), 100], text="Start Quiz", scale=2, thickness=2,
                            colorR=(0, 0, 0), offset=20)
        self.level_text = ['Difficulty Level?', '- Easy', '- Medium', '- Hard', '- Random']  #
        self.levels = self.button_list(self.level_text)
        self.number = ['How many Questions?', '- 3', '- 5', '- 10']
        self.number_buttons = self.button_list(self.number)
        self.category = {'Sports': 21, 'General Knowledge': 9, 'Maths': 19, 'Science & Nature': 17, 'History': 23,
                         'Computer Science': 18,
                         'Random': None, 'Geography': 22, 'Politics': 24, 'Celebrities': 26}
        self.category_buttons = self.category_list()
        self.review = 0
        self.color = {'green': (0, 255, 0), 'red': (0, 0, 255), 'blue': (255, 0, 0), 'white': (255, 255, 255),
                      'black': (0, 0, 0)}
        self.next = Button(pos=[round(frame_size["width"] // 1.2), 200], text="Next", scale=2, thickness=2,
                           colorR=self.color['blue'], offset=20, colorB=self.color['white'], border=3)
        self.choice = None
        self.question = None
        self.page_list = {1: self.levels, 2: self.category_buttons, 3: self.number_buttons}

    @staticmethod
    def button_list(text_list):
        return [Button(pos=[100, (i * 100) + 50], text=text_list[i], scale=2, thickness=2, colorR=(0, 0, 0), offset=20,
                       border=3, colorB=(255, 255, 255)) if i != 0 else Button(pos=[100, (i * 100) + 50],
                                                                               text=text_list[i], scale=2, thickness=2,
                                                                               colorR=(255, 255, 255), offset=20,
                                                                               border=3, colorB=(0, 0, 0),
                                                                               colorT=(0, 0, 0)) for i in
                range(len(text_list))]

    def category_list(self):
        text_list = list(self.category.keys())
        array = [Button(pos=self.pos(no=i, array=text_list), text=f"- {text_list[i]}", scale=2, thickness=2,
                        colorR=(0, 0, 0), offset=20,
                        border=3, colorB=(255, 255, 255)) for i in range(len(text_list))]
        array = [Button(pos=[100, 50], text="Question Category?", scale=2, thickness=2, colorR=(255, 255, 255),
                        offset=20,
                        border=3, colorT=(0, 0, 0), colorB=(0, 0, 0))] + array

        return array

    def pos(self, no, array):
        # row_count  # no of buttons in a row
        column_count = 5
        row_count = len(array) // column_count
        x = 100 + (300 * (no % row_count))
        y = 150 + (100 * (no // row_count))
        return [x, y]

    def draw_start(self, image, my_hands):
        if my_hands:
            # x, y = self.start.get_coordinates()
            [x1, y2, x2, y1] = self.start.my_position()
            x, y = (x1, y2), (x2, y1)
            cursor = my_hands[0]['lmList'][8]
            if x[0] < cursor[0] < y[0] and x[1] < cursor[1] < y[1]:
                self.start.colorR = (0, 255, 0)
                fingers = detector.fingersUp(myHand=my_hands[0])
                if fingers == [1, 1, 0, 0, 0]:  # index, thumb are up
                    self.page = 1
                    bell()

            else:
                self.start.colorR = (0, 0, 0)
        image = self.start.putTextRect(image)
        return image

    def draw_review(self, image, my_hands, button_list):
        image = button_list[0].putTextRect(image)
        for button in button_list[1:]:
            if self.choice == button.text[2:]:
                button.colorR = self.color['green']
            else:
                button.colorR = self.color['black']
            image = button.putTextRect(image)
        if my_hands:
            # x, y = self.start.get_coordinates()
            [x1, y2, x2, y1] = self.next.my_position()
            x, y = (x1, y2), (x2, y1)
            cursor = my_hands[0]['lmList'][8]
            if x[0] < cursor[0] < y[0] and x[1] < cursor[1] < y[1]:
                self.next.colorR = self.color['green']
                fingers = detector.fingersUp(myHand=my_hands[0])
                if fingers == [1, 1, 0, 0, 0]:  # index, thumb are up
                    self.review = 0
                    bell()
            else:
                self.next.colorR = self.color['blue']

        image = self.next.putTextRect(image)
        return image

    def draw_difficulty(self, image, my_hands):
        image = self.draw_pre_question(image=image, my_hands=my_hands, next_page=2, obj_list=self.levels,
                                       option_key='level')
        return image

    def draw_category(self, image, my_hands):
        image = self.draw_pre_question(image=image, my_hands=my_hands, next_page=3, obj_list=self.category_buttons,
                                       option_key='category')
        return image

    def draw_question_number(self, image, my_hands):
        image = self.draw_pre_question(image=image, my_hands=my_hands, next_page=4, obj_list=self.number_buttons,
                                       option_key='number')
        return image

    def draw_pre_question(self, image, my_hands, next_page, obj_list, option_key):
        image = obj_list[0].putTextRect(image)
        for button in obj_list[1:]:
            if my_hands:
                [x1, y2, x2, y1] = button.my_position()
                x, y = (x1, y2), (x2, y1)
                cursor = my_hands[0]['lmList'][8]
                if x[0] < cursor[0] < y[0] and x[1] < cursor[1] < y[1]:
                    button.colorR = (0, 255, 0)
                    fingers = detector.fingersUp(myHand=my_hands[0])
                    if fingers == [1, 1, 0, 0, 0]:  # index, thumb are up
                        self.page = next_page
                        self.review = 1
                        bell()
                        self.options[option_key] = button.text[2:]
                        self.choice = button.text[2:]

                else:
                    button.colorR = (0, 0, 0)
            image = button.putTextRect(image)
        return image

    def draw(self, image, my_hands):
        if self.review == 1:
            return self.draw_review(image, my_hands, self.page_list[self.page - 1])
        if self.page == 0:
            return self.draw_start(image, my_hands)
        elif self.page == 1:
            return self.draw_difficulty(image, my_hands)
        elif self.page == 2:
            return self.draw_category(image, my_hands)
        elif self.page == 3:
            return self.draw_question_number(image, my_hands)
        else:
            if self.question is None:
                self.question = Question(amount=int(self.options['number']), difficulty=self.options['level'],
                                         category=self.category[self.options['category']])
            image, self.page = self.question.draw(image=image, my_hand=my_hands)
            if self.page != 4:
                self.question = None
            return image


class Question:
    def __init__(self, amount=10, difficulty='random', category=None):
        self.amount = amount
        self.difficulty = difficulty.lower()
        self.category = category
        self.url = self.get_url()
        self.correct = 0
        self.ques_id = 0
        self.questions = self.get_question()
        self.page = 4
        self.review = 0
        self.color = {'green': (0, 255, 0), 'red': (0, 0, 255), 'blue': (255, 0, 0), 'white': (255, 255, 255),
                      'black': (0, 0, 0)}
        self.next = Button(pos=[round(frame_size["width"] // 1.2), 200], text="Next", scale=2, thickness=2,
                           colorR=(255, 0, 0), offset=20, colorB=self.color['white'], border=2)
        self.current_display = self.button_list(text_list=self.questions[self.ques_id]['options'])

    def score(self):
        return round((self.correct / self.amount) * 100)

    def button_list(self, text_list):
        return [Button(pos=[100, (i * 100) + 50], text=unquote(text_list[i]), scale=1, thickness=2,
                       colorR=self.color['black'], offset=20,
                       border=3,
                       colorB=self.color['white']) if i != 0 else Button(pos=[100, (i * 100) + 50],
                                                                         text=unquote(text_list[i]), scale=1,
                                                                         thickness=2,
                                                                         colorR=self.color['white'], offset=20,
                                                                         border=3, colorT=self.color['black'],
                                                                         colorB=self.color['black']) for i in
                range(len(text_list))]

    def get_url(self):
        if self.difficulty == 'random':
            return f"https://opentdb.com/api.php?amount={self.amount}&{self.get_category()}encode=url3986"
        else:
            return f"https://opentdb.com/api.php?amount={self.amount}&{self.get_category()}difficulty={self.difficulty}&encode=url3986"

    def get_category(self):
        # https://opentdb.com/api.php?amount=10&category=23&difficulty=easy&encode=url3986
        if self.category is None:
            return ''
        else:
            return f"category={self.category}&"

    def get_question(self):
        response = requests.get(self.url)
        res_string = response.json()
        question = res_string  # eval(unquote(str(res_string)))
        for i in range(len(question['results'])):
            options = [*question['results'][i]['incorrect_answers'], question['results'][i]['correct_answer']]
            random.shuffle(options)
            question['results'][i]['options'] = [question['results'][i]['question']] + options
        return question['results']

    def draw_review(self, image, my_hands):
        image = self.current_display[0].putTextRect(image)
        for button in self.current_display[1:]:
            if unquote(self.questions[self.ques_id - 1]['correct_answer']) == button.text:
                button.colorR = self.color['green']
            else:
                button.colorR = self.color['red']
            image = button.putTextRect(image)
        if my_hands:
            # x, y = self.start.get_coordinates()
            [x1, y2, x2, y1] = self.next.my_position()
            x, y = (x1, y2), (x2, y1)
            cursor = my_hands[0]['lmList'][8]
            if x[0] < cursor[0] < y[0] and x[1] < cursor[1] < y[1]:
                self.next.colorR = self.color['green']
                fingers = detector.fingersUp(myHand=my_hands[0])
                if fingers == [1, 1, 0, 0, 0]:  # index, thumb are up
                    self.review = 0
                    self.update_current_display()
                    bell()
            else:
                self.next.colorR = self.color['blue']

        image = self.next.putTextRect(image)
        image = self.progress_bar(image)
        return image

    def update_current_display(self):
        if self.ques_id < self.amount:
            self.current_display = self.button_list(text_list=self.questions[self.ques_id]['options'])

    def draw_question(self, image, my_hands, obj_list):
        image = obj_list[0].putTextRect(image)
        for button in obj_list[1:]:
            if my_hands:
                [x1, y2, x2, y1] = button.my_position()
                x, y = (x1, y2), (x2, y1)
                cursor = my_hands[0]['lmList'][8]
                if x[0] < cursor[0] < y[0] and x[1] < cursor[1] < y[1]:
                    button.colorR = (0, 255, 0)
                    fingers = detector.fingersUp(myHand=my_hands[0])
                    if fingers == [1, 1, 0, 0, 0]:  # index, thumb are up
                        if unquote(self.questions[self.ques_id]['correct_answer']) == button.text:
                            self.correct += 1
                        self.ques_id += 1
                        self.review = 1
                        bell()
                        time.sleep(0.2)
                else:
                    button.colorR = (0, 0, 0)
            image = button.putTextRect(image)
        image = self.progress_bar(image)
        return image

    def progress_bar(self, image):
        bar_value = 150 + (950 // self.amount) * self.ques_id

        # progress
        y1 = 550
        image = cv2.rectangle(image, (150, y1), (bar_value, 600), self.color['green'], cv2.FILLED)
        image = cv2.rectangle(image, (150, y1), (1100, 600), self.color['black'], 5)
        per = f"Progress : {round((self.ques_id / self.amount) * 100)}%"
        cv2.putText(image, per, (150 + 20, y1 + 33), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 4)
        # image, _ = cvzone.putTextRect(image, per, [1130, 635], 2, 2, offset=20, border=5, colorB=white, colorR=black)

        # score
        y2 = 650
        bar_value = 150 + (950 // self.amount) * self.correct
        image = cv2.rectangle(image, (150, y2), (bar_value, 700), self.color['green'], cv2.FILLED)
        image = cv2.rectangle(image, (150, y2), (1100, 700), self.color['black'], 5)
        per = f"Score : {self.score()}%"
        cv2.putText(image, per, (150 + 20, y2 + 33), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 4)
        return image

    def completed(self, image, my_hands):
        image, _ = cvzone.putTextRect(image, "Quiz Completed", [250, 300], 2, 2, offset=20, border=5,
                                      colorB=self.color['white'],
                                      colorR=self.color['black'])
        image, bbox = cvzone.putTextRect(image, "Go To Start", [700, 300], 2, 2, offset=20, border=5,
                                         colorB=self.color['white'],
                                         colorR=self.color['black'])
        if my_hands:
            [x1, y2, x2, y1] = bbox
            x, y = (x1, y2), (x2, y1)
            cursor = my_hands[0]['lmList'][8]
            if x[0] < cursor[0] < y[0] and x[1] < cursor[1] < y[1]:
                image, bbox = cvzone.putTextRect(image, "Go To Start", [700, 300], 2, 2, offset=20, border=5,
                                                 colorB=self.color['white'],
                                                 colorR=self.color['green'])
                fingers = detector.fingersUp(myHand=my_hands[0])
                if fingers == [1, 1, 0, 0, 0]:  # index, thumb are up
                    self.page = 0
                    bell()
        image = self.progress_bar(image)
        return image

    def draw(self, image, my_hand):
        if self.review == 1:
            return self.draw_review(image=image, my_hands=my_hand), self.page
        elif self.ques_id < self.amount:
            return self.draw_question(image=image, my_hands=my_hand, obj_list=self.current_display), self.page
        else:
            image = self.completed(image, my_hand)
            return image, self.page


menu = Menu()

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    hands, img = detector.findHands(img)
    img = menu.draw(img, hands)
    cv2.imshow("Virtual Q&A", img)

    ch = cv2.waitKey(1)
    if ch & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
