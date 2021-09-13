from Pinyin2Hanzi import *
import pygame
import math
import string
import sys

pinYinLang = set()
for i in all_pinyin():
    for j in range(2, len(i) + 2):
        pinYinLang.add(i[0:j])
pinYinLang.add("")


class Textbox:
    def __init__(self, x, y, width):
        self.x = x
        self.y = y
        self.width = width
        self.height = 25
        self.font = pygame.font.SysFont("SimHei", 16)
        self.text = ""
        self.params = DefaultDagParams()
        self.page = 1
        self.state = 0
        self.caps = False
        self.char = ""
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.language = "Chinese"
        self.words = []
        self.bufferText = ""
        self.pinYin = ""
        self.text_surface = None
        self.bufferText_surface = None

    def draw(self, sc):
        self.pinYin = ""
        for index, word in enumerate(self.words, 1):
            self.pinYin += str(index) + word
        self.text_surface = self.font.render(self.text, True, (0, 0, 0))
        self.bufferText_surface = self.font.render(self.pinYin, True, (0, 0, 0))
        sc.blit(self.text_surface, (self.x + 2, self.y + 2.5))
        pygame.draw.rect(sc, (255, 0, 0), self.rect, 1)
        if self.bufferText != "":
            sc.blit(self.bufferText_surface, (self.x + 2, self.y - 22.5))

    def keyDown(self, key_num):
        try:
            # 删除键
            if key_num == pygame.K_BACKSPACE:
                if self.text[-1] not in string.ascii_letters:
                    if self.state == 0 and self.text != "":
                        self.text = self.text[:-1]
                    elif self.state == 1:
                        if len(self.bufferText) == 1:
                            self.bufferText = ""
                            self.state = 0
                        else:
                            self.bufferText = self.bufferText[:-1]
                            self.words = self._hz2py(self.bufferText)
                        self.text = self.text[:-1]
                else:
                    if self.text != "" and self.bufferText == "":
                        self.text = self.text[:-1]
                    elif self.bufferText != "" and len(self.bufferText) != 1:
                        self.bufferText = self.bufferText[:-1]
                        self.words = self._hz2py(self.bufferText)
                        self.text = self.text[:-1]
                    elif self.bufferText != "" and len(self.bufferText) == 1:
                        self.bufferText = ""
                        self.text = self.text[:-1]
                        self.state = 0
                return None
            # shift键
            if key_num in (pygame.K_RSHIFT, pygame.K_LSHIFT):
                if self.language == "Chinese":
                    self.language = "English"
                else:
                    self.language = "Chinese"
                return None
            # 选词
            if key_num in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5):
                self.text = self.text[:len(self.text) - len(self.bufferText)]
                self.bufferText = ""
                self.text += self.words[key_num - 49]
                self.state = 0
                return None
            # 空格键
            if key_num == pygame.K_EQUALS:
                if self.state == 0:
                    return None
                p = 1
                limit_page = 0
                while True:
                    da = dag(self.params, (self.bufferText,), path_num=5 * p)
                    if len(da) % 5 != 0:
                        limit_page += len(da)
                        break
                    p += 1
                if self.bufferText not in pinYinLang:
                    for p in all_pinyin():
                        if p.startswith(self.bufferText):
                            p = 1
                            while True:
                                da = dag(self.params, (self.bufferText,), path_num=5 * p)
                                if len(da) % 5 != 0:
                                    limit_page += len(da)
                                    break
                                p += 1
                limit_page = limit_page / 5
                if limit_page % 1 != 0:
                    limit_page = math.ceil(limit_page)
                if self.page != limit_page:
                    self.page += 1
                    self.words = self._hz2py(self.bufferText)
                return None
            if key_num == pygame.K_MINUS:
                if self.page != 1:
                    self.page -= 1
                    self.words = self._hz2py(self.bufferText)
                return None
            if key_num == pygame.K_SPACE:
                if self.state == 0:
                    self.text += " "
                else:
                    self.text = self.text[:len(self.text) - len(self.bufferText)]
                    self.text += self.words[0]
                    self.bufferText = ""
                    self.state = 0
                return None
            # 大/小写键
            if key_num == pygame.K_CAPSLOCK:
                self.caps = not self.caps
                return None
            self.char = chr(key_num)
            if self.caps:
                self.char = chr(key_num - 32)
                if self.char in string.ascii_uppercase:
                    self.text += chr(key_num - 32)
                    return None
            if self.language == "English":
                self.char = chr(key_num)
                if self.char in string.ascii_lowercase:
                    self.text += self.char
                    return None
            self.char = chr(key_num)
            if self.char in string.ascii_letters:
                self.bufferText += self.char
                self.page = 1
                self.words = self._hz2py(self.bufferText)
            else:
                return None
            self.state = 1
            self.text += self.char
        except (ValueError, IndexError):
            pass

    def _hz2py(self, pinyin):
        result = dag(self.params, (pinyin,), path_num=5 * self.page)
        if pinyin not in all_pinyin():
            for p in all_pinyin():
                if p.startswith(pinyin):
                    result += dag(self.params, (p,), path_num=5 * self.page)
        result = {p.path[0]: p.score for p in result}
        result = sorted(result.items(), key=lambda d: d[1], reverse=True)
        result = result[(self.page - 1) * 5:self.page * 5]
        data = [item[0] for item in result]
        return data


pygame.init()
screen = pygame.display.set_mode((700, 500))
textbox = Textbox(40, 40, 500)
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)
        elif event.type == pygame.KEYDOWN:
            if event.type == pygame.K_RETURN:
                print("回车测试", textbox.text)
            textbox.keyDown(event.key)
    screen.fill((255, 255, 255))
    textbox.draw(screen)
    pygame.display.update()
