from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton
from pynput.keyboard import Key, Controller

chicken_color = (255, 204, 170)
blade_color = (194, 195, 199)

chicken_blade_offset = 50

right = [475]
left = [119]

play_range = range(50, 450)

kb = Controller()

play_interval = 80
kb_delay = 20

fbc_value = 1


class Pico8Player(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("PICO-8 Player")
		self.setGeometry(0, 0, 800, 600)
		
		self.auto_play = False
		
		# Main widget and layout
		main_widget = QWidget(self)
		self.setCentralWidget(main_widget)
		layout = QVBoxLayout(main_widget)
		
		self.web_view = QWebEngineView(self)
		self.web_view.setMinimumWidth(621)
		self.web_view.setMinimumHeight(640)
		with open('html_embed', 'r') as f:
			self.web_view.setHtml(f.read())
		self.web_view.repaint()
		
		layout.addWidget(self.web_view)
		
		play_button = QPushButton("Play Game", self)
		play_button.clicked.connect(self.play_game)
		layout.addWidget(play_button)
		
		self.timer = QTimer(self)
		self.timer.timeout.connect(self.read_pixels)
		self.timer.start(play_interval)
		
		self.pressed_key = False
		self.fbc = fbc_value
	
	def play_game(self):
		self.auto_play = not self.auto_play
		# print(f'Auto play: {self.auto_play}')
		self.web_view.setFocus()
	
	def read_pixels(self):
		pixmap = self.web_view.grab()
		qimage = pixmap.toImage()
		
		chicken_pos = ''
		chicken_y = 0
		
		for x in right:
			for y in play_range:
				color = QColor(qimage.pixel(x, y))
				if color.red() == chicken_color[0] and color.green() == chicken_color[1] and color.blue() == \
						chicken_color[2]:
					chicken_pos = 'right'
					chicken_y = y
					break
		if chicken_pos == '':
			for x in left:
				for y in play_range:
					color = QColor(qimage.pixel(x, y))
					if color.red() == chicken_color[0] and color.green() == chicken_color[1] and color.blue() == \
							chicken_color[2]:
						chicken_pos = 'left'
						chicken_y = y
						break
		
		closest_blade_right = 0
		closest_blade_left = 0
		
		for x in right:
			for dy in range(play_range.start, chicken_y - chicken_blade_offset):
				color = QColor(qimage.pixel(x, dy))
				if color.red() == blade_color[0] and color.green() == blade_color[1] and color.blue() == blade_color[2]:
					if dy > closest_blade_right:
						closest_blade_right = dy
			for x in left:
				for dy in range(play_range.start, chicken_y - chicken_blade_offset):
					color = QColor(qimage.pixel(x, dy))
					if color.red() == blade_color[0] and color.green() == blade_color[1] and color.blue() == \
							blade_color[2]:
						if dy > closest_blade_left:
							closest_blade_left = dy
		
		# print(f'Chicken pos: {self.chicken_pos} ({chicken_y}); Closest blade right: {closest_blade_right}; Closest blade left: {closest_blade_left}')
		
		if self.auto_play and chicken_pos != '' and not self.pressed_key:
			if chicken_pos == 'right' and closest_blade_right < closest_blade_left:
				k = Key.right
			elif chicken_pos == 'right' and closest_blade_right > closest_blade_left:
				k = Key.left
			elif chicken_pos == 'left' and closest_blade_left < closest_blade_right:
				k = Key.left
			else:
				k = Key.right
			self.simulate_keypress(k)
			self.pressed_key = True
			self.fbc = fbc_value
		elif self.auto_play and chicken_pos != '' and self.pressed_key:
			self.fbc -= 1
			if self.fbc == 0:
				self.pressed_key = False
	
	def simulate_keypress(self, k):
		kb.press(k)
		QTimer.singleShot(kb_delay, lambda: kb.release(k))
