WIDTH, HEIGHT = 1500, 980
UI_WIDTH = 360
DEFAULT_RENDER_FPS = 75
DEFAULT_SIM_FPS = DEFAULT_RENDER_FPS
MAX_SIM_STEPS_PER_FRAME = 64
SIM_TIME_BUDGET_MS = 4.0
BACKGROUND_COLOR = (20, 20, 30)
ATOM_COLOR = (100, 200, 255)
ATOM_POSITIVE_COLOR = (235, 80, 80)
ATOM_NEGATIVE_COLOR = (80, 140, 255)
ATOM_NEUTRAL_COLOR = ATOM_COLOR
WALL_COLOR = (200, 100, 100)
UI_COLOR = (240, 240, 240)
UI_BG_COLOR = (40, 40, 50)
UI_ACCENT_COLOR = (70, 130, 200)
VELOCITY_VECTOR_COLOR = (255, 255, 100)

DEFAULT_STRENGTH = 800.0
DEFAULT_TARGET_DIST = 60.0
DEFAULT_INTERACTION_RADIUS = 200.0
DEFAULT_DAMPING = 0.97
DEFAULT_MIN_DIST = 5.0
DEFAULT_WALL_BOUNCE = 0.8
DEFAULT_MASS = 1.0
MAGNET_STRENGTH = 2000.0

ATOM_NEUTRAL = 0
ATOM_POSITIVE = 1
ATOM_NEGATIVE = -1

MODE_REPEL = 0
MODE_ATTRACT = 1
MODE_KEEP_DIST = 2
MODE_NAMES = ["Отталкивание", "Притяжение", "Фикс. дистанция"]  # для совместимости, но в UI используются тексты из TEXTS

# External attraction modes
ATTRACT_NONE = 0
ATTRACT_CENTER = 1
ATTRACT_TOP_CENTER = 2
ATTRACT_BOTTOM_CENTER = 3
ATTRACT_LEFT_CENTER = 4
ATTRACT_RIGHT_CENTER = 5

# Тексты интерфейса на двух языках
TEXTS = {
    'ru': {
        'title': "Настройки",
        'strength': "Сила",
        'radius': "Радиус",
        'target_dist': "Целевое расстояние",
        'damping': "Затухание",
        'wall_bounce': "Отскок от стен",
        'magnet': "Магнит",
        'sim_fps': "Sim FPS",
        'render_fps': "Render FPS",
        'atom_type': "Тип атома",
        'external_attraction': "Внешнее притяжение",
        'mode_repel': "Отталкивание",
        'mode_attract': "Притяжение",
        'mode_fixed': "Фикс. дистанция",
        'clear_walls': "Очистить стены",
        'clear_atoms': "Очистить атомы",
        'neutral': "Нейтральный",
        'positive': "Красный +",
        'negative': "Синий -",
        'magnet_toggle': "Магнит +/-",
        'attract_none': "Нет",
        'attract_center': "Центр",
        'attract_top': "Верх",
        'attract_bottom': "Низ",
        'attract_left': "Лево",
        'attract_right': "Право",
        'language': "Язык",
        'help': [
            "Мышь:",
            "ЛКМ - добавить атом",
            "Средняя - магнит",
            "ПКМ - удалить атом",
            "",
            "Клавиши:",
            "C/Delete - очистить атомы",
            "N - добавить 10 атомов",
            "B / Shift+B - стена",
            "K - очистить стены",
            "G - границы",
            "P - скорости",
            "Пробел - пауза",
            "R - сброс",
            "L - переключить язык",
        ]
    },
    'en': {
        'title': "Settings",
        'strength': "Strength",
        'radius': "Radius",
        'target_dist': "Target Dist",
        'damping': "Damping",
        'wall_bounce': "Wall Bounce",
        'magnet': "Magnet",
        'sim_fps': "Sim FPS",
        'render_fps': "Render FPS",
        'atom_type': "Atom type",
        'external_attraction': "External attraction",
        'mode_repel': "Repel",
        'mode_attract': "Attract",
        'mode_fixed': "Fixed",
        'clear_walls': "Clear walls",
        'clear_atoms': "Clear atoms",
        'neutral': "Neutral",
        'positive': "Red +",
        'negative': "Blue -",
        'magnet_toggle': "Magnet +/-",
        'attract_none': "None",
        'attract_center': "Center",
        'attract_top': "Top",
        'attract_bottom': "Bottom",
        'attract_left': "Left",
        'attract_right': "Right",
        'language': "Language",
        'help': [
            "Mouse:",
            "LMB - add atom",
            "Middle - magnet",
            "RMB - remove atom",
            "",
            "Keys:",
            "C/Delete - clear atoms",
            "N - add 10 atoms",
            "B / Shift+B - wall",
            "K - clear walls",
            "G - boundaries",
            "P - velocities",
            "Space - pause",
            "R - reset",
            "L - toggle language",
        ]
    }
}