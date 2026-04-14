import sys
import os
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QWidget, QStackedWidget,
    QLineEdit, QComboBox, QSlider, QDialog
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt
print(">>> MAIN FILE LOADED <<<")
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import Qt, QUrl, QPoint
from PyQt6.QtGui import QPixmap, QFont, QPainter, QColor, QPen, QBrush
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from PyQt6.QtCore import QPointF
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QPixmap
from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QGridLayout
from PyQt6.QtWidgets import QGridLayout, QWidget
import math
import time
import datetime
import json
import os
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QBrush
from abc import ABC, abstractmethod
import random
def resource_path(relative_path: str) -> str:
    """Корректный путь к ресурсам и для PyCharm, и для .exe."""
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)
class BasketLabel(QLabel):
    def __init__(self, text, color, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("border: 2px dashed #7f8c8d; background: rgba(0,0,0,40%); color: white;")
        self.color = color  # "red" или "green"

    def highlight(self, on: bool):
        if on:
            self.setStyleSheet("border: 3px solid #f1c40f; background: rgba(0,0,0,40%); color: white;")
        else:
            self.setStyleSheet("border: 2px dashed #7f8c8d; background: rgba(0,0,0,40%); color: white;")


class DraggableRoot(QLabel):
    def __init__(self, color: str, parent=None):
        super().__init__(parent)
        self.color = color  # "red" или "green"
        self.setFixedSize(50, 50)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)

        pix = QPixmap(self.size())
        pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix)
        if color == "red":
            p.setBrush(QBrush(QColor(192, 57, 43)))
        else:
            p.setBrush(QBrush(QColor(39, 174, 96)))
        p.setPen(QPen(Qt.GlobalColor.black, 2))
        p.drawEllipse(5, 5, 40, 40)
        p.end()
        self.setPixmap(pix)
        self.setScaledContents(True)

        self.dragging = False
        self.drag_offset = QPoint()
        self.placed = False

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.placed:
            self.dragging = True
            self.drag_offset = event.position().toPoint()
            self.raise_()
        # не вызываем super, чтобы событие не ушло наверх

    def mouseMoveEvent(self, event):
        if self.dragging and not self.placed:
            new_pos = self.mapToParent(event.position().toPoint() - self.drag_offset)
            self.move(new_pos)
        # не вызываем super

    def mouseReleaseEvent(self, event):
        if self.dragging and event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            main = self.window()
            if hasattr(main, "root_dropped_in_game"):
                main.root_dropped_in_game(self)
        # не вызываем super
# ---------- 1. Интерфейсы ----------

class ISaveable(ABC):
    @abstractmethod
    def save_to_file(self):
        pass


class IEntity(ABC):
    @abstractmethod
    def get_info(self):
        pass
class ICombatant(ABC):
    @abstractmethod
    def take_damage(self, amount: int):
        pass

    @abstractmethod
    def is_alive(self) -> bool:
        pass


# ---------- 2. Логика ----------

class Inventory:
    def __init__(self):
        self.gold = 0
        self.weapon = "Нет оружия"
        self.strength = 0
        self.weapon_image: Optional[str] = None
        self.algae = 0  # водоросли Водяного
        self.potion_image: Optional[str] = None



class GameSession(ISaveable):
    def __init__(self):
        self.player_name = "Герой"
        self.karma = 0
        self.hp = 5
        self.inventory = Inventory()
        self.theme = "light"
        self.language = "ru"

    def save_to_file(self):
        with open("save_game.txt", "w", encoding="utf-8") as f:
            f.write(f"{self.player_name};{self.karma};{self.inventory.gold}")

class PlayerCombatant(ICombatant):
    def __init__(self, game_session: GameSession):
        self.session = game_session  # тут лежит hp
        self.hp = self.session.hp

    def take_damage(self, amount: int):
        self.hp = max(0, self.hp - amount)
        self.session.hp = self.hp  # синхронизируем с сессией

    def is_alive(self) -> bool:
        return self.hp > 0


# ---------- 3. Главное меню ----------

class MainMenu(QWidget):
    def __init__(self, start_callback, exit_callback, open_settings_callback, open_lore_callback):
        super().__init__()

        self.start_callback = start_callback
        self.exit_callback = exit_callback
        self.open_settings_callback = open_settings_callback
        self.open_lore_callback = open_lore_callback

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title = QLabel()
        self.title.setFont(QFont("Georgia", 36, QFont.Weight.Bold))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.title)

        name_layout = QVBoxLayout()
        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.name_input = QLineEdit()
        self.name_input.setFixedWidth(250)
        self.name_input.setAlignment(Qt.AlignmentFlag.AlignCenter)

        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.name_input, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_start = QPushButton()
        self.btn_start.setFixedSize(220, 50)
        self.btn_start.clicked.connect(start_callback)
        name_layout.addWidget(self.btn_start, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addLayout(name_layout)

        self.btn_lore = QPushButton()
        self.btn_lore.setFixedSize(220, 40)
        self.btn_lore.clicked.connect(open_lore_callback)
        main_layout.addWidget(self.btn_lore, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_settings = QPushButton()
        self.btn_settings.setFixedSize(220, 40)
        self.btn_settings.clicked.connect(open_settings_callback)
        main_layout.addWidget(self.btn_settings, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_exit = QPushButton()
        self.btn_exit.setFixedSize(220, 40)
        self.btn_exit.clicked.connect(exit_callback)
        main_layout.addWidget(self.btn_exit, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)

        # по умолчанию русский
        self.set_language("ru")

    def set_language(self, lang: str):
        if lang == "en":
            self.title.setText("FAIRYTALE QUEST")
            self.name_label.setText("Hero's name:")
            self.name_input.setPlaceholderText("Enter your name...")
            self.btn_start.setText("PLAY")
            self.btn_lore.setText("CHARACTERS INFO")
            self.btn_settings.setText("SETTINGS")
            self.btn_exit.setText("EXIT")
        else:
            self.title.setText("СКАЗОЧНЫЙ КВЕСТ")
            self.name_label.setText("Имя героя:")
            self.name_input.setPlaceholderText("Введите ваше имя...")
            self.btn_start.setText("ИГРАТЬ")
            self.btn_lore.setText("ИНФО О ПЕРСОНАЖАХ")
            self.btn_settings.setText("НАСТРОЙКИ")
            self.btn_exit.setText("ВЫХОД")


# ---------- 4. Окно настроек ----------

class SettingsDialog(QDialog):
    def __init__(
        self,
        change_theme_callback,
        change_language_callback,
        toggle_music_callback,
        change_volume_callback,
        parent=None
    ):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setFixedSize(500, 250)

        layout = QVBoxLayout()

        # Язык
        lang_layout = QHBoxLayout()
        lang_label = QLabel("Язык / Language:")
        self.lang_box = QComboBox()
        self.lang_box.addItems(["Русский", "English"])
        self.lang_box.currentIndexChanged.connect(change_language_callback)
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_box)
        layout.addLayout(lang_layout)

        # Музыка
        music_layout = QHBoxLayout()
        self.music_toggle_btn = QPushButton("Музыка: Вкл / Music: On")
        self.music_toggle_btn.setCheckable(True)
        self.music_toggle_btn.setChecked(True)
        self.music_toggle_btn.clicked.connect(toggle_music_callback)

        volume_label = QLabel("Громкость / Volume:")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(30)
        self.volume_slider.valueChanged.connect(change_volume_callback)

        music_layout.addWidget(self.music_toggle_btn)
        music_layout.addWidget(volume_label)
        music_layout.addWidget(self.volume_slider)
        layout.addLayout(music_layout)

        # Тема
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Оформление / Theme:")
        self.theme_box = QComboBox()
        self.theme_box.addItems(["Светлая тема / A light theme", "Тёмная тема / Dark theme"])
        self.theme_box.currentIndexChanged.connect(change_theme_callback)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_box)
        layout.addLayout(theme_layout)

        self.setLayout(layout)


# ---------- 5. Основное окно игры ----------
class LoreDialog(QDialog):
    def __init__(self, parent=None, lang: str = "ru"):
        super().__init__(parent)
        self.setWindowTitle("Информация о персонажах" if lang == "ru" else "Characters Info")
        self.setFixedSize(600, 400)

        layout = QVBoxLayout()

        self.text = QLabel()
        self.text.setWordWrap(True)
        layout.addWidget(self.text)

        btn_close = QPushButton("Закрыть" if lang == "ru" else "Close")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

        self.set_language(lang)

    def set_language(self, lang: str):
        if lang == "en":
            self.setWindowTitle("Characters Info")
            self.text.setText(
                "<b>Leshy</b> — a forest spirit and guardian of the woods. "
                "In fairy tales he can mislead travelers or protect the forest from those who harm it. "
                "In this quest he asks the hero to help save the forest from darkness.\n\n"
                "<b>Vodyanoy</b> — a water spirit. He dwells in ponds and rivers and watches that humans "
                "do not spoil the water. He may be dangerous to those who disrespect his domain, "
                "but favors those who help nature.\n\n"
                "<b>Baba Yaga</b> — the mistress of the forest, a witch living in a hut on chicken legs. "
                "In folk tales she can be cruel or a fair tester of heroes, checking their courage and wisdom. "
                "She knows ancient magic and brews powerful potions.\n\n"
                "<b>Koschei</b> — lord of darkness and keeper of treasures. "
                "He cannot be defeated by a simple sword, because his death is hidden elsewhere. "
                "In this story he appears as a mysterious merchant of artifacts.\n\n"
                "<b>Imp</b> — a small mischievous demon from the forest thicket. "
                "Not very strong on its own, but loves to cause chaos and push people toward foolish acts.\n\n"
                "<b>Dark Wizard</b> — a mage who bound himself to the crack of darkness under the forest. "
                "He amplifies every human mistake and uses the gloom to grow his power, "
                "even if the forest must suffer for it."
            )
        else:
            self.setWindowTitle("Информация о персонажах")
            self.text.setText(
                "<b>Леший</b> — лесной дух и хранитель чащи. "
                "В сказках может и вводить путников в заблуждение, и охранять лес от тех, кто разрушает его. "
                "В этом квесте он просит героя помочь спасти лес от тьмы.\n\n"
                "<b>Водяной</b> — дух водоёма. Часто живёт в прудах и реках, следит за тем, чтобы люди не портили воду. "
                "Может быть опасен для тех, кто не уважает его владения, но благосклонен к тем, кто помогает природе.\n\n"
                "<b>Баба Яга</b> — хозяйка леса, ведьма, живущая в избушке на курьих ножках. "
                "В народных сказках может быть и злой, и справедливой испытательницей, проверяющей героя. "
                "Знает много древних чар и варит сильные зелья.\n\n"
                "<b>Кощей</b> — владыка мрака и хранитель сокровищ. "
                "Его нельзя победить простым мечом, потому что смерть Кощея спрятана отдельно. "
                "В этой истории он выступает как загадочный торговец артефактами.\n\n"
                "<b>Чёртик</b> — мелкий пакостник из лесной чащи. "
                "Сам по себе не слишком силён, но любит устраивать хаос и подталкивать людей к глупым поступкам.\n\n"
                "<b>Злой колдун</b> — маг, который подчинил себе трещину тьмы под лесом. "
                "Он усиливает каждую человеческую ошибку и использует мрак, чтобы увеличить свою силу, "
                "даже если от этого страдает весь лес."
            )
class FairyQuestGame(QMainWindow):
    def __init__(self):
        super().__init__()
        print("INIT FAIRY QUEST")
        self.run_start_time = None
        self.session = GameSession()

        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.load_music("forest_theme.mp3")

        self.music_enabled = True

        self.player_combatant = PlayerCombatant(self.session)

        # параметры боя (кликовый бой с чёртиком)
        self.player_hp = self.session.hp
        self.imp_hp = 0
        self.imp_max_hp = 0
        self.in_imp_battle = False

        # состояние загадок Водяного
        self.riddle_index = 0
        self.riddles = []
        self.riddle_mistakes = 0
        self.has_met_vodyanoy = False  # уже встречали Водяного
        self.vodyanoy_reward_given = False  # уже получали награду за загадки
        self.alchemy_done = False  # прошли ли испытания у Яги
        self.roots_to_sort = []
        self.roots_index = 0
        self.roots_correct = 0
        # мини-игра сортировки корней
        self.roots_to_sort = []
        self.roots_correct = 0
        self.roots_left_basket = None
        self.roots_right_basket = None
        # Кощей и его лавка
        self.met_koschei = False
        self.shop_items = [
            {"name": "Костяной оберег", "price": 3, "desc": "Снижает урон от тёмной магии."},
            {"name": "Серебряный клинок", "price": 4, "desc": "Помогает пробивать чары злого колдуна."},
            {"name": "Зелье ясновидения", "price": 2, "desc": "Подсказывает слабости врагов."},
        ]

        # испытание помешивания зелья (мини-игра на реакцию)
        self.stir_sequence = []
        self.stir_index = 0
        self.stir_timer: Optional[QTimer] = None
        self.stir_time_ms = 8000
        self.btn_stir_cw = None
        self.btn_stir_ccw = None

        # финальная битва "три в ряд"
        self.match3_rows = 6
        self.match3_cols = 6
        self.match3_board = []
        self.match3_buttons = []
        self.match3_selected = None
        self.evil_wizard_hp = 10

        self.match3_turns = 0
        self.match3_damage_done = 0
        self.match3_start_time = 0.0
        self.match3_damage_history = []  # список урона по каждому ходу

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Сказочный квест: Легенды леса")
        self.resize(1000, 800)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.menu_screen = MainMenu(
            self.start_game,
            sys.exit,
            self.open_settings_dialog,
            self.open_lore_dialog,  # новый колбэк
        )
        self.stack.addWidget(self.menu_screen)

        # --- Экран игры ---
        self.game_widget = QWidget()
        main_v_layout = QVBoxLayout()

        # Верхняя панель: статы + иконка оружия
        top_layout = QHBoxLayout()

        self.stats_label = QLabel()
        self.stats_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))

        self.weapon_icon_label = QLabel()
        self.weapon_icon_label.setFixedSize(64, 64)
        self.weapon_icon_label.setScaledContents(True)

        self.potion_icon_label = QLabel()
        self.potion_icon_label.setFixedSize(48, 48)
        self.potion_icon_label.setScaledContents(True)

        top_layout.addWidget(self.stats_label, alignment=Qt.AlignmentFlag.AlignLeft)
        top_layout.addStretch()
        top_layout.addWidget(QLabel("Оружие:"), alignment=Qt.AlignmentFlag.AlignRight)
        top_layout.addWidget(self.weapon_icon_label, alignment=Qt.AlignmentFlag.AlignRight)
        top_layout.addWidget(QLabel("Зелье:"), alignment=Qt.AlignmentFlag.AlignRight)
        top_layout.addWidget(self.potion_icon_label, alignment=Qt.AlignmentFlag.AlignRight)

        main_v_layout.addLayout(top_layout)

        # Область для фона и спрайтов
        self.screen_area = QWidget()
        self.screen_area.setMinimumHeight(400)
        self.screen_area.setMaximumHeight(540)
        self.screen_area.setMaximumWidth(960)

        screen_layout = QVBoxLayout()
        screen_layout.setContentsMargins(0, 0, 0, 0)

        self.bg_label = QLabel()
        self.bg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bg_label.setScaledContents(True)

        # Лейбл для графика поверх фона
        self.chart_label = QLabel(self.bg_label)
        self.chart_label.setScaledContents(True)
        self.chart_label.hide()

        # Леший как оверлей поверх фона
        self.leshy_label = QLabel(self.bg_label)
        self.leshy_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.leshy_label.setStyleSheet("background: transparent;")
        self.leshy_label.setScaledContents(True)
        self.leshy_label.hide()

        # Чёртик как оверлей поверх фона
        self.imp_label = QLabel(self.bg_label)
        self.imp_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.imp_label.setStyleSheet("background: transparent;")
        self.imp_label.setScaledContents(True)
        self.imp_label.hide()

        # Водяной как оверлей поверх фона водоёма
        self.vodyanoy_label = QLabel(self.bg_label)
        self.vodyanoy_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.vodyanoy_label.setStyleSheet("background: transparent;")
        self.vodyanoy_label.setScaledContents(True)
        self.vodyanoy_label.hide()
        self.evil_wizard_label = QLabel(self.bg_label)
        self.evil_wizard_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.evil_wizard_label.setStyleSheet("background: transparent;")
        self.evil_wizard_label.setScaledContents(True)
        self.evil_wizard_label.hide()
        # Лейбл для графика финальной битвы
        self.chart_label = QLabel(self.bg_label)
        self.chart_label.setScaledContents(True)
        self.chart_label.hide()

        screen_layout.addWidget(self.bg_label)
        self.screen_area.setLayout(screen_layout)

        main_v_layout.addWidget(self.screen_area, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Текст и кнопки
        self.text_label = QLabel()
        self.text_label.setWordWrap(True)
        self.text_label.setFont(QFont("Georgia", 13))
        self.text_label.setContentsMargins(10, 10, 10, 0)
        main_v_layout.addWidget(self.text_label)

        self.btn_container = QVBoxLayout()
        main_v_layout.addLayout(self.btn_container)

        self.game_widget.setLayout(main_v_layout)
        self.stack.addWidget(self.game_widget)

    def return_to_main_menu(self):
        print("RETURN TO MENU CALLED")
        self.stack.setCurrentWidget(self.menu_screen)
        self.stack.setCurrentWidget(self.menu_screen)

        # чистим состояние игры
        self.show_leshy(False)
        self.show_imp(False)
        self.show_vodyanoy(False)
        self.show_evil_wizard(False)

        if hasattr(self, "chart_label"):
            self.chart_label.hide()

        if hasattr(self, "text_label"):
            self.text_label.clear()

        self.clear_btns()
    # ---------- Настройки / мультимедиа ----------
    def open_lore_dialog(self):
        lang = self.session.language  # "ru" или "en"
        dlg = LoreDialog(self, lang=lang)
        dlg.exec()

    def load_music(self, file_name: str):
        path = resource_path(os.path.join("music", file_name))
        if os.path.exists(path):
            self.media_player.setSource(QUrl.fromLocalFile(path))
            self.media_player.setLoops(QMediaPlayer.Loops.Infinite)
            self.audio_output.setVolume(0.3)
        else:
            print("No music:", path)

    def toggle_theme(self, index: int):
        if index == 1:
            self.setStyleSheet(
                "QMainWindow, QWidget { background-color: #2c3e50; color: white; } "
                "QPushButton { background-color: #34495e; color: white; border: 1px solid #7f8c8d; }"
            )
            self.session.theme = "dark"
        else:
            self.setStyleSheet("")
            self.session.theme = "light"

    def toggle_music(self):
        self.music_enabled = not self.music_enabled

        if self.music_enabled:
            self.media_player.play()
        else:
            self.media_player.pause()

        btn = self.sender()
        if isinstance(btn, QPushButton):
            btn.setText("Музыка: Вкл" if self.music_enabled else "Музыка: Выкл")
            btn.setChecked(self.music_enabled)

    def change_volume(self, value: int):
        self.audio_output.setVolume(value / 100.0)

    def change_language(self, index: int):
        lang = "ru" if index == 0 else "en"
        self.session.language = lang

        # обновляем главное меню
        self.menu_screen.set_language(lang)

    def open_settings_dialog(self):
        dlg = SettingsDialog(
            self.toggle_theme,
            self.change_language,
            self.toggle_music,
            self.change_volume,
            self
        )
        dlg.music_toggle_btn.setChecked(self.music_enabled)
        dlg.music_toggle_btn.setText("Музыка: Вкл" if self.music_enabled else "Музыка: Выкл")
        dlg.exec()

    def save_run_result(self, ending_path: str):
        if self.run_start_time is None:
            return

        total_seconds = time.perf_counter() - self.run_start_time
        total_time_str = str(datetime.timedelta(seconds=int(total_seconds)))

        base_dir = os.path.dirname(__file__)
        stats_path = os.path.join(base_dir, "stats.txt")

        results = []
        if os.path.exists(stats_path):
            try:
                with open(stats_path, "r", encoding="utf-8") as f:
                    data = f.read().strip()
                    if data:
                        results = json.loads(data)
            except Exception:
                results = []

        run = {
            "date": datetime.date.today().strftime("%d.%m.%Y"),
            "name": self.session.player_name,
            "time_seconds": int(total_seconds),
            "time_str": total_time_str,
            "path": ending_path,
            "karma": self.session.karma,
            "gold": self.session.inventory.gold,
        }
        results.append(run)
        results.sort(key=lambda r: r["time_seconds"])

        rank = 1
        for idx, r in enumerate(results, start=1):
            if r is run:
                rank = idx
                break
        run["rank"] = rank

        with open(stats_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(results, ensure_ascii=False, indent=2))

        last_line_path = os.path.join(base_dir, "last_result.txt")
        with open(last_line_path, "w", encoding="utf-8") as f:
            f.write(
                f"Дата: {run['date']}\n"
                f"Имя: {run['name']}\n"
                f"Время: {run['time_str']}\n"
                f"Рейтинг: {run['rank']}\n"
                f"Путь: {run['path']}\n"
                f"Карма: {run['karma']}\n"
                f"Золото: {run['gold']}\n"
            )

    def load_all_results(self):
        base_dir = os.path.dirname(__file__)
        stats_path = os.path.join(base_dir, "stats.txt")
        if not os.path.exists(stats_path):
            return []

        try:
            with open(stats_path, "r", encoding="utf-8") as f:
                data = f.read().strip()
                if not data:
                    return []
                return json.loads(data)
        except Exception:
            return []

    # ---------- Игровая логика: пролог и Леший ----------

    def start_game(self):
        name = self.menu_screen.name_input.text()
        if name:
            self.session.player_name = name

        self.run_start_time = time.perf_counter()  # старт забега

        self.stack.setCurrentIndex(1)
        if self.music_enabled:
            self.media_player.play()
        self.update_stats()
        self.update_weapon_icon()
        self.update_potion_icon()
        self.show_intro()

    def update_stats(self):
        self.stats_label.setText(
            f"Герой: {self.session.player_name} | Карма: {self.session.karma} | "
            f"Золото: {self.session.inventory.gold} G | "
            f"Водоросли: {self.session.inventory.algae}"
        )

    def update_weapon_icon(self):
        if self.session.inventory.weapon_image:
            path = resource_path(os.path.join("images", self.session.inventory.weapon_image))
            if os.path.exists(path):
                pix = QPixmap(path)
                self.weapon_icon_label.setPixmap(pix)
            else:
                print("No weapon icon:", path)
                self.weapon_icon_label.clear()
        else:
            self.weapon_icon_label.clear()

    def show_intro(self):
        self.set_background("forest.jpg")
        self.show_leshy(False)
        self.show_imp(False)
        self.show_vodyanoy(False)
        self.text_label.setText(
            f"Очнувшись среди корней деревьев, {self.session.player_name} оглядывается по сторонам. "
            "Впереди виднеются странные огоньки. Вы решаете подойти ближе..."
        )
        self.clear_btns()
        self.add_btn("Подойти к огонькам", self.meet_leshy)

    def meet_leshy(self):
        self.set_background("forest.jpg")
        self.show_imp(False)
        self.show_vodyanoy(False)
        self.show_leshy(True)
        self.text_label.setText(
            "Перед вами из тени выступает высокий бородатый Леший. Его глаза светятся тусклым зелёным.\n\n"
            "Леший: Приветствую тебя, путник. Лес умирает. Магия слабеет, корни сохнут, звери болеют. "
            "Но сначала, пожалуй, стоит объяснить, что здесь происходит..."
        )
        self.clear_btns()
        self.add_btn("Что вообще случилось с лесом?", self.ask_what_happened)
        self.add_btn("Кто виноват в беде леса?", self.ask_who_is_guilty)
        self.add_btn("Чем именно я могу помочь?", self.ask_how_help)
        self.add_btn("Ладно, давай к делу", self.leshy_main_choice)

    def ask_what_happened(self):
        self.text_label.setText(
            "Леший: Когда‑то этот лес был полон силы. Но не так давно в самой глубине чащи "
            "поселился колдун, чья магия питается тьмой.\n\n"
            "Он нашёл древнюю трещину под корнями старых деревьев и начал вытягивать из неё мрак. "
            "С тех пор лес чахнет, реки мутнеют, а мои чары держатся всё слабее."
        )
        self.clear_btns()
        self.add_btn("Кто на самом деле виноват?", self.ask_who_is_guilty)
        self.add_btn("Чем именно я могу помочь?", self.ask_how_help)
        self.add_btn("Ладно, давай к делу", self.leshy_main_choice)

    def ask_who_is_guilty(self):
        self.text_label.setText(
            "Леший: Люди, конечно, тоже постарались — рубят без меры, бросают мусор в реку, "
            "да ещё и травы редкие выдирают с корнем.\n\n"
            "Но самую страшную рану лесу нанёс колдун. Он усиливает каждую человеческую глупость, "
            "оплетает их чарами и направляет тьму туда, где лес и так слаб.\n"
            "Чёртики в чаще только рады служить ему и разносить беду дальше."
        )
        self.clear_btns()
        self.add_btn("Что вообще случилось с лесом?", self.ask_what_happened)
        self.add_btn("Чем именно я могу помочь?", self.ask_how_help)
        self.add_btn("Ладно, давай к делу", self.leshy_main_choice)

    def ask_how_help(self):
        self.text_label.setText(
            "Леший: Мне нужен тот, кто сможет ходить между людьми, духами и даже выйти на самого колдуна.\n\n"
            "Я дам тебе крупицу силы леса, а взамен ты попробуешь умаслить духов, "
            "успокоить людей, прогнать чёртиков и, в конце концов, встретиться с тем, "
            "кто раскрыл трещину тьмы.\n"
            "Без такого проводника лесу не выжить."
        )
        self.clear_btns()
        self.add_btn("Что вообще случилось с лесом?", self.ask_what_happened)
        self.add_btn("Кто на самом деле виноват?", self.ask_who_is_guilty)
        self.add_btn("Ладно, давай к делу", self.leshy_main_choice)

    def leshy_main_choice(self):
        self.text_label.setText(
            "Леший тяжело опирается на посох и смотрит прямо вам в глаза.\n\n"
            "Леший: Ну что же, теперь ты знаешь достаточно. "
            "Скажи прямо — для чего ты готов помочь этому лесу?"
        )
        self.clear_btns()
        self.add_btn("Мне всё равно, разбирайся сам", lambda: self.leshy_choice("ignore"))
        self.add_btn("Ладно, помогу, но не бесплатно", lambda: self.leshy_choice("gold"))
        self.add_btn("Я помогу просто так. Лесу тоже больно", lambda: self.leshy_choice("hero"))

    def leshy_choice(self, choice: str):
        if choice == "ignore":
            self.session.karma -= 5
            msg = (
                "Леший обиженно вздохнул и будто стал старее:\n\n"
                "Леший: Твоя правда, человек... Но судьба всё равно тебя настигнет. "
                "Лес запомнит твой выбор."
            )
        elif choice == "gold":
            self.session.karma += 5
            self.session.inventory.gold += 3
            msg = (
                "Леший усмехнулся, но в глазах по-прежнему тревога:\n\n"
                "Леший: Честный договор. Ты — не святой, но и не последняя сволочь. "
                "Вот тебе 3 золотых на снаряжение. Не потрать их впустую."
            )
        else:
            self.session.karma += 10
            self.session.inventory.gold += 1
            msg = (
                "Леший на миг теряет голос, а потом тихо улыбается:\n\n"
                "Леший: Редкая доброта. Лесу больно, и ты это слышишь. "
                "Возьми эту монету — не за плату, а как знак, что лес на твоей стороне."
            )

        self.update_stats()
        self.text_label.setText(msg)
        self.clear_btns()
        self.add_btn("Перейти в лавку снаряжения", self.open_shop)

    # ---------- Лавка ----------

    def open_shop(self):
        self.show_leshy(False)
        self.show_imp(False)
        self.show_vodyanoy(False)
        self.text_label.setText("Вы нашли старую лесную лавку. Выберите оружие для защиты:")
        self.clear_btns()

        btn_wood = QPushButton("Деревянный меч (1 G) [+1 Сила]")
        btn_wood.setEnabled(self.session.inventory.gold >= 1)
        btn_wood.clicked.connect(
            lambda: self.buy_weapon("Деревянный меч", 1, 1, "weapons/wood_sword.png")
        )
        self.btn_layout.addWidget(btn_wood)

        btn_iron = QPushButton("Железный меч (3 G) [+3 Сила]")
        btn_iron.setEnabled(self.session.inventory.gold >= 3)
        btn_iron.clicked.connect(
            lambda: self.buy_weapon("Железный меч", 3, 3, "weapons/iron_sword.png")
        )
        self.btn_layout.addWidget(btn_iron)

        self.add_btn("Пойти без оружия (0 G)", self.prepare_battle)

    def buy_weapon(self, name: str, price: int, power: int, img_rel_path: str):
        self.session.inventory.gold -= price
        self.session.inventory.weapon = name
        self.session.inventory.strength = power
        self.session.inventory.weapon_image = img_rel_path
        self.update_stats()
        self.update_weapon_icon()
        self.prepare_battle()

    # ---------- Переход к бою с чёртиком (клик) ----------

    def prepare_battle(self):
        self.clear_btns()
        self.set_background("dark_forest.jpg")
        self.show_leshy(False)
        self.show_imp(False)
        self.show_vodyanoy(False)
        self.text_label.setText(
            "Вы углубляетесь в чащу. Между корней вдруг выскакивает чёртик, "
            "швыряясь угольками и корой.\n\nПопробуйте ударить его, кликнув по нему мышкой."
        )
        self.start_imp_battle()

    def start_imp_battle(self):
        self.in_imp_battle = True
        self.imp_max_hp = 5
        self.imp_hp = self.imp_max_hp
        self.player_hp = self.session.hp

        path = resource_path(os.path.join("images", "imp_sprite.png"))
        if os.path.exists(path):
            pix = QPixmap(path)
            self.imp_label.setPixmap(pix)
            self.imp_label.show()
            self.update_imp_geometry()
        else:
            print(f"Спрайт чёртика не найден: {path}")
            self.imp_label.hide()

        self.update_imp_battle_text(
            "Чёртик подскакивает к вам и строит рожи, пытаясь вывести из себя."
        )

    def update_imp_battle_text(self, extra: str = ""):
        base = (
            f"Ваше здоровье: {self.player_hp}\n"
            f"Чёртик: {self.imp_hp}/{self.imp_max_hp}\n\n"
        )
        self.text_label.setText(base + extra)

    # ---------- Клики мышью ----------

    def mousePressEvent(self, event):
        super().mousePressEvent(event)

        if not self.in_imp_battle:
            return

        if event.button() == Qt.MouseButton.LeftButton and self.imp_label.isVisible():
            local_pos = self.bg_label.mapFromGlobal(
                self.mapToGlobal(event.position().toPoint())
            )
            if self.imp_label.geometry().contains(local_pos):
                self.player_hit_imp()

    # ---------- Логика удара по чёртику ----------

    def player_hit_imp(self):
        if self.imp_hp <= 0 or not self.in_imp_battle:
            return

        dmg = 1 + self.session.inventory.strength
        self.imp_hp = max(0, self.imp_hp - dmg)

        log = f"Вы попадаете по чёртику и отнимаете {dmg} HP!\n"

        if self.imp_hp <= 0:
            log += "\nЧёртик с визгом растворяется в дымке. Победа!"
            self.update_imp_battle_text(log)
            self.finish_imp_battle(victory=True)
            return

        # чёртик отпрыгивает в новое место
        self.update_imp_geometry()

        # ответный удар чёртика
        if random.random() <= 0.7:
            enemy_dmg = random.randint(1, 2)
            self.player_combatant.take_damage(enemy_dmg)
            self.player_hp = self.player_combatant.hp
            self.session.hp = self.player_hp
            log += f"\nЧёртик кидается на вас и царапает на {enemy_dmg} HP!"
        else:
            log += "\nЧёртик промахивается, спотыкаясь о корень."

        if not self.player_combatant.is_alive():
            log += "\n\nВы падаете на колени. Чёртики радостно отплясывают вокруг..."
            self.update_imp_battle_text(log)
            self.finish_imp_battle(victory=False)
            return

        self.update_imp_battle_text(log)

    def finish_imp_battle(self, victory: bool):
        self.in_imp_battle = False
        self.imp_label.hide()
        self.clear_btns()

        if victory:
            self.session.karma += 2
            self.session.inventory.gold += 1
            self.update_stats()
            self.text_label.setText(
                "Вы расправились с чёртиком. Лес будто становится тише и светлее.\n\n"
                "Вы получаете 1 золотой и немного доброй кармы."
            )
            # сразу отправляем к Яге
            self.add_btn("Отправиться к Яге", self.go_to_yaga)
        else:
            self.text_label.setText(
                "Силы покидают тебя, и мир вокруг растекается в темноту.\n\n"
                "Однако лес не сдаётся — чёртик всё ещё здесь, и у тебя есть шанс попробовать ещё раз."
            )
            self.add_btn("Попробовать сразиться ещё раз", self.start_imp_battle_again)
    def start_imp_battle_again(self):
        # перезапускаем бой, не трогая остальную историю
        self.in_imp_battle = False
        self.imp_hp = 0
        self.imp_max_hp = 0

        self.clear_btns()
        self.set_background("dark_forest.jpg")
        self.show_leshy(False)
        self.show_vodyanoy(False)
        self.show_evil_wizard(False)
        self.show_imp(True)

        self.text_label.setText(
            "Ты собираешься с силами и снова выходишь против чёртика.\n"
            "Кликай по чёртику, чтобы победить его, пока он не одолел тебя."
        )

        # здесь вызови ту же функцию, которой ты запускаешь бой в первый раз
        # если она у тебя называется, например, start_imp_battle:
        self.start_imp_battle()


    # ---------- Путь к Яге и Водяной ----------

    def go_to_yaga(self):
        self.show_leshy(False)
        self.show_imp(False)
        self.show_vodyanoy(False)
        self.set_background("dark_forest.jpg")
        self.clear_btns()
        self.text_label.setText(
            "Вы идёте по всё более тихому лесу. Птицы почти не поют, "
            "листья вянут прямо у вас на глазах.\n\n"
            "Наконец, тропинка выводит к тёмному пруду рядом с кривой избушкой на курьих ножках."
        )
        self.add_btn("Подойти к пруду", self.meet_gatekeeper_leshy)

    def meet_gatekeeper_leshy(self):
        self.show_leshy(False)
        self.show_imp(False)
        self.set_background("pond.jpg")
        self.show_vodyanoy(True)
        self.clear_btns()

        if not self.has_met_vodyanoy:
            self.has_met_vodyanoy = True
            self.text_label.setText(
                "Вы выходите к тёмному пруду. Вода неподвижна, как зеркало.\n\n"
                "Из глубины медленно поднимается фигура: бородатый Водяной, обвитый водорослями.\n\n"
                "Водяной: Человек у моего берега? Редкое зрелище. "
                "У Яги кончились мои лучшие водоросли, но просто так я их не отдам.\n"
                "Отгадаешь мои загадки — получишь водоросли. Ошибёшься — уйдёшь ни с чем."
            )
        else:
            self.text_label.setText(
                "Воды пруда узнаваемо колышутся, и Водяной появляется быстрее, чем в прошлый раз.\n\n"
                "Водяной: Снова пришёл? Что ж, посмотрим, запомнил ли ты наших духов.\n"
            )

        self.add_btn("Принять испытание Водяного", self.start_riddle_quiz)
        self.add_btn("Отказатьcя и уйти", self.leave_without_algae)

    # ---------- Загадки Водяного ----------

    def start_riddle_quiz(self):
        self.riddles = [
            {
                "question": (
                    "Первая загадка.\n\n"
                    "Эти лесные духи выглядят как молодые девушки с длинными распущенными волосами, "
                    "иногда без тени и с пустотой вместо спины. Они могут и оберегать лес, и "
                    "затанцевать человека до смерти.\n\n"
                    "О каких существах из восточнославянских поверий идёт речь?"
                ),
                "options": ["Мавки", "Русалки", "Полудницы"],
                "answer": "Мавки",
            },
            {
                "question": (
                    "Вторая загадка.\n\n"
                    "Эта сущность появляется в знойный полдень на полях. Часто описывается как высокая "
                    "женщина в белом, которая подходит к жнецам, задаёт вопросы или заставляет работать "
                    "в самый жар. Встреча с ней грозит солнечным ударом или безумием.\n\n"
                    "Как зовут этот полуденный дух в славянской мифологии?"
                ),
                "options": ["Полудница", "Кикимора", "Мара"],
                "answer": "Полудница",
            },
            {
                "question": (
                    "Третья загадка.\n\n"
                    "Это древнее чудовище часто описывают как многоголовое змееподобное или драконье "
                    "существо, связанное с водной стихией. В сказках оно становится почти "
                    "олицетворением разрушительной силы, способной жечь города и царства.\n\n"
                    "Как в русских сказках называется это существо?"
                ),
                "options": ["Чудо‑Юдо", "Змей Горыныч", "Тугарин Змей"],
                "answer": "Чудо‑Юдо",
            },
            {
                "question": (
                    "Четвёртая загадка.\n\n"
                    "Этот дух не живёт дома и не охраняет очаг, но тоже связан с повседневной жизнью людей. "
                    "Иногда его представляли как худую, измождённую фигуру, следящую за человеком с рождения, "
                    "приносящую бедность и несчастья — будто сама \"несчастье\" воплоти.\n\n"
                    "Как в некоторых славянских традициях называют такой образ беды‑несчастья?"
                ),
                "options": ["Беда", "Мара", "Чума"],
                "answer": "Беда",
            },
            {
                "question": (
                    "Пятая загадка.\n\n"
                    "Эта фигура в славянской традиции связана с зимой, увяданием и смертью. "
                    "Её могли представлять как бледную женщину или чучело, которое в конце зимы "
                    "торжественно сжигают или топят, провожая холод и зовя весну.\n\n"
                    "Как обычно называют этот образ в славянских обрядах?"
                ),
                "options": ["Морана", "Полудница", "Кикимора"],
                "answer": "Морана",
            },
        ]
        self.riddle_index = 0
        self.riddle_mistakes = 0
        self.text_label.setText(
            "Водяной: Тогда слушай внимательно, человек. "
            "Я не люблю тех, кто путает духов леса и воды.\n\n"
            "Каждый неверный ответ — шаг прочь от моих водорослей."
        )
        self.clear_btns()
        self.add_btn("Начать загадки", self.ask_next_riddle)

    def ask_next_riddle(self):
        self.clear_btns()
        if self.riddle_index >= len(self.riddles):
            # если ошибок нет — успех, иначе провал
            self.finish_riddles(success=(self.riddle_mistakes == 0))
            return

        r = self.riddles[self.riddle_index]
        self.text_label.setText(r["question"])

        for opt in r["options"]:
            self.add_btn(opt, lambda checked=False, o=opt: self.check_riddle_answer(o))

    def check_riddle_answer(self, selected: str):
        r = self.riddles[self.riddle_index]
        correct = r["answer"]

        if selected == correct:
            self.riddle_index += 1
            self.text_label.setText(
                "Водяной хрипло смеётся:\n"
                "— Не так прост, как выглядишь. Посмотрим, что будет дальше...\n"
            )
            self.clear_btns()
            self.add_btn("Продолжить", self.ask_next_riddle)
        else:
            self.riddle_mistakes += 1
            self.riddle_index += 1
            # если ещё есть вопросы — продолжаем, но он ворчит
            if self.riddle_index < len(self.riddles):
                self.text_label.setText(
                    "Водяной недовольно шлёпает хвостом по воде:\n"
                    "— Нехорошо путать духов. Мифологию надо знать лучше.\n"
                )
                self.clear_btns()
                self.add_btn("Продолжить", self.ask_next_riddle)
            else:
                # закончились вопросы — сразу завершаем
                self.finish_riddles(success=False)

    def finish_riddles(self, success: bool):
        self.clear_btns()

        if success:
            # сюда попадаем только при идеальном прохождении (0 ошибок)
            if not self.vodyanoy_reward_given:
                self.session.inventory.algae += 1
                self.session.karma += 2
                self.session.inventory.gold += 1
                self.vodyanoy_reward_given = True
                self.update_stats()
                self.text_label.setText(
                    "Водяной довольно улыбается и вода вокруг светлеет:\n\n"
                    "— Ни одной ошибки. Редко такое вижу даже среди духов.\n"
                    "Бери мои лучшие водоросли, золото и моё расположение.\n\n"
                    "Вы получаете водоросли, 2 кармы и 1 золотой."
                )
            else:
                self.text_label.setText(
                    "Водяной: Я уже отдавал тебе водоросли. Больше у меня для тебя наград нет.\n"
                    "Учить мифологию всё равно полезно, но платить за это второй раз я не стану."
                )

            self.add_btn("Идти к Бабе Яге", self.go_to_baba_yaga)
            return  # дальше не идём

        # ----- success == False: есть ошибки -----

        if self.riddle_mistakes == 1 and not self.vodyanoy_reward_given:
            # одна ошибка — водоросли без бонусов
            self.session.inventory.algae += 1
            self.vodyanoy_reward_given = True
            self.update_stats()
            self.text_label.setText(
                "Водяной ворчит, волны вокруг становятся чуть тяжелее:\n\n"
                "— Одну-то ошибку я переживу. Но мифологию надо знать лучше, человек.\n"
                "Ладно, держи водоросли, Яга тебе их всё равно выпросила бы.\n\n"
                "Вы получаете водоросли, но без дополнительных наград."
            )
            self.add_btn("Идти к Бабе Яге", self.go_to_baba_yaga)

        elif self.riddle_mistakes >= 2:
            # слишком много ошибок — без водорослей, но без отката игры
            self.text_label.setText(
                "Вы путаетесь в ответах, называя не тех духов и не те имена.\n\n"
                "Водяной тяжело вздыхает:\n"
                "— Всё мимо. Так мифологию не изучают. Сегодня водорослей не будет.\n\n"
                "— Но если вернёшься подготовленным, я дам тебе ещё один шанс."
            )
            self.add_btn("Отойти от пруда", self.leave_without_algae)

        else:
            # на всякий случай защитный вариант (например, 0 ошибок, но success=False не должен случиться)
            self.text_label.setText(
                "Водяной смотрит на тебя пристально:\n"
                "— Сегодня без наград. Возвращайся, когда будешь уверен в ответах.\n"
            )
            self.add_btn("Отойти от пруда", self.leave_without_algae)


    def leave_without_algae(self):
        # уходим от Водяного к Лешему
        self.set_background("forest.jpg")
        self.show_vodyanoy(False)
        self.show_imp(False)
        self.show_leshy(True)
        self.clear_btns()

        penalty_text = ""
        # лёгкое наказание за отказ
        if self.session.inventory.gold > 0:
            self.session.inventory.gold -= 1
            penalty_text = "Леший тяжело вздыхает и забирает у вас 1 золотой за потерянное время.\n\n"
        else:
            self.session.karma -= 1
            penalty_text = "Леший качает головой: «Так дела не делаются». Ваша карма слегка ухудшается.\n\n"

        self.update_stats()

        self.text_label.setText(
            penalty_text +
            "Леший: Я понимаю, Водяной непростой, но без его водорослей лесу не выжить.\n"
            "Если передумаешь — придётся вернуться к пруду и попытаться ещё раз."
        )
        self.add_btn("Вернуться к Водяному", self.go_to_yaga)
    def go_to_baba_yaga(self):
        self.set_background("forest1.jpg")  # можешь сделать отдельный фон избушки
        self.show_leshy(False)
        self.show_imp(False)
        self.show_vodyanoy(False)
        self.clear_btns()

        self.text_label.setText(
            "Избушка поворачивается к вам фасадом, скрипят курьи ножки.\n"
            "На пороге появляется Баба Яга, прищурив глаза.\n\n"
            "Баба Яга: Вижу, у тебя водоросли Водяного. Не так-то просто их достать..."
        )

        # варианты сделки
        if self.session.inventory.algae > 0 and not self.alchemy_done:
            self.add_btn("Отдать водоросли просто так", self.give_algae_free)
            self.add_btn("Поторговаться", self.trade_algae_for_gold)
        else:
            # если почему-то пришли без водорослей или уже всё сделали
            self.add_btn("Поговорить о зельях", self.start_alchemy_tests)
    def give_algae_free(self):
        # отдать водоросли без наград
        self.session.inventory.algae = 0
        self.update_stats()
        self.clear_btns()
        self.text_label.setText(
            "Вы молча протягиваете Бабе Яге водоросли.\n\n"
            "Баба Яга хмыкает:\n"
            "— Ну хоть кто-то ещё делает что-то не из корыстных побуждений.\n"
            "Ладно, раз уж ты помог, помогу и я. Но придётся поработать руками.\n\n"
            "Она затаскивает вас в избушку, к столу с корнями и котлом."
        )
        self.add_btn("Приступить к испытаниям", self.start_alchemy_tests)

    def trade_algae_for_gold(self):
        # торг: +2 золота, -10 кармы, водоросли тратятся
        self.session.inventory.algae = 0
        self.session.inventory.gold += 2
        self.session.karma -= 10
        self.update_stats()
        self.clear_btns()
        self.text_label.setText(
            "Вы задерживаете руку с водорослями.\n\n"
            "— Просто так? — усмехается Яга. — Ну-ну. Давай-ка по-честному: "
            "ты мне водоросли, я тебе немного золота. Карма твоя, конечно, от этого не поправится...\n\n"
            "Вы соглашаетесь. Водоросли исчезают в её руках, а на стол падают две туго набитые монеты.\n"
            "Баба Яга: Раз уж ты всё равно здесь — поможешь с моими зельями."
        )
        self.add_btn("Приступить к испытаниям", self.start_alchemy_tests)

    def start_roots_sort_game(self):
        # перед каждым запуском сортировки аккуратно убираем всё старое
        if self.roots_left_basket is not None:
            self.roots_left_basket.deleteLater()
            self.roots_left_basket = None
        if self.roots_right_basket is not None:
            self.roots_right_basket.deleteLater()
            self.roots_right_basket = None
        for r in getattr(self, "roots_to_sort", []):
            if r is not None:
                r.deleteLater()
        self.roots_to_sort = []
        self.roots_correct = 0

        self.clear_btns()
        self.text_label.setText(
            "Перетаскивайте красные корни в левую корзину, а зелёные — в правую."
        )

        bg_rect = self.bg_label.contentsRect()

        # корзины на bg_label
        self.roots_left_basket = BasketLabel("Левая корзина\n(красные)", "red", self.bg_label)
        self.roots_left_basket.setFixedSize(220, 180)
        self.roots_right_basket = BasketLabel("Правая корзина\n(зелёные)", "green", self.bg_label)
        self.roots_right_basket.setFixedSize(220, 180)

        left_x = bg_rect.x() + int(bg_rect.width() * 0.15)
        right_x = bg_rect.x() + int(bg_rect.width() * 0.65)
        y = bg_rect.y() + int(bg_rect.height() * 0.55)

        self.roots_left_basket.move(left_x, y)
        self.roots_right_basket.move(right_x, y)
        self.roots_left_basket.show()
        self.roots_right_basket.show()

        colors = ["red"] * 3 + ["green"] * 3
        random.shuffle(colors)

        for color in colors:
            root = DraggableRoot(color, self.bg_label)
            rx = random.randint(bg_rect.x() + 50, bg_rect.x() + bg_rect.width() - 100)
            ry = bg_rect.y() + int(bg_rect.height() * 0.15)
            root.move(rx, ry)
            root.show()
            self.roots_to_sort.append(root)

    def root_dropped_in_game(self, root: DraggableRoot):
        if root.placed or not (self.roots_left_basket and self.roots_right_basket):
            return

        # центр корня в координатах bg_label
        center_in_bg = root.mapToParent(root.rect().center())  # parent = bg_label

        left_rect = self.roots_left_basket.geometry()
        right_rect = self.roots_right_basket.geometry()

        in_left = left_rect.contains(center_in_bg)
        in_right = right_rect.contains(center_in_bg)

        if in_left or in_right:
            target_color = "red" if in_left else "green"
            if root.color == target_color:
                self.roots_correct += 1

            basket = self.roots_left_basket if in_left else self.roots_right_basket
            pos_in_basket = basket.mapFromParent(center_in_bg)
            root.setParent(basket)
            root.move(pos_in_basket - root.rect().center())
            root.placed = True
            root.show()

        if self.roots_to_sort and all(r.placed for r in self.roots_to_sort):
            self.finish_roots_sort_game()

    def start_alchemy_tests(self):
        self.alchemy_done = False
        self.clear_btns()
        self.text_label.setText(
            "Вы оказываетесь за столом у Бабы Яги. На фоне виднеется котёл, а перед вами — "
            "две большие корзины.\n\n"
            "Баба Яга: Красные корни — в левую, зелёные — в правую. Не перепутай, а то всё взлетит к лешему."
        )
        self.add_btn("Начать сортировку корней", self.start_roots_sort_game)

    def finish_roots_sort_game(self):
        self.clear_btns()
        total = len(self.roots_to_sort)
        if self.roots_correct >= total - 1:
            self.text_label.setText(
                f"Баба Яга осматривает корзины.\n\n"
                f"— {self.roots_correct} из {total} правильно. Почти без ошибок. Сойдёт.\n"
                "Теперь самое главное — мешать зелье правильно, а не как попало."
            )
            self.add_btn("Перейти к помешиванию зелья", self.start_stir_test)
        else:
            self.text_label.setText(
                f"Корни отсортированы неаккуратно: правильно только {self.roots_correct} из {total}.\n\n"
                "Баба Яга фыркает: — С такой сортировкой котёл точно взлетит. "
                "Будем считать, что сегодня зелья не выйдет.\n\n"
                "Попробуй ещё раз разложить корни по корзинам."
            )
            self.add_btn("Попробовать ещё раз", self.start_roots_sort_game)

    def update_potion_icon(self):
        if self.session.inventory.potion_image:
            path = resource_path(os.path.join("images", self.session.inventory.potion_image))
            if os.path.exists(path):
                pix = QPixmap(path)
                self.potion_icon_label.setPixmap(pix)
            else:
                print("No potion icon:", path)
                self.potion_icon_label.clear()
        else:
            self.potion_icon_label.clear()

    def start_stir_test(self):
        # аккуратно убираем корзины и корни
        if self.roots_left_basket is not None:
            self.roots_left_basket.deleteLater()
            self.roots_left_basket = None
        if self.roots_right_basket is not None:
            self.roots_right_basket.deleteLater()
            self.roots_right_basket = None
        for r in getattr(self, "roots_to_sort", []):
            if r is not None:
                r.deleteLater()
        self.roots_to_sort = []
        self.roots_correct = 0

        self.clear_btns()

        self.text_label.setText(
            "Баба Яга пододвигает к вам тяжёлый чугунный котёл.\n\n"
            "— Сейчас проверим, как ты мешаешь зелье.\n"
            "Следи за стрелками и успевай крутить в нужную сторону!"
        )

        # создаём последовательность: немного случайная, но с обеими сторонами
        base_seq = ["cw", "cw", "ccw", "cw", "ccw"]
        random.shuffle(base_seq)
        self.stir_sequence = base_seq
        self.stir_index = 0

        # кнопки управления
        self.btn_stir_cw = self.add_btn("Крутить по часовой ↻", lambda: self.handle_stir_click("cw"))
        self.btn_stir_ccw = self.add_btn("Крутить против ↺", lambda: self.handle_stir_click("ccw"))

        # таймер на реакцию
        if self.stir_timer is None:
            self.stir_timer = QTimer(self)
            self.stir_timer.setSingleShot(True)
            self.stir_timer.timeout.connect(self.stir_timeout)

        # показываем первый шаг
        self.show_current_stir_step()

    def show_current_stir_step(self):
        """Обновить текст и запустить таймер для текущего шага."""
        if self.stir_index >= len(self.stir_sequence):
            # все шаги выполнены
            self.finish_stir_success()
            return

        step = self.stir_sequence[self.stir_index]
        if step == "cw":
            direction_text = "по часовой стрелке ↻"
        else:
            direction_text = "против часовой стрелки ↺"

        self.text_label.setText(
            "Баба Яга внимательно смотрит на котёл.\n\n"
            f"Сейчас нужно крутить {direction_text}.\n"
            f"У тебя есть всего {self.stir_time_ms // 1000} сек. на реакцию!"
        )

        # перезапускаем таймер
        self.stir_timer.start(self.stir_time_ms)

    def handle_stir_click(self, direction: str):
        """Игрок нажал одну из кнопок."""
        if self.stir_index >= len(self.stir_sequence):
            return  # уже всё

        expected = self.stir_sequence[self.stir_index]

        # останавливаем таймер, чтобы не сработал после клика
        if self.stir_timer.isActive():
            self.stir_timer.stop()

        if direction == expected:
            # успешный шаг
            self.stir_index += 1
            # небольшая фраза-реакция, затем следующий шаг
            self.text_label.setText(
                "Зелье чуть булькнуло.\n\n"
                "Яга хмыкает: — Ладно, пока не перелил. Продолжай..."
            )
            QTimer.singleShot(700, self.show_current_stir_step)
        else:
            # ошибка
            self.finish_stir_fail("Не в ту сторону крутишь, варево вот-вот убежит!")

    def stir_timeout(self):
        """Игрок не успел нажать вовремя."""
        self.finish_stir_fail("Замешкался! Зелье вспенивается и грозит выплеснуться.")

    def finish_stir_fail(self, reason: str):
        """Провал испытания помешивания."""
        self.clear_btns()
        if self.stir_timer and self.stir_timer.isActive():
            self.stir_timer.stop()

        self.text_label.setText(
            f"{reason}\n\n"
            "Баба Яга резко отталкивает котёл.\n"
            "— Эх ты, размазня. Так зелье только испортишь.\n"
            "Попробуем ещё раз, пока котёл не треснул."
        )

        self.add_btn("Попробовать помешивать снова", self.start_stir_test)
        self.add_btn("Смиренно отойти от котла", self.after_yaga_fail)

    def finish_stir_success(self):
        """Успешное прохождение испытания помешивания."""
        self.clear_btns()
        if self.stir_timer and self.stir_timer.isActive():
            self.stir_timer.stop()

        self.text_label.setText(
            "Ты чётко следуешь указаниям, зелье мерно закручивается в котле.\n\n"
            "Баба Яга довольно крякает:\n"
            "— Вот это помешивание! Может, из тебя ещё толк будет.\n"
            "Держи своё зелье, только не расплескай по дороге."
        )

        self.session.inventory.potion_image = "potion.png"
        self.update_potion_icon()

        self.add_btn("Поблагодарить Ягу и уйти", self.after_yaga_success)

    def after_yaga_fail(self):
        """Что происходит после отказа продолжать помешивание (сюжетный ход)."""
        # тут можешь сделать, например, возвращение в лес или к Лешему
        self.text_label.setText(
            "Вы сбились с ритма, зелье шипит и темнеет.\n"
            "Баба Яга недовольно цокает языком.\n\n"
            "— Ничего, — ворчит она. — Будешь внимательнее и попробуешь ещё раз."
        )
        self.add_btn("Попробовать помешивать снова", self.start_stir_test)


    def after_yaga_success(self):
        self.alchemy_done = True
        self.clear_btns()
        self.text_label.setText(
            "С зельем в сумке ты выходишь из избушки.\n\n"
            "Баба Яга кряхтит, поправляя платок:\n"
            "— Вот что, герой. Зелье у тебя есть, но этого мало.\n"
            "В лесу завёлся злой колдун, отравляет корни и воду.\n"
            "Один ты с ним не справишься.\n\n"
            "— Ступай к Кощею Бессмертному, — шепчет Яга.\n"
            "— Стар он, мудр и жаден. За золото отдаст тебе артефакты,\n"
            "что помогут выдержать бой: обереги, клинки да редкие травы.\n"
            "Только слушай его байки внимательно — иной раз в них больше правды,\n"
            "чем в книжках.\n"
        )
        self.clear_btns()
        self.add_btn("Отправиться к Кощею", self.go_to_koschei)

    def go_to_koschei(self):
        self.set_background("koschei_tower.jpg")
        self.clear_btns()

        if not self.met_koschei:
            self.met_koschei = True
            intro = (
                "Ты поднимаешься к чёрной башне, что торчит над лесом, как старая кость.\n"
                "На вершине, среди книг и цепей, сидит высохший старик с живыми глазами.\n\n"
                "— Кощей Бессмертный, — представляется он хриплым голосом.\n"
                "— Жив дольше многих царств, видел больше многих сказок.\n"
                "Слыхал я и про твоего колдуна, что травит лес.\n"
                "Но мудрость и сила нынче недёшево стоят.\n"
            )
        else:
            intro = (
                "Кощей тяжело разворачивается к тебе.\n\n"
                "— Снова ты, герой. Лес ещё живой? Золото не отсырело?\n"
            )

        self.text_label.setText(intro)
        self.add_btn("Поговорить с Кощеем", self.talk_with_koschei)
        self.add_btn("Посмотреть артефакты", self.open_koschei_shop)

    def talk_with_koschei(self):
        self.clear_btns()
        self.text_label.setText(
            "Кощей устало опирается на посох.\n\n"
            "— Жизнь длинна, как старая дорога, — бурчит он.\n"
            "— Видал я и домовых, и котов, что сказками лечат, и таких колдунов,\n"
            "которые сами не помнят, зачем зло сеют.\n\n"
            "— О чём хочешь услышать, герой?"
        )

        self.add_btn("О домовых, хранителях домов", self.koschei_tell_domovoi)
        self.add_btn("О Коте Баюне и его сказках", self.koschei_tell_kot_bayun)
        self.add_btn("Про самого Кощея", self.koschei_tell_self)
        self.add_btn("Хватит сказок, к артефактам", self.open_koschei_shop)

    def koschei_tell_domovoi(self):
        self.clear_btns()
        self.text_label.setText(
            "— Домовой, — улыбается Кощей краешком губ, — не злой и не добрый.\n"
            "Он как печь: как кормишь, так и греет.\n"
            "Бережёт дом от крадущихся, от завистников да от лихих духов.\n"
            "Кто с ним ладит — тот в беду редко попадает.\n\n"
            "— Запомни, герой: прежде чем с колдуном сражаться,\n"
            "научись с малой нечистью дружить.\n"
        )
        self.add_btn("Спросить ещё про сказочных существ", self.talk_with_koschei)
        self.add_btn("Вернуться к артефактам", self.open_koschei_shop)

    def koschei_tell_kot_bayun(self):
        self.clear_btns()
        self.text_label.setText(
            "— Кот Баюн… — голос Кощея становится тише.\n"
            "— Сидит на цепи, сказки бает, да не для всех.\n"
            "Кого убаюкает — того и съест, а кого не доспать заставит — тому боль снимет,\n"
            "сердце залечит да мысли прояснит.\n\n"
            "— Ты бы с таким не поспорил, герой.\n"
            "Но помни: слово и песня порой сильнее меча.\n"
        )
        self.add_btn("Спросить ещё", self.talk_with_koschei)
        self.add_btn("Вернуться к артефактам", self.open_koschei_shop)

    def koschei_tell_self(self):
        self.clear_btns()
        self.text_label.setText(
            "Кощей на секунду замолкает.\n\n"
            "— Про меня сказки врали не меньше, чем про лесных духов,\n"
            "— усмехается он.\n"
            "— Бессмертный — не значит всесильный.\n"
            "Слишком долгий век — тоже проклятие.\n\n"
            "— Оттого-то я и коплю артефакты: каждый — память о чьей-то надежде.\n"
        )
        self.add_btn("Перевести разговор к делу", self.open_koschei_shop)
        self.add_btn("Спросить ещё сказок", self.talk_with_koschei)

    def open_koschei_shop(self):
        self.clear_btns()
        gold = self.session.inventory.gold
        lines = [
            f"— Золото у тебя, вижу, есть: {gold} монет.",
            "— Смотри внимательно, герой. Каждая безделушка — чья-то судьба."
        ]

        desc_lines = []
        for idx, item in enumerate(self.shop_items, start=1):
            desc_lines.append(f"{idx}. {item['name']} — {item['price']} золота. {item['desc']}")

        self.text_label.setText("\n".join(lines) + "\n\n" + "\n".join(desc_lines))

        for idx, item in enumerate(self.shop_items, start=1):
            self.add_btn(f"Купить: {item['name']}", lambda _, i=idx - 1: self.buy_shop_item(i))

        # новая кнопка — ничего не покупать
        self.add_btn("Ничего не покупать", self.after_koschei_shop)


    def buy_shop_item(self, index: int):
        item = self.shop_items[index]
        price = item["price"]
        if self.session.inventory.gold < price:
            self.text_label.setText(
                "Кощей качает головой:\n"
                "— Не хватает монет, герой. В этом мире даже сказки в долг не дают.\n"
            )
            self.clear_btns()
            self.add_btn("Купить что‑то ещё", self.open_koschei_shop)
            self.add_btn("Закончить дела с Кощеем", self.after_koschei_shop)
            return

        # списываем золото
        self.session.inventory.gold -= price

        # очень простой эффект: кладём название в инвентарь/поля
        if item["name"] == "Костяной оберег":
            self.session.inventory.strength += 1
        elif item["name"] == "Серебряный клинок":
            self.session.inventory.strength += 2
            self.session.inventory.weapon = "Серебряный клинок"
        elif item["name"] == "Зелье ясновидения":
            # можешь завести отдельный флаг для финальной битвы
            self.session.inventory.algae += 1  # как пример “магического ресурса”

        self.update_stats()
        self.clear_btns()
        self.text_label.setText(
            f"Ты отдаёшь {price} монет. Кощей аккуратно перекладывает их в шкатулку.\n\n"
            f"— {item['name']} теперь твой, — говорит он.\n"
            "— Пусть послужит лучше, чем тем, кто его потерял.\n"
        )

        self.add_btn("Купить что‑то ещё", self.open_koschei_shop)
        self.add_btn("Закончить дела с Кощеем", self.after_koschei_shop)

    def after_koschei_shop(self):
        """Герой закончил дела с Кощеем и идёт к Лешему с зельем."""
        self.clear_btns()
        self.set_background("forest_mist.jpg")  # туманный лес
        self.show_leshy(True)
        self.show_imp(False)
        self.show_vodyanoy(False)

        self.text_label.setText(
            "С зельем и, возможно, парой артефактов ты возвращаешься к Лешему.\n\n"
            "Леший бережно принимает склянку, нюхает и залпом выпивает её содержимое.\n"
            "Корни вокруг пускают свежие побеги, листья становятся ярче, воздух наполняется шёпотом леса.\n\n"
            "Но радость длится недолго: из глубины чащи поднимается холодный туман.\n"
            "Тени сгущаются, и из них выходит высокий силуэт в тёмном плаще — злой волшебник,\n"
            "чья магия отравляла лес всё это время."
        )

        self.add_btn("Посмотреть на злого волшебника", self.meet_evil_wizard)

    def show_evil_wizard(self, visible: bool):
        path = resource_path(os.path.join("images", "evil_wizard.png"))
        if visible and os.path.exists(path):
            pix = QPixmap(path)
            self.evil_wizard_label.setPixmap(pix)
            self.evil_wizard_label.show()
            self.update_evil_wizard_geometry()
        else:
            self.evil_wizard_label.hide()

    def meet_evil_wizard(self):
        self.clear_btns()
        self.set_background("forest_mist.jpg")
        self.show_leshy(False)
        self.show_imp(False)
        self.show_vodyanoy(False)
        self.show_evil_wizard(True)

        self.text_label.setText(
            "Туман сгущается, и из серой мглы выступает высокая фигура в тёмном плаще.\n\n"
            "Голос колдуна раздаётся сразу отовсюду:\n"
            "— Значит, это ты тот герой, о котором шепчутся Леший и его жалкие союзники.\n"
            "Ты потревожил моих чёртиков, уговорил духов и даже добрался сюда.\n\n"
            "— Лес гибнет не потому, что я так захотел, — продолжает он. — Я лишь использую трещину тьмы, "
            "которую люди сами разбудили своей жадностью. Я беру силу из того, что уже обречено.\n"
            "Скажи, человек, уверен ли ты, что защищаешь тех, кто вообще достоин спасения?"
        )

        self.add_btn("Я здесь, чтобы остановить тебя", self.prepare_final_battle)

    def prepare_final_battle(self):
        self.clear_btns()
        self.evil_wizard_hp = 10
        self.match3_selected = None
        self.match3_turns = 0
        self.match3_damage_done = 0
        self.match3_damage_history = []
        self.match3_start_time = time.perf_counter()
        self.init_match3_board()
        self.show_match3_board()

        karma = self.session.karma
        weapon = self.session.inventory.weapon
        potion_img = self.session.inventory.potion_image  # у тебя так хранится зелье
        has_algae = (self.session.inventory.algae > 0)
        helped_yaga = self.alchemy_done

        # базовая эмоция сцены по карме
        if karma >= 8:
            intro = (
                "Ты сжимаешь артефакты, и лес будто дышит вместе с тобой.\n"
                "Свет, который ты собрал по пути, не даёт туману вокруг колдуна сомкнуться."
            )
        elif karma <= -5:
            intro = (
                "Ты сжимаешь артефакты, и тьма вокруг колдуна кажется почти знакомой.\n"
                "Лес колеблется, не уверенный, действительно ли ты его защищаешь."
            )
        else:
            intro = (
                "Ты сжимаешь артефакты, вспоминая все спорные решения пути.\n"
                "Лес просто молчит и ждёт исхода битвы."
            )

        # реплики под выбор предмета Кощея
        if weapon == "Костяной оберег":
            intro += (
                "\n\nКостяной оберег на груди тяжелеет, впитывая каждое колебание тёмной магии.\n"
                "Он глухо звенит, когда колдун тянется к трещине тьмы — будто предупреждает о грядущем ударе."
            )
        elif weapon == "Серебряный клинок":
            intro += (
                "\n\nСеребряный клинок дрожит в твоей руке, подпевая каждому шороху чар колдуна.\n"
                "Сила Кощея рвётся наружу, готовая рассечь тьму."
            )
        elif weapon == "Зелье ясновидения":
            intro += (
                "\n\nФлакон с Зельем ясновидения холодит ладонь.\n"
                "В густой жидкости вспыхивают образы слабых мест колдуна, но у тебя будет лишь один шанс использовать это знание."
            )
        else:
            intro += (
                "\n\nУ тебя нет особых даров Кощея — только то, что удалось собрать в дороге.\n"
                "Но даже этого может хватить, если не отступать."
            )

        # вклад Яги / Водяного
        if helped_yaga:
            intro += (
                "\n\nГде‑то внутри ещё отзывается вкус зелья Бабы Яги — "
                "её магия тонкой нитью поддерживает твои силы."
            )

        if has_algae:
            intro += (
                "\n\nОт водорослей Водяного тянет сырой прохладой, "
                "и часть тьмы вокруг трещины гаснет, не дотягиваясь до тебя."
            )

        intro += "\n\nВскоре начнётся решающее столкновение. Ошибаться уже нельзя."

        self.text_label.setText(intro)
        self.add_btn("Начать решающую битву", self.start_match3_battle)
    def init_match3_board(self):
        symbols = ["🌿", "🔥", "💧", "🌙", "⭐"]  # можно заменить на буквы
        self.match3_board = [[None for _ in range(self.match3_cols)] for _ in range(self.match3_rows)]

        for r in range(self.match3_rows):
            for c in range(self.match3_cols):
                while True:
                    s = random.choice(symbols)
                    # не создаём сразу 3 в ряд
                    if c >= 2 and self.match3_board[r][c-1] == s and self.match3_board[r][c-2] == s:
                        continue
                    if r >= 2 and self.match3_board[r-1][c] == s and self.match3_board[r-2][c] == s:
                        continue
                    self.match3_board[r][c] = s
                    break

    def show_match3_board(self):
        self.clear_btns()

        self.text_label.setText(
            f"HP злого волшебника: {self.evil_wizard_hp}\n"
            "Выбери две соседние клетки, чтобы поменять их местами.\n"
            "Собранные ряды наносят урон."
        )

        container = QWidget()
        container_layout = QGridLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(2)  # расстояние между кнопками

        self.match3_buttons = [[None for _ in range(self.match3_cols)] for _ in range(self.match3_rows)]

        for r in range(self.match3_rows):
            for c in range(self.match3_cols):
                btn = QPushButton(self.match3_board[r][c])
                btn.setFixedSize(40, 40)
                container.setFixedWidth(6 * 40 + 5 * 2 + 10)
                btn.setStyleSheet(
                    "QPushButton { background-color: #ffffff; border: 1px solid #bdc3c7; }"
                    "QPushButton:hover { background-color: #ecf0f1; }"
                )
                btn.clicked.connect(lambda checked=False, rr=r, cc=c: self.handle_match3_click(rr, cc))
                self.match3_buttons[r][c] = btn
                container_layout.addWidget(btn, r, c)

        # фиксируем примерную ширину под сетку (6 * 50 + зазоры)
        container.setFixedWidth(6 * 50 + 5 * 2 + 10)
        self.btn_layout.addWidget(container, alignment=Qt.AlignmentFlag.AlignHCenter)
    def handle_match3_click(self, r, c):
        # первый выбор
        if self.match3_selected is None:
            self.match3_selected = (r, c)
            self.match3_buttons[r][c].setStyleSheet("background-color: #f1c40f;")
            return

        r1, c1 = self.match3_selected
        r2, c2 = r, c

        # снимаем выделение
        self.match3_buttons[r1][c1].setStyleSheet("")
        self.match3_selected = None

        # та же клетка
        if r1 == r2 and c1 == c2:
            return

        # проверка соседства
        if abs(r1 - r2) + abs(c1 - c2) != 1:
            return

        # пробуем обмен
        self.swap_match3_cells(r1, c1, r2, c2)
        matches = self.find_match3_matches()
        if not matches:
            # откат, если не получилось собрать
            self.swap_match3_cells(r1, c1, r2, c2)
            return

        # обрабатываем совпадения
        self.match3_turns += 1
        self.resolve_match3(matches)

    def swap_match3_cells(self, r1, c1, r2, c2):
        self.match3_board[r1][c1], self.match3_board[r2][c2] = \
            self.match3_board[r2][c2], self.match3_board[r1][c1]
    def find_match3_matches(self):
        rows = self.match3_rows
        cols = self.match3_cols
        b = self.match3_board
        matched = [[False] * cols for _ in range(rows)]

        # горизонтальные
        for r in range(rows):
            c = 0
            while c < cols - 2:
                s = b[r][c]
                if s is None:
                    c += 1
                    continue
                run = 1
                while c + run < cols and b[r][c + run] == s:
                    run += 1
                if run >= 3:
                    for k in range(run):
                        matched[r][c + k] = True
                c += run if run > 1 else 1

        # вертикальные
        for c in range(cols):
            r = 0
            while r < rows - 2:
                s = b[r][c]
                if s is None:
                    r += 1
                    continue
                run = 1
                while r + run < rows and b[r + run][c] == s:
                    run += 1
                if run >= 3:
                    for k in range(run):
                        matched[r + k][c] = True
                r += run if run > 1 else 1

        return [(r, c) for r in range(rows) for c in range(cols) if matched[r][c]]
    def resolve_match3(self, matches):
        if not matches:
            self.show_match3_board()
            return

        # урон: примерно по числу рядов
        damage = max(1, len(matches) // 3)
        self.evil_wizard_hp = max(0, self.evil_wizard_hp - damage)
        self.match3_damage_done += damage
        self.match3_damage_history.append(damage)

        # удаляем совпавшие
        for r, c in matches:
            self.match3_board[r][c] = None

        # "падение" вниз
        for c in range(self.match3_cols):
            write_row = self.match3_rows - 1
            for r in range(self.match3_rows - 1, -1, -1):
                if self.match3_board[r][c] is not None:
                    self.match3_board[write_row][c] = self.match3_board[r][c]
                    write_row -= 1
            for r in range(write_row, -1, -1):
                self.match3_board[r][c] = None

        # заполняем сверху новыми
        symbols = ["🌿", "🔥", "💧", "🌙", "⭐"]
        for r in range(self.match3_rows):
            for c in range(self.match3_cols):
                if self.match3_board[r][c] is None:
                    self.match3_board[r][c] = random.choice(symbols)

        if self.evil_wizard_hp <= 0:
            # победа — вызываем твой финал
            self.finish_final_battle(victory=True, destroyed_rows=len(matches))
        else:
            self.show_match3_board()

    def try_talk_with_wizard(self):
        self.clear_btns()
        self.text_label.setText(
            "Ты пытаешься заговорить с волшебником о том, что лес можно исцелить без разрушения.\n"
            "Он молчит долго, затем лишь усмехается.\n\n"
            "— Посмотрим, чья воля окажется сильнее, — шепчет он.\n"
            "Мир вокруг темнеет, и воздух наполняется искрами магии."
        )
        self.add_btn("Подготовиться к противостоянию", self.prepare_final_battle)

    def start_match3_battle(self):
        self.clear_btns()
        self.evil_wizard_hp = 10
        self.match3_turns_left = 5
        self.text_label.setText(
            "Перед твоим взором вспыхивает магическая решётка — плетение чар злого волшебника.\n"
            "Каждый разрушенный ряд ослабляет его, но время ограничено."
        )
        self.update_match3_status()

    def update_match3_status(self):
        self.clear_btns()
        self.text_label.setText(
            f"HP злого волшебника: {self.evil_wizard_hp}\n"
            f"Оставшихся ходов: {self.match3_turns_left}\n\n"
            "Нажми, чтобы попытаться сложить ряды и разрушить часть чар."
        )
        self.add_btn("Сделать ход", self.match3_do_turn)
        self.add_btn("Попробовать говорить вместо боя", self.try_talk_with_wizard)

    def match3_do_turn(self):
        import random
        if self.evil_wizard_hp <= 0 or self.match3_turns_left <= 0:
            return

        destroyed_rows = random.randint(0, 3)
        damage = destroyed_rows  # 1 HP за ряд

        self.match3_turns_left -= 1
        self.evil_wizard_hp = max(0, self.evil_wizard_hp - damage)

        if self.evil_wizard_hp <= 0:
            self.finish_final_battle(victory=True, destroyed_rows=destroyed_rows)
        elif self.match3_turns_left <= 0:
            self.finish_final_battle(victory=False, destroyed_rows=destroyed_rows)
        else:
            text = (
                f"Ты меняешь местами магические символы.\n"
                f"Разрушено рядов: {destroyed_rows}.\n"
                f"HP волшебника теперь: {self.evil_wizard_hp}.\n"
            )
            self.text_label.setText(text)
            self.clear_btns()
            self.add_btn("Продолжить битву", self.update_match3_status)

    def finish_final_battle(self, victory: bool, destroyed_rows: int):
        self.clear_btns()
        elapsed = time.perf_counter() - self.match3_start_time

        if victory:
            base_text = (
                "Последние ряды чар рушатся, и сила злого волшебника рассыпается искрами.\n"
                "Лес вздыхает с облегчением, а туман начинает таять.\n\n"
            )
        else:
            base_text = (
                "Чар оказалось слишком много, и лес снова надолго тонет в тумане.\n"
                "Но лес запомнит твою попытку.\n\n"
            )

        stats_text = (
            "Статистика битвы:\n"
            f"  • Время битвы: {elapsed:.1f} секунд\n"
            f"  • Сделано ходов: {self.match3_turns}\n"
            f"  • Нанесённый урон: {self.match3_damage_done} HP\n"
        )

        self.text_label.setText(base_text + stats_text)

        # дальше можно звать кармический финал
        self.add_btn("Посмотреть, что будет дальше", self.show_karma_ending)

    def show_karma_ending(self):
        karma = self.session.karma
        self.clear_btns()
        self.show_evil_wizard(False)

        if karma < 0:
            self.set_background("dark_forest.jpg")  # мрачный лес
            self.text_label.setText(
                "Лес исцелен, но помнит все твои жестокие и эгоистичные поступки.\n"
                "Корни обвиваются вокруг тропинок, не отпуская тебя прочь.\n"
                "Ты чувствуешь, что останешься здесь навеки — сторожить этот лес вместо Лешего."
            )
            self.save_run_result("Тёмный финал: сторож леса")
            self.add_btn("Посмотреть итоговый график", self.show_battle_chart)

        elif 0 <= karma <= 6:
            self.set_background("forest_twilight.jpg")
            self.text_label.setText(
                "Ты остаёшься в лесу, помогая Лешему и другим духам.\n"
                "Иногда тебе кажется, что мир людей был всего лишь сном.\n"
                "Но лес шепчет, что ты сделал правильный выбор."
            )
            self.save_run_result("Нейтральный финал: хранитель леса")
            self.add_btn("Посмотреть итоговый график", self.show_battle_chart)

        else:  # karma > 6
            self.set_background("forest_sunrise.jpg")
            self.text_label.setText(
                "Лес благодарно шепчет твоё имя.\n"
                "Каждый шаг, каждое решение отзывалось добром.\n\n"
                "На мгновение туман раскрывает тропу домой — чистую, светлую, как новый лист."
            )
            self.save_run_result("Добрый финал: герой леса")
            self.add_btn("Посмотреть итоговый график", self.show_battle_chart)

    def show_battle_chart(self):
        # скрываем персонажей, фон оставляем или ставим нейтральный
        self.show_leshy(False)
        self.show_imp(False)
        self.show_vodyanoy(False)
        self.show_evil_wizard(False)

        self.clear_btns()
        self.text_label.setText("")  # текст не нужен, только график

        results = self.load_all_results()
        if not results:
            self.text_label.setText("Пока нет данных для графика.")
            self.add_btn("В главное меню", self.return_to_main_menu)
            return

        # сортировка по времени и топ-5
        results_sorted = sorted(results, key=lambda r: r.get("time_seconds", 999999))
        top = results_sorted[:5]

        # забираем размер области под график (по bg_label)
        bg_rect = self.bg_label.contentsRect()
        width = bg_rect.width()
        height = bg_rect.height()
        if width <= 0 or height <= 0:
            width, height = 800, 400

        pix = QPixmap(width, height)
        pix.fill(QColor(0, 0, 0, 0))

        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # фон графика
        painter.fillRect(0, 0, width, height, QColor(20, 35, 55, 230))

        # отступы
        margin_left = 80
        margin_right = 40
        margin_top = 40
        margin_bottom = 60

        chart_width = width - margin_left - margin_right
        chart_height = height - margin_top - margin_bottom

        # оси
        painter.setPen(QPen(QColor(220, 220, 220), 2))
        # вертикальная
        painter.drawLine(margin_left, margin_top, margin_left, margin_top + chart_height)
        # горизонтальная
        painter.drawLine(margin_left, margin_top + chart_height,
                         margin_left + chart_width, margin_top + chart_height)

        # данные
        times = [r["time_seconds"] for r in top]
        max_time = max(times) if times else 1

        # ширина одного столбца
        bar_count = len(top)
        bar_spacing = 20
        bar_width = (chart_width - bar_spacing * (bar_count + 1)) / max(bar_count, 1)

        # подпись осей
        painter.setPen(QPen(QColor(230, 230, 230), 1))
        painter.setFont(QFont("Arial", 10))

        painter.drawText(margin_left, margin_top - 10, "Время прохождения (сек)")
        painter.drawText(margin_left, margin_top + chart_height + 40, "Топ 5 игроков")

        # сами столбцы
        for i, r in enumerate(top):
            t = r["time_seconds"]
            ratio = t / max_time if max_time > 0 else 0
            bar_h = int(chart_height * ratio)

            x = margin_left + bar_spacing + i * (bar_width + bar_spacing)
            y = margin_top + chart_height - bar_h

            # цвет: чем быстрее, тем светлее
            brightness = 255 - int(120 * (t / max_time)) if max_time > 0 else 200
            painter.setBrush(QBrush(QColor(80, brightness, 150)))
            painter.setPen(QPen(QColor(30, 30, 60), 1))

            rect = QRect(int(x), int(y), int(bar_width), int(bar_h))
            painter.drawRect(rect)

            # подпись имени и времени
            painter.setPen(QPen(QColor(240, 240, 240), 1))
            name = r["name"][:10]  # чтобы не залезало
            painter.drawText(rect.x(), rect.bottom() + 15, name)
            painter.drawText(rect.x(), rect.bottom() + 30, r["time_str"])

        painter.end()

        # показываем график
        self.chart_label.setPixmap(pix)
        self.chart_label.setGeometry(bg_rect)
        self.chart_label.show()

        # кнопки
        self.add_btn("В главное меню", self.return_to_main_menu)

    def back_to_main_menu(self):
        # возвращаем вид на экран меню
        self.stack.setCurrentIndex(0)


    # ---------- Фон и спрайты ----------

    def set_background(self, image_name: str):
        print("SET_BACKGROUND CALLED WITH:", image_name)
        path = resource_path(os.path.join("images", image_name))
        print("BACKGROUND PATH:", path)
        if not os.path.exists(path):
            print(f"Файл фона не найден: {path}")
            self.bg_label.clear()
            return
        pix = QPixmap(path)
        self.bg_label.setPixmap(pix)
        self.update_leshy_geometry()
        self.update_imp_geometry()
        self.update_vodyanoy_geometry()
        self.update_evil_wizard_geometry()
        self.chart_label.hide()

    def show_leshy(self, visible: bool):
        path = resource_path(os.path.join("images", "leshy_sprite.png"))
        if visible and os.path.exists(path):
            pix = QPixmap(path)
            self.leshy_label.setPixmap(pix)
            self.leshy_label.show()
            self.update_leshy_geometry()
        else:
            self.leshy_label.hide()

    def show_vodyanoy(self, visible: bool):
        path = resource_path(os.path.join("images", "vodyanoy_sprite.png"))
        if visible and os.path.exists(path):
            pix = QPixmap(path)
            self.vodyanoy_label.setPixmap(pix)
            self.vodyanoy_label.show()
            self.update_vodyanoy_geometry()
        else:
            self.vodyanoy_label.hide()

    def show_evil_wizard(self, visible: bool):
        base_dir = os.path.dirname(__file__)
        path = os.path.join(base_dir, "images", "evil_wizard.png")  # своё имя файла
        if visible and os.path.exists(path):
            pix = QPixmap(path)
            self.evil_wizard_label.setPixmap(pix)
            self.evil_wizard_label.show()
            self.update_evil_wizard_geometry()
        else:
            self.evil_wizard_label.hide()

    def update_evil_wizard_geometry(self):
        if not self.evil_wizard_label.isVisible():
            return
        bg_rect = self.bg_label.contentsRect()
        if bg_rect.width() <= 0 or bg_rect.height() <= 0:
            return
        w = int(bg_rect.width() * 0.25)
        h = int(bg_rect.height() * 0.5)
        x = bg_rect.x() + int(bg_rect.width() * 0.65) - w // 2
        y = bg_rect.y() + bg_rect.height() - h - 10
        self.evil_wizard_label.setGeometry(x, y, w, h)

    def show_imp(self, visible: bool):
        path = resource_path(os.path.join("images", "imp_sprite.png"))
        if visible and os.path.exists(path):
            pix = QPixmap(path)
            self.imp_label.setPixmap(pix)
            self.imp_label.show()
            self.update_imp_geometry()
        else:
            self.imp_label.hide()

    def update_leshy_geometry(self):
        if not self.leshy_label.isVisible():
            return
        bg_rect = self.bg_label.contentsRect()
        w = int(bg_rect.width() * 0.25)
        h = int(bg_rect.height() * 0.45)
        x = bg_rect.x() + (bg_rect.width() - w) // 2
        y = bg_rect.y() + bg_rect.height() - h - 10
        self.leshy_label.setGeometry(x, y, w, h)

    def update_vodyanoy_geometry(self):
        if not self.vodyanoy_label.isVisible():
            return
        bg_rect = self.bg_label.contentsRect()
        if bg_rect.width() <= 0 or bg_rect.height() <= 0:
            return
        w = int(bg_rect.width() * 0.22)
        h = int(bg_rect.height() * 0.40)
        x = bg_rect.x() + int(bg_rect.width() * 0.30) - w // 2
        y = bg_rect.y() + bg_rect.height() - h - 10
        self.vodyanoy_label.setGeometry(x, y, w, h)

    def update_imp_geometry(self):
        if not self.imp_label.isVisible():
            return
        bg_rect = self.bg_label.contentsRect()
        if bg_rect.width() <= 0 or bg_rect.height() <= 0:
            return

        w = int(bg_rect.width() * 0.18)
        h = int(bg_rect.height() * 0.30)

        x_min = bg_rect.x() + int(bg_rect.width() * 0.1)
        x_max = bg_rect.x() + int(bg_rect.width() * 0.7) - w
        y_min = bg_rect.y() + int(bg_rect.height() * 0.2)
        y_max = bg_rect.y() + int(bg_rect.height() * 0.7) - h

        if x_max < x_min:
            x_max = x_min
        if y_max < y_min:
            y_max = y_min

        x = random.randint(x_min, x_max)
        y = random.randint(y_min, y_max)

        self.imp_label.setGeometry(x, y, w, h)
    def update_chart_geometry(self):
        if not self.chart_label.isVisible():
            return
        bg_rect = self.bg_label.contentsRect()
        w = int(bg_rect.width() * 0.5)
        h = int(bg_rect.height() * 0.35)
        x = bg_rect.x() + (bg_rect.width() - w) // 2
        y = bg_rect.y() + int(bg_rect.height() * 0.1)
        self.chart_label.setGeometry(x, y, w, h)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_leshy_geometry()
        self.update_imp_geometry()
        self.update_vodyanoy_geometry()
        self.update_evil_wizard_geometry()
        self.update_chart_geometry()

        # если идёт мини-игра, обновим позицию корзин
        if self.roots_left_basket and self.roots_left_basket.parent() is self.bg_label:
            bg_rect = self.bg_label.contentsRect()
            left_x = bg_rect.x() + int(bg_rect.width() * 0.15)
            right_x = bg_rect.x() + int(bg_rect.width() * 0.65)
            y = bg_rect.y() + int(bg_rect.height() * 0.55)
            self.roots_left_basket.move(left_x, y)
            self.roots_right_basket.move(right_x, y)

    # ---------- Вспомогательные ----------

    def clear_btns(self):
        while self.btn_layout.count():
            item = self.btn_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def add_btn(self, text: str, func):
        btn = QPushButton(text)
        btn.setFixedHeight(45)
        btn.clicked.connect(func)
        self.btn_layout.addWidget(btn)

    @property
    def btn_layout(self):
        return self.btn_container


if __name__ == "__main__":
    print(">>> STARTING APP <<<")
    app = QApplication(sys.argv)
    app.setStyleSheet(
        "QPushButton { font-size: 14px; padding: 10px; border-radius: 5px; background-color: #ecf0f1; } "
        "QPushButton:hover { background-color: #bdc3c7; }"
    )
    window = FairyQuestGame()
    window.show()
    sys.exit(app.exec())