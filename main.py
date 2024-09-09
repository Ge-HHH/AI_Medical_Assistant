import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLineEdit, QPushButton, QWidget, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
from bubble_message import TextMessage, ChatWidget, BubbleMessage, MessageType, Notice
from GPT import GptMsg
import time

class GPTWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, gpt_msg, user_message):
        super().__init__()
        self.gpt_msg = gpt_msg
        self.user_message = user_message

    def run(self):
        self.gpt_msg.send_msg(self.user_message)
        response = self.gpt_msg.msg
        self.finished.emit(response)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI Medical Assistant")
        self.setGeometry(100, 100, 600, 800)

        # Initialize GptMsg instance only once
        self.gpt_msg = GptMsg()

        # Set up the central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        # Initialize ChatWidget
        self.chat_widget = ChatWidget()
        self.layout.addWidget(self.chat_widget)

        # Create the input and send button area
        input_layout = QHBoxLayout()

        # Create the message input area
        self.user_input = QLineEdit(self)
        self.user_input.setPlaceholderText("Type your message here...")
        self.user_input.setStyleSheet(
            """
            QLineEdit {
                border-radius: 15px;
                padding: 10px;
                font-size: 16px;
                border: 1px solid #ccc;
            }
            """
        )
        input_layout.addWidget(self.user_input)

        # Capture return key press to send message
        self.user_input.returnPressed.connect(self.send_message)

        # Create the send button
        self.send_button = QPushButton("Send", self)
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setStyleSheet(
            """
            QPushButton {
                border-radius: 15px;
                padding: 10px 20px;
                font-size: 16px;
                background-color: #4CAF50;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            """
        )
        input_layout.addWidget(self.send_button)

        # Add the input layout to the main layout
        self.layout.addLayout(input_layout)

        # Track if GPT response is pending
        self.is_gpt_processing = False

        self.last_msg_time = None

        # Set up a timer that triggers every 0.5 seconds
        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.on_timer)
        self.timer_cnt = 0

    def send_message(self):
        if self.is_gpt_processing:
            return  # Do not allow sending another message while waiting for GPT response

        user_message = self.user_input.text()
        if user_message:
            # 5 minutes check
            if (self.last_msg_time is None) or (time.time() - self.last_msg_time > 300):
                # xxxx-xx-xx xx:xx
                time_str = time.strftime("%Y-%m-%d %H:%M", time.localtime())
                time_message = Notice(time_str)
                self.chat_widget.add_message_item(time_message)
                self.last_msg_time = time.time()

            self.add_message(user_message, is_send=True)
            self.user_input.clear()

            # Start a thread to handle GPT message generation
            self.is_gpt_processing = True
            self.gpt_worker = GPTWorker(self.gpt_msg, user_message)
            self.gpt_worker.finished.connect(self.display_gpt_response)
            self.gpt_worker.start()

            # Start the timer
            self.add_message("", is_send=False)
            self.timer_cnt = 0
            self.timer.start()

    def display_gpt_response(self, response):
        # self.add_message(response, is_send=False)
        self.chat_widget.set_last_item_text(response)
        self.is_gpt_processing = False

        # Stop the timer
        self.timer.stop()

    def add_message(self, message, is_send):
        bubble_message = BubbleMessage(message, is_send=is_send, Type=MessageType.Text, avatar='avatar_doctor.png' if not is_send else 'avatar_user.png')
        self.chat_widget.add_message_item(bubble_message)
        self.chat_widget.set_scroll_bar_last()

    def on_timer(self):
        # This function will be called every 0.5 seconds while waiting for the GPT response
        self.timer_cnt = (self.timer_cnt + 1) % 4
        if self.timer_cnt == 0:
            self.chat_widget.set_last_item_text("")
        elif self.timer_cnt == 1:
            self.chat_widget.set_last_item_text(".")
        elif self.timer_cnt == 2:
            self.chat_widget.set_last_item_text("..")
        else:
            self.chat_widget.set_last_item_text("...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
