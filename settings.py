WIDTH, HEIGHT = 1500, 980
UI_WIDTH = 440
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
DEFAULT_ATOM_RADIUS = 5

# Границы слайдеров
SLIDER_STRENGTH_MIN = 0
SLIDER_STRENGTH_MAX = 10000
SLIDER_INTERACTION_RADIUS_MIN = 20
SLIDER_INTERACTION_RADIUS_MAX = 1000
SLIDER_TARGET_DIST_MIN = 10
SLIDER_TARGET_DIST_MAX = 500
SLIDER_DAMPING_MIN = 0.5
SLIDER_DAMPING_MAX = 1.0
SLIDER_WALL_BOUNCE_MIN = 0.0
SLIDER_WALL_BOUNCE_MAX = 2.0
SLIDER_ATOM_RADIUS_MIN = 2
SLIDER_ATOM_RADIUS_MAX = 30
SLIDER_MAGNET_STRENGTH_MIN = 200
SLIDER_MAGNET_STRENGTH_MAX = 20000
SLIDER_SIM_FPS_MIN = 1
SLIDER_SIM_FPS_MAX = 2000
SLIDER_RENDER_FPS_MIN = 30
SLIDER_RENDER_FPS_MAX = 240

# Шаги для точной настройки
SLIDER_STRENGTH_STEP = 10
SLIDER_INTERACTION_RADIUS_STEP = 5
SLIDER_TARGET_DIST_STEP = 0.5
SLIDER_DAMPING_STEP = 0.001
SLIDER_WALL_BOUNCE_STEP = 0.01
SLIDER_ATOM_RADIUS_STEP = 1
SLIDER_MAGNET_STRENGTH_STEP = 50
SLIDER_SIM_FPS_STEP = 1
SLIDER_RENDER_FPS_STEP = 1

# Размер кнопок точной настройки
FINE_TUNE_BUTTON_SIZE = 26

# Количество процессов для распараллеливания расчёта сил (1 – отключено)
NUM_PROCESSES = 8  # установите, например, 4 или 8 для многоядерности

ATOM_NEUTRAL = 0
ATOM_POSITIVE = 1
ATOM_NEGATIVE = -1

MODE_REPEL = 0
MODE_ATTRACT = 1
MODE_KEEP_DIST = 2

ATTRACT_NONE = 0
ATTRACT_CENTER = 1
ATTRACT_LEFT = 2
ATTRACT_RIGHT = 3
ATTRACT_UP = 4
ATTRACT_DOWN = 5
ATTRACT_LEFT_CENTER = 6
ATTRACT_RIGHT_CENTER = 7
ATTRACT_TOP_CENTER = 8
ATTRACT_BOTTOM_CENTER = 9

TEXTS = {
    'ru': {
        'title': "Настройки",
        'strength': "Сила",
        'radius': "Радиус взаимодействия",
        'interaction_radius': "Радиус взаимодействия",
        'target_dist': "Целевое расстояние",
        'damping': "Затухание",
        'wall_bounce': "Отскок от стен",
        'atom_radius': "Размер атома",
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
        'attract_left': "Влево",
        'attract_right': "Вправо",
        'attract_up': "Вверх",
        'attract_down': "Вниз",
        'attract_left_center': "Влево (центр)",
        'attract_right_center': "Вправо (центр)",
        'attract_top_center': "Вверх (центр)",
        'attract_bottom_center': "Вниз (центр)",
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
        'radius': "Interaction Radius",
        'interaction_radius': "Interaction Radius",
        'target_dist': "Target Dist",
        'damping': "Damping",
        'wall_bounce': "Wall Bounce",
        'atom_radius': "Atom size",
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
        'attract_left': "Left",
        'attract_right': "Right",
        'attract_up': "Up",
        'attract_down': "Down",
        'attract_left_center': "Left (center)",
        'attract_right_center': "Right (center)",
        'attract_top_center': "Up (center)",
        'attract_bottom_center': "Down (center)",
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