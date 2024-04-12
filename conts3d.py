import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.widgets import Button, RadioButtons, Slider
from mpl_toolkits.mplot3d import Axes3D

ENABLE_SAMPLING = False

__all__ = ["Axes3D"]

themes = {
    "☼": {"bg": "white", "fg": "black"},
    "☾": {"bg": "black", "fg": "white"},
    "🕹": {"bg": "black", "fg": "#3dcc3e"},
}


class Contour:
    directory: str
    lines: list = []
    name: str = ""
    current_line: int = 3
    subsample: list = []
    change: float = 2.5
    marks: list = []
    xlim: list = [999999, 0]
    ylim: list = [999999, 0]
    zlim: list = [999999, 0]

    def __init__(self, directory) -> None:
        super().__init__()
        self.directory = directory
        self.lines = self.load_contour_lines(directory)
        self.subsample = [0, len(self.lines)]
        self.name = os.path.basename(directory)

    def load_contour_lines(self, directory):
        lines = []
        for filename in os.listdir(directory):
            with open(os.path.join(directory, filename), "r") as f:
                file_lines = f.readlines()
                _z = float(file_lines[0].split()[1])
                self.zlim = [
                    _z if _z < self.zlim[0] else self.zlim[0],
                    _z if _z > self.zlim[1] else self.zlim[1],
                ]
                x, y, z = [], [], []
                for file_line in file_lines[1:]:
                    _y, _x = file_line.split()
                    _x = float(_x)
                    _y = float(_y)
                    self.xlim = [
                        _x if _x < self.xlim[0] else self.xlim[0],
                        _x if _x > self.xlim[1] else self.xlim[1],
                    ]
                    self.ylim = [
                        _y if _y < self.ylim[0] else self.ylim[0],
                        _y if _y > self.ylim[1] else self.ylim[1],
                    ]
                    x.append(_x)
                    y.append(_y)
                    z.append(_z)
                lines.append({"z": z, "x": x, "y": y})
        lines.sort(key=lambda point: point["z"][0])
        return lines

    def mark(self):
        """
        Marks current line and saves it to marks list
        -------
        Returns
        Returns True if mark added and false if mark removed
        """
        marked = self.current_line in self.marks
        getattr(self.marks, "remove" if marked else "append")(
            self.current_line * self.change
        )
        return marked

    @property
    def center_x(self):
        return sum(self.xlim) / 2

    @property
    def center_y(self):
        return sum(self.ylim) / 2

    @property
    def center_z(self):
        return sum(self.zlim) / 2

    @property
    def height(self):
        return self.zlim[1] - self.zlim[0]


def draw() -> None:
    contour: Contour = settings.contours[settings.contour_index]

    for axis in settings.axes.values():
        xlim = axis.get_xlim()
        ylim = axis.get_ylim()
        zlim = axis.get_zlim() if isinstance(axis, Axes3D) else []
        axis.cla()
        axis.set_xlabel("Pixels", color=themes[settings.theme_color]["fg"])
        axis.set_ylabel("Pixels", color=themes[settings.theme_color]["fg"])
        axis.set_xlim(*xlim)
        axis.set_ylim(*ylim)
        if isinstance(axis, Axes3D):
            axis.set_zlim(*zlim)

        # Hides all the axis stuff
        # if not settings.grid:
        #     axis.set_axis_off()

        if isinstance(axis, Axes3D):
            axis.set_zlabel("MM", color=themes[settings.theme_color]["fg"])
            # axis.set_zlim(contour.zlim)

    # Vectors Start
    data = np.loadtxt(os.path.join(os.getcwd(), "contours_vectors", "vectors.stance"))
    origin = data[0, :3]
    # Plot unit vectors (assumed to be rows 2 to 4 in the data)
    for i in range(1, 4):
        settings.axes["stance"].quiver(
            *origin,
            *(data[i, :3] * 54),
            color="maroon",
            linewidth=2,
            arrow_length_ratio=0.1,
            alpha=0.5,
        )
    # Femoral shaft vector
    femoral_origin = data[5, :3]
    femoral_direction = data[4, :3] * 30  # scaling factor applied
    settings.axes["stance"].quiver(
        *femoral_origin,
        *femoral_direction,
        color="gold",
        linewidth=2,
        arrow_length_ratio=0.1,
        alpha=0.5,
    )
    # Force vector
    force_origin = data[7, :3]
    force_direction = (
        data[6, :3] * 30
    )  # scaling factor applied, direction assumed from data structure
    settings.axes["stance"].quiver(
        *force_origin,
        *force_direction,
        color="red",
        linewidth=2,
        arrow_length_ratio=0.1,
        alpha=0.5,
    )
    # Vectors END
    for line in contour.lines[int(contour.subsample[0]) : int(contour.subsample[1])]:
        line_color = themes[settings.theme_color]["fg"]
        if line["z"][0] in contour.marks:
            line_color = "blue"
        if contour.current_line * contour.change == line["z"][0]:
            line_color = "#FF00FF"
        if (
            contour.current_line * contour.change == line["z"][0]
            and line["z"][0] in contour.marks
        ):
            line_color = "#8000FF"
        for axis in settings.axes.values():
            if isinstance(axis, Axes3D):
                axis.plot(
                    line["x"], line["y"], line["z"], color=line_color, linewidth=0.3
                )
            if (
                isinstance(axis, Axes)
                and contour.current_line * contour.change == line["z"][0]
            ):
                settings.axes["contour"].plot(line["x"], line["y"], color=line_color)

    settings.figure.canvas.draw_idle()


def generate_axes(fig: Figure) -> dict[str, Axes3D | Axes]:
    # Created with https://tombohub.github.io/matplotlib-layout-generator/
    gridspec = fig.add_gridspec(nrows=10, ncols=12)
    plt.subplots_adjust(wspace=0, hspace=0)
    fig.tight_layout()

    return {
        "stance": fig.add_subplot(gridspec[0:5, 0:6], projection="3d"),
        "fall": fig.add_subplot(gridspec[5:10, 0:6], projection="3d"),
        "contour": fig.add_subplot(gridspec[0:5, 6:12]),
    }


def set_theme(label: str) -> None:
    settings.theme_color = label
    for axis in settings.axes.values():
        axis.set_xlabel("X Label", color=themes[label]["fg"])
        axis.set_ylabel("Y Label", color=themes[label]["fg"])
        axis.set_facecolor(themes[label]["bg"])
        axis.spines["bottom"].set_color(themes[label]["fg"])
        axis.spines["top"].set_color(themes[label]["fg"])
        axis.spines["left"].set_color(themes[label]["fg"])
        axis.spines["right"].set_color(themes[label]["fg"])
        axis.xaxis.label.set_color(themes[label]["fg"])
        axis.yaxis.label.set_color(themes[label]["fg"])
        axis.tick_params(axis="both", colors=themes[label]["fg"])
        if isinstance(axis, Axes3D):
            axis.set_ylabel("Z Label", color=themes[label]["fg"])
            axis.zaxis.label.set_color(themes[label]["fg"])
    settings.figure.set_facecolor(themes[label]["bg"])
    draw()


def on_move(event):
    if not isinstance(event.inaxes, Axes3D):
        return
    for axis in settings.axes.values():
        if event.inaxes == axis:
            continue
        axis.set_xlim(*event.inaxes.get_xlim())
        axis.set_ylim(*event.inaxes.get_ylim())
        if isinstance(axis, Axes3D):
            axis.view_init(elev=event.inaxes.elev, azim=event.inaxes.azim)
            axis.set_zlim(event.inaxes.get_zlim())
    settings.figure.canvas.draw_idle()


def on_press(event) -> None:
    contour: Contour = settings.contours[settings.contour_index]
    match event.key:
        case "j":
            # Move down contour line
            original_line = contour.current_line
            settings.contours[settings.contour_index].current_line = (
                contour.current_line - 1
                if contour.current_line > 1
                else (len(contour.lines) - 1)
            )
            if ENABLE_SAMPLING:
                settings.contours[settings.contour_index].subsample = [
                    settings.contours[settings.contour_index].current_line,
                    original_line + 1,
                ]
            draw()
        case "k":
            # Move up contour line
            original_line = contour.current_line
            settings.contours[settings.contour_index].current_line = (
                contour.current_line + 1
                if contour.current_line < len(contour.lines)
                else 0
            )
            if ENABLE_SAMPLING:
                settings.contours[settings.contour_index].subsample = [
                    original_line,
                    settings.contours[settings.contour_index].current_line + 1,
                ]
            draw()
        case "left":
            # Previous contour
            settings.contour_index = (
                settings.contour_index - 1
                if settings.contour_index > 0
                else len(settings.contours) - 1
            )
            settings.figure.canvas.manager.set_window_title(
                settings.contours[settings.contour_index].name
            )
            draw()
        case "l":
            # Next contour
            settings.contour_index = (
                settings.contour_index + 1
                if settings.contour_index < len(settings.contours) - 1
                else 0
            )
            settings.figure.canvas.manager.set_window_title(
                settings.contours[settings.contour_index].name
            )
            draw()
        case " ":
            settings.contours[settings.contour_index].mark()
            draw()
        case _:
            print(f"Pressed: {event.key}")


def slide(contour_line):
    settings.contours[settings.contour_index].current_line = contour_line
    save_button.label.set_text(
        "Unmark"
        if contour_line in settings.contours[settings.contour_index].marks
        else "Mark"
    )
    draw()


def toggle_grid(_):
    settings.grid = not settings.grid
    draw()


class SETTINGS:

    theme_color = "☼"
    grid = False
    axes: dict[str, Axes | Axes3D]
    CONTOUR_DIRECTORY = os.path.join(os.getcwd(), "contours")
    contour_index = 0
    contours: list[Contour] = []
    figure: Figure


def mark(_) -> None:
    save_button.label.set_text(
        "Mark" if settings.contours[settings.contour_index].mark() else "Undo"
    )
    draw()


if __name__ == "__main__":

    # Plots
    settings = SETTINGS()
    settings.figure = plt.figure()
    settings.contours = [
        Contour(os.path.join(settings.CONTOUR_DIRECTORY, directory))
        for directory in os.listdir(settings.CONTOUR_DIRECTORY)
    ]
    contour = settings.contours[settings.contour_index]
    settings.figure.canvas.manager.set_window_title(contour.name)
    settings.axes = generate_axes(settings.figure)
    for axis in settings.axes.values():
        if isinstance(axis, Axes3D):
            axis.view_init(elev=0, azim=90)

    # GUI

    theme_buttons_location = plt.axes((0.91, 0.05, 0.05, 0.075))
    save_button_axis = plt.axes((0.81, 0.05, 0.1, 0.075))
    save_button = Button(save_button_axis, "Mark")
    save_button.on_clicked(mark)
    radio = RadioButtons(theme_buttons_location, tuple(key for key in themes))
    radio.on_clicked(set_theme)
    slider_axis = plt.axes((0.2, 0.01, 0.65, 0.03), facecolor="lightgoldenrodyellow")
    slider = Slider(
        slider_axis,
        "Z Max",
        contour.zlim[0],
        contour.zlim[1] / contour.change,
        valinit=contour.current_line,
        valstep=1,
    )
    slider.on_changed(slide)

    # Register Events
    _ = settings.figure.canvas.mpl_connect("motion_notify_event", on_move)
    _ = settings.figure.canvas.mpl_connect("button_release_event", on_move)
    _ = settings.figure.canvas.mpl_connect("key_press_event", on_press)
    draw()

    for axis in settings.axes.values():
        axis.set_xlim(
            contour.center_x - contour.height / 2, contour.center_x + contour.height / 2
        )
        axis.set_ylim(
            contour.center_y - contour.height / 2, contour.center_y + contour.height / 2
        )
        if isinstance(axis, Axes3D):
            axis.set_zlim(0, contour.height)
    plt.show()
