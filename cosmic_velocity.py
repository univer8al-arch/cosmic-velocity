import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from matplotlib.patches import FancyArrowPatch, Circle
import matplotlib.animation as animation
from matplotlib.lines import Line2D


class CosmicVelocitySimulator:
    def __init__(self):
        self.fig = plt.figure(figsize=(16, 8))
        self.fig.suptitle('Первая космическая скорость на экваториальной планете',
                          fontsize=14, fontweight='bold', y=0.98)

        # Создаем сетку графиков с увеличенными отступами
        gs = self.fig.add_gridspec(2, 3, height_ratios=[3, 1],
                                   hspace=0.4, wspace=0.4,
                                   top=0.88, bottom=0.22)

        self.ax_planet = self.fig.add_subplot(gs[0, 0])  # Вид планеты
        self.ax_vectors = self.fig.add_subplot(gs[0, 1])  # Векторы скоростей
        self.ax_trajectory = self.fig.add_subplot(gs[0, 2])  # Траектория запуска
        self.ax_info = self.fig.add_subplot(gs[1, :])  # Информационная панель

        # Параметры планеты
        self.R = 6371  # км
        self.M = 5.97e24  # кг
        self.G = 6.67430e-11
        self.T = 5060  # секунд

        # Вычисляемые параметры
        self.omega = 2 * np.pi / self.T
        self.v_rotation = self.omega * (self.R * 1000)
        self.v1_cosmic = np.sqrt(self.G * self.M / (self.R * 1000))
        self.v_additional = self.v1_cosmic - self.v_rotation

        # Флаг для отслеживания, нужно ли обновлять траекторию
        self.trajectory_needs_update = True

        # Настройка графиков
        self.setup_planet_view()
        self.setup_vectors_view()
        self.setup_trajectory_view()
        self.setup_info_panel()

        # Добавляем элементы управления
        self.add_controls()

        # Анимация
        self.animation = None
        self.start_animation()

    def setup_planet_view(self):
        """Настройка вида планеты с экваториальной точкой"""
        self.ax_planet.clear()
        self.ax_planet.set_xlim(-self.R * 2, self.R * 2)
        self.ax_planet.set_ylim(-self.R * 2, self.R * 2)
        self.ax_planet.set_aspect('equal')
        self.ax_planet.grid(True, alpha=0.3)
        self.ax_planet.set_title('Планета и точка запуска', fontweight='bold')

        # Планета
        planet = Circle((0, 0), self.R, color='lightblue', alpha=0.7, ec='blue', linewidth=2)
        self.ax_planet.add_patch(planet)

        # Экваториальная линия
        self.ax_planet.axhline(y=0, color='red', linestyle='--', alpha=0.5, linewidth=1)

        # Точка запуска (будет анимироваться)
        self.launch_point, = self.ax_planet.plot([self.R], [0], 'ro', markersize=12,
                                                 markeredgecolor='darkred', markeredgewidth=2)

        # Маркер направления вращения
        theta = np.linspace(0, 2 * np.pi, 100)
        self.ax_planet.plot(self.R * 1.1 * np.cos(theta), self.R * 1.1 * np.sin(theta),
                            'g--', alpha=0.4, linewidth=1)

    def setup_vectors_view(self):
        """Настройка графика с векторами скоростей"""
        self.ax_vectors.clear()
        self.ax_vectors.set_xlim(-2, 12)
        self.ax_vectors.set_ylim(-2, 12)
        self.ax_vectors.set_aspect('equal')
        self.ax_vectors.grid(True, alpha=0.3)
        self.ax_vectors.set_title('Векторы скоростей (км/с)', fontweight='bold')
        self.ax_vectors.set_xlabel('Горизонтальная скорость')
        self.ax_vectors.set_ylabel('Вертикальная скорость')

    def setup_trajectory_view(self):
        """Настройка графика траектории"""
        self.ax_trajectory.clear()
        self.ax_trajectory.set_xlim(-self.R * 2, self.R * 2)
        self.ax_trajectory.set_ylim(-self.R * 2, self.R * 2)
        self.ax_trajectory.set_aspect('equal')
        self.ax_trajectory.grid(True, alpha=0.3)
        self.ax_trajectory.set_title('Траектория запуска', fontweight='bold')

        # Планета
        planet = Circle((0, 0), self.R, color='lightblue', alpha=0.3, ec='blue', linewidth=1)
        self.ax_trajectory.add_patch(planet)

        # Орбита
        theta = np.linspace(0, 2 * np.pi, 100)
        orbit_r = self.R * 1.5
        self.ax_trajectory.plot(orbit_r * np.cos(theta), orbit_r * np.sin(theta),
                                'r--', alpha=0.5, linewidth=1, label='Орбита')

    def setup_info_panel(self):
        """Информационная панель с параметрами в 2 столбца"""
        self.ax_info.clear()
        self.ax_info.axis('off')

        # Создаем два текстовых блока
        info_text_left = self.get_info_text_left()
        info_text_right = self.get_info_text_right()

        self.info_display_left = self.ax_info.text(0.25, 0.5, info_text_left,
                                                   transform=self.ax_info.transAxes,
                                                   fontsize=9, verticalalignment='center',
                                                   horizontalalignment='center',
                                                   fontfamily='monospace',
                                                   bbox=dict(boxstyle='round', facecolor='lightyellow',
                                                             alpha=0.9, edgecolor='orange'))

        self.info_display_right = self.ax_info.text(0.75, 0.5, info_text_right,
                                                    transform=self.ax_info.transAxes,
                                                    fontsize=9, verticalalignment='center',
                                                    horizontalalignment='center',
                                                    fontfamily='monospace',
                                                    bbox=dict(boxstyle='round', facecolor='lightyellow',
                                                              alpha=0.9, edgecolor='orange'))

    def get_info_text_left(self):
        """Формирование левого информационного текста (Параметры системы)"""
        return f"""
        ╔══════════════════════════════════╗
        ║      ПАРАМЕТРЫ СИСТЕМЫ          ║
        ╠══════════════════════════════════╣
        ║ Радиус:    {self.R:8.0f} км    ║
        ║ Период:    {self.T:8.1f} с     ║
        ║            {self.T / 3600:8.2f} ч     ║
        ║ Угл. ск.:  {self.omega:8.5f}   ║
        ║            рад/с                ║
        ╚══════════════════════════════════╝
        """

    def get_info_text_right(self):
        """Формирование правого информационного текста (Скорости и Решение)"""
        v_rot_km = self.v_rotation / 1000
        v1_km = self.v1_cosmic / 1000
        v_add_km = self.v_additional / 1000

        # Определяем направление запуска
        if self.v_additional > 0:
            direction = "ВЕРТИКАЛЬНО ВВЕРХ ↑"
        elif self.v_additional < 0:
            direction = "ВНИЗ ↓ (невозможно!)"
        else:
            direction = "Уже на орбите"

        return f"""
        ╔══════════════════════════════════╗
        ║     СКОРОСТИ И РЕШЕНИЕ          ║
        ╠══════════════════════════════════╣
        ║ Вращения: {v_rot_km:8.3f} км/с  ║
        ║ 1-я косм: {v1_km:8.3f} км/с     ║
        ║ Дополнит: {v_add_km:8.3f} км/с  ║
        ╠══════════════════════════════════╣
        ║ Решение:                        ║
        ║ {direction:^28}║
        ║                                 ║
        ║ v₁ = v_вращ(→) + v_доп(↑)      ║
        ╚══════════════════════════════════╝
        """

    def add_controls(self):
        """Добавление элементов управления"""
        # Слайдер радиуса - левее
        ax_radius = plt.axes([0.08, 0.10, 0.25, 0.03])
        self.slider_radius = Slider(ax_radius, 'Радиус (км)', 1000, 20000,
                                    valinit=self.R, valfmt='%d')

        # Слайдер периода - левее и ниже
        ax_period = plt.axes([0.08, 0.05, 0.25, 0.03])
        self.slider_period = Slider(ax_period, 'Период (с)', 100, 50000,
                                    valinit=self.T, valfmt='%d')

        # Кнопки - правее
        ax_weightless = plt.axes([0.70, 0.10, 0.12, 0.04])
        self.btn_weightless = Button(ax_weightless, 'Невесомость')
        self.btn_weightless.on_clicked(self.set_weightless)

        ax_earth = plt.axes([0.70, 0.04, 0.12, 0.04])
        self.btn_earth = Button(ax_earth, 'Земля')
        self.btn_earth.on_clicked(self.set_earth_params)

        # Подключаем события слайдеров
        self.slider_radius.on_changed(self.update_parameters)
        self.slider_period.on_changed(self.update_parameters)

    def set_weightless(self, event):
        """Установка условий невесомости"""
        self.omega = np.sqrt(self.G * self.M / (self.R * 1000) ** 3)
        self.T = 2 * np.pi / self.omega
        self.slider_period.set_val(self.T)

    def set_earth_params(self, event):
        """Установка параметров Земли"""
        self.R = 6371
        self.T = 86400  # 24 часа
        self.slider_radius.set_val(self.R)
        self.slider_period.set_val(self.T)

    def update_parameters(self, val):
        """Обновление параметров при изменении слайдеров"""
        self.R = self.slider_radius.val
        self.T = self.slider_period.val
        self.omega = 2 * np.pi / self.T

        # Пересчет скоростей
        self.v_rotation = self.omega * (self.R * 1000)
        self.v1_cosmic = np.sqrt(self.G * self.M / (self.R * 1000))
        self.v_additional = self.v1_cosmic - self.v_rotation

        # Устанавливаем флаг для обновления траектории
        self.trajectory_needs_update = True

        # Обновление графиков
        self.setup_planet_view()
        self.setup_trajectory_view()
        self.update_info()

        self.fig.canvas.draw_idle()

    def update_info(self):
        """Обновление информационной панели"""
        self.info_display_left.set_text(self.get_info_text_left())
        self.info_display_right.set_text(self.get_info_text_right())

    def start_animation(self):
        """Запуск анимации векторов"""
        # Сохраняем начальные значения для анимации
        self.anim_v_rot = self.v_rotation / 1000
        self.anim_v_add = self.v_additional / 1000
        self.anim_v1 = self.v1_cosmic / 1000

        def animate(frame):
            # Очищаем график векторов
            self.ax_vectors.clear()
            self.ax_vectors.set_xlim(-2, 12)
            self.ax_vectors.set_ylim(-2, 12)
            self.ax_vectors.set_aspect('equal')
            self.ax_vectors.grid(True, alpha=0.3)
            self.ax_vectors.set_title('Векторы скоростей (км/с)', fontweight='bold')
            self.ax_vectors.set_xlabel('Горизонтальная скорость')
            self.ax_vectors.set_ylabel('Вертикальная скорость')

            # Анимация - векторы "растут" со временем
            t = (frame % 100) / 100.0  # от 0 до 1

            # Используем сохраненные значения для плавной анимации
            v_rot_show = self.anim_v_rot
            v_add_show = self.anim_v_add
            v1_show = self.anim_v1

            # Точка отсчета
            self.ax_vectors.plot(0, 0, 'ko', markersize=8, zorder=5)

            # Вектор вращения (зеленый) - растет горизонтально
            v_rot_current = v_rot_show * t
            if v_rot_show > 0:
                self.ax_vectors.arrow(0, 0, v_rot_current, 0,
                                      head_width=0.3, head_length=0.3,
                                      fc='green', ec='darkgreen', linewidth=2,
                                      alpha=0.8, zorder=3,
                                      label=f'Вращение: {v_rot_show:.2f} км/с')

            # Дополнительный вектор (синий) - растет вертикально
            if v_add_show > 0:
                v_add_current = v_add_show * t
                self.ax_vectors.arrow(v_rot_current, 0, 0, v_add_current,
                                      head_width=0.3, head_length=0.3,
                                      fc='blue', ec='darkblue', linewidth=2,
                                      alpha=0.8, zorder=3,
                                      label=f'Дополнит.: {v_add_show:.2f} км/с')
            elif v_add_show < 0:
                v_add_current = v_add_show * t
                self.ax_vectors.arrow(v_rot_current, 0, 0, v_add_current,
                                      head_width=0.3, head_length=0.3,
                                      fc='orange', ec='darkorange', linewidth=2,
                                      alpha=0.8, zorder=3,
                                      label=f'Дополнит.: {v_add_show:.2f} км/с')

            # Результирующий вектор (красный) - диагональный
            v1_current = v1_show * t
            if v_rot_show != 0 or v_add_show != 0:
                angle = np.arctan2(v_add_show, v_rot_show) if v_rot_show != 0 else np.pi / 2 * np.sign(v_add_show)
                dx = v1_current * np.cos(angle)
                dy = v1_current * np.sin(angle)
                self.ax_vectors.arrow(0, 0, dx, dy,
                                      head_width=0.3, head_length=0.3,
                                      fc='red', ec='darkred', linewidth=3,
                                      alpha=0.9, zorder=4,
                                      label=f'1-я косм.: {v1_show:.2f} км/с')

                # Пунктирные линии проекций
                if v_rot_show != 0 and v_add_show != 0:
                    self.ax_vectors.plot([v_rot_current, v_rot_current], [0, v_add_current],
                                         'gray', linestyle=':', alpha=0.5)
                    self.ax_vectors.plot([0, v_rot_current], [v_add_current, v_add_current],
                                         'gray', linestyle=':', alpha=0.5)

            # Легенда
            self.ax_vectors.legend(loc='upper left', fontsize=8)

            # Анимация точки на планете
            angle_rot = (frame % 360) * np.pi / 180
            x_point = self.R * np.cos(angle_rot)
            y_point = self.R * np.sin(angle_rot)
            self.launch_point.set_data([x_point], [y_point])

            # Обновляем траекторию при необходимости
            if self.trajectory_needs_update:
                self.setup_trajectory_view()
                # Рисуем траекторию запуска
                if self.v_additional > 0:
                    # Рисуем орбиту
                    r_orbit = self.R * 1.2  # немного выше поверхности
                    theta = np.linspace(0, 2 * np.pi, 200)
                    self.ax_trajectory.plot(r_orbit * np.cos(theta), r_orbit * np.sin(theta),
                                            'orange', linewidth=2, alpha=0.7, label='Орбита')

                    # Точка старта
                    self.ax_trajectory.plot(self.R, 0, 'go', markersize=10,
                                            label='Точка старта')

                    # Стрелка направления запуска
                    arrow_length = self.R * 0.5
                    if self.v_additional > 0:
                        self.ax_trajectory.arrow(self.R, 0, 0, arrow_length,
                                                 head_width=self.R * 0.1, head_length=self.R * 0.2,
                                                 fc='blue', ec='darkblue', linewidth=2,
                                                 label='Направление запуска')

                    self.ax_trajectory.legend(loc='upper right', fontsize=8)

                self.trajectory_needs_update = False

            return [self.launch_point]

        # Создаем анимацию
        self.animation = animation.FuncAnimation(
            self.fig, animate, frames=360, interval=50, blit=False, repeat=True
        )

    def show(self):
        """Показ симуляции"""
        plt.show()


# Интерактивная демонстрация с пояснениями
def print_solution():
    print("""
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                РЕШЕНИЕ ЗАДАЧИ О ПЕРВОЙ КОСМИЧЕСКОЙ СКОРОСТИ        ║
    ╚══════════════════════════════════════════════════════════════════════╝

    📐 ФИЗИЧЕСКАЯ МОДЕЛЬ:

    1. Условие невесомости на экваторе:
       Центробежная сила = Сила гравитации
       m·ω²R = G·M·m/R²
       ω = √(G·M/R³)

    2. Скорость вращения экватора:
       v_rot = ω·R (горизонтальная составляющая)

    3. Первая космическая скорость:
       v₁ = √(G·M/R) (полная скорость для орбиты)

    4. Дополнительная скорость:
       v_add = v₁ - v_rot (вертикальная составляющая)

    🎯 ОТВЕТ НА ВОПРОС ЗАДАЧИ:

    Жители экваториальных районов должны запустить предмет
    ВЕРТИКАЛЬНО ВВЕРХ (перпендикулярно поверхности планеты)
    со скоростью:

    v_запуска = √(G·M/R) - ω·R

    📊 ВЕКТОРНОЕ СЛОЖЕНИЕ:

    Горизонтальная скорость (от вращения планеты)
    +
    Вертикальная скорость (от запуска)
    =
    Первая космическая скорость (под углом к горизонту)

    ┌─────────────────────────────────────────┐
    │  Жители запускают предмет ↑            │
    │  Планета "запускает" предмет →         │
    │  Результат: предмет на орбите ↗        │
    └─────────────────────────────────────────┘

    💡 ИНТЕРАКТИВНАЯ ДЕМОНСТРАЦИЯ:

    В программе вы можете:
    • Изменять радиус планеты и период вращения
    • Наблюдать анимированные векторы скоростей
    • Видеть траекторию запуска
    • Исследовать различные сценарии

    Попробуйте кнопку "Невесомость" для автоматической
    настройки условий задачи!
    """)


if __name__ == "__main__":
    print_solution()

    # Создаем и запускаем симуляцию
    sim = CosmicVelocitySimulator()
    sim.show()