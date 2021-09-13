import cv2


class Color:
    def __init__(self):
        self.green = (0, 255, 0)
        self.red = (0, 0, 255)
        self.blue = (255, 0, 0)
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.grey = (105, 105, 105)
        self.orange = (0, 165, 255)


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