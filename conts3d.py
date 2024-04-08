import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, RadioButtons, Slider
from mpl_toolkits.mplot3d import Axes3D

__all__ = ["Axes3D"]

color_index = 0  # Current color index
# Your data loading code remains unchanged
contour_lines = []

global settings
settings = {"current_line": 30, "theme_color": "☼", "saves": []}
themes = {
    "☼": {"bg": "white", "fg": "black"},
    "☾": {"bg": "black", "fg": "white"},
    "🕹": {"bg": "black", "fg": "#3dcc3e"},
}

change = 2.5
min_x = min_y = min_z = 999999
max_x = max_y = max_z = 0

for filename in os.listdir(os.path.join(os.getcwd(), "contours/c/")):
    with open(os.path.join(os.getcwd(), "contours", "c", filename), "r") as f:
        file_lines = f.readlines()
        _z = float(file_lines[0].split()[1])
        min_z = _z if _z < min_z else min_z
        max_z = _z if _z > max_z else max_z
        x, y, z = [], [], []
        for file_line in file_lines[1:]:
            _y, _x = file_line.split()
            _x = float(_x)
            _y = float(_y)
            min_x = _x if _x < min_x else min_x
            max_x = _x if _x > max_x else max_x

            min_y = _y if _y < min_y else min_y
            max_y = _y if _y > max_y else max_y
            x.append(_x)
            y.append(_y)
            z.append(_z)
        contour_lines.append({"z": z, "x": x, "y": y})
center_x = (max_x + min_x) / 2
center_y = (max_y + min_y) / 2
height_z = max_z - min_z
lim_min_x = center_x - (height_z / 2)
lim_max_x = center_x + (height_z / 2)
lim_min_y = center_y - (height_z / 2)
lim_max_y = center_y + (height_z / 2)


main_figure = plt.figure()
plt.subplots_adjust(wspace=0, hspace=0)
plot_vector_stance = main_figure.add_subplot(221, projection="3d")
plot_clean = main_figure.add_subplot(223, projection="3d")
plot_2D = main_figure.add_subplot(222)

theme_buttons_location = plt.axes((0.91, 0.05, 0.05, 0.075))
save_button_location = plt.axes((0.81, 0.05, 0.1, 0.075))
save_button = Button(save_button_location, "Save")


def save(_):
    if settings["current_line"] in settings["saves"]:
        settings["saves"].remove(settings["current_line"])
        save_button.label.set_text("Save")
    else:
        settings["saves"].append(settings["current_line"])
        save_button.label.set_text("Undo")
    draw()


save_button.on_clicked(save)

radio = RadioButtons(theme_buttons_location, tuple(key for key in themes.keys()))
plots3D = [plot_vector_stance, plot_clean]
plots2D = [plot_2D]
for plot in plots3D:
    plot.view_init(elev=20.0, azim=-35)


def theme(label):
    settings["theme_color"] = label
    for plot in plots3D + plots2D:
        plot.set_xlabel("X Label", color=themes[label]["fg"])
        plot.set_ylabel("Y Label", color=themes[label]["fg"])
        plot.set_facecolor(themes[label]["bg"])
        plot.spines["bottom"].set_color(themes[label]["fg"])
        plot.spines["top"].set_color(themes[label]["fg"])
        plot.spines["left"].set_color(themes[label]["fg"])
        plot.spines["right"].set_color(themes[label]["fg"])
        plot.xaxis.label.set_color(themes[label]["fg"])
        plot.yaxis.label.set_color(themes[label]["fg"])
        plot.tick_params(axis="x", colors=themes[label]["fg"])
        plot.tick_params(axis="y", colors=themes[label]["fg"])
        if plot in plots3D:
            plot.set_ylabel("Z Label", color=themes[label]["fg"])
            plot.tick_params(axis="z", colors=themes[label]["fg"])
            plot.zaxis.label.set_color(themes[label]["fg"])
    main_figure.set_facecolor(themes[label]["bg"])
    draw()


radio.on_clicked(theme)

# ax['color'].set_facecolor(radio_background)


# Adding a slider for controlling the Z plane visibility
ax_slider = plt.axes([0.2, 0.01, 0.65, 0.03], facecolor="lightgoldenrodyellow")
slider = Slider(
    ax_slider, "Z Max", min_z, max_z, valinit=settings["current_line"], valstep=change
)

# Update function for the slider
print("ylim", lim_max_y, lim_min_y)
print("xlim", lim_max_x, lim_min_x)
print("center_x", center_x)
print("center_y", center_y)


def draw():
    for plot in plots3D + plots2D:
        plot.cla()
        plot.set_xlabel("Pixels", color=themes[settings["theme_color"]]["fg"])
        plot.set_ylabel("Pixels", color=themes[settings["theme_color"]]["fg"])
        plot.set_xlim([lim_min_x, lim_max_x])
        plot.set_ylim([lim_min_y, lim_max_y])
        # Hides all the axis stuff
        plot.set_axis_off()
        if plot in plots3D:
            plot.set_zlabel("MM", color=themes[settings["theme_color"]]["fg"])
            plot.set_zlim([min_z, max_z])

    ## Vectors Start
    data = np.loadtxt(os.path.join(os.getcwd(), "contours_vectors", "vectors.stance"))
    origin = data[0, :3]
    # Plot unit vectors (assumed to be rows 2 to 4 in the data)
    for i in range(1, 4):
        plot_vector_stance.quiver(
            *origin,
            *(data[i, :3] * 54),
            color="maroon",
            linewidth=2,
            arrow_length_ratio=0.1,
            alpha=0.5
        )
    # Femoral shaft vector
    femoral_origin = data[5, :3]
    femoral_direction = data[4, :3] * 30  # scaling factor applied
    plot_vector_stance.quiver(
        *femoral_origin,
        *femoral_direction,
        color="gold",
        linewidth=2,
        arrow_length_ratio=0.1,
        alpha=0.5
    )
    # Force vector
    force_origin = data[7, :3]
    force_direction = (
        data[6, :3] * 30
    )  # scaling factor applied, direction assumed from data structure
    plot_vector_stance.quiver(
        *force_origin,
        *force_direction,
        color="red",
        linewidth=2,
        arrow_length_ratio=0.1,
        alpha=0.5
    )
    ## Vectors END
    for line in contour_lines:
        line_color = themes[settings["theme_color"]]["fg"]
        if line["z"][0] in settings["saves"]:
            line_color = "blue"
        if settings["current_line"] == line["z"][0]:
            line_color = "#FF00FF"
        if (
            settings["current_line"] == line["z"][0]
            and line["z"][0] in settings["saves"]
        ):
            line_color = "#8000FF"

        plot_vector_stance.plot(
            line["x"], line["y"], line["z"], color=line_color, linewidth=0.3
        )
        plot_clean.plot(
            line["x"], line["y"], line["z"], color=line_color, linewidth=0.3
        )
        if settings["current_line"] == line["z"][0]:
            plot_2D.plot(line["x"], line["y"], color=line_color)

    main_figure.canvas.draw_idle()


draw()


def on_move(event):
    if event.inaxes == plot_vector_stance:
        plot_clean.view_init(elev=plot_vector_stance.elev, azim=plot_vector_stance.azim)
        plot_clean.set_xlim(plot_vector_stance.get_xlim())
        plot_clean.set_ylim(plot_vector_stance.get_ylim())
        plot_clean.set_zlim(plot_vector_stance.get_zlim())
    elif event.inaxes == plot_clean:
        plot_vector_stance.view_init(elev=plot_clean.elev, azim=plot_clean.azim)
        plot_vector_stance.set_xlim(plot_clean.get_xlim())
        plot_vector_stance.set_ylim(plot_clean.get_ylim())
        plot_vector_stance.set_zlim(plot_clean.get_zlim())
    main_figure.canvas.draw_idle()


c1 = main_figure.canvas.mpl_connect("motion_notify_event", on_move)
c2 = main_figure.canvas.mpl_connect("button_release_event", on_move)


def slide(val):
    settings["current_line"] = val
    save_button.label.set_text(
        "Undo" if settings["current_line"] in settings["saves"] else "Save"
    )
    draw()


slider.on_changed(slide)
plt.show()
