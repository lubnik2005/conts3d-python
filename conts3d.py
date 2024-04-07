import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, RadioButtons, Slider
from mpl_toolkits.mplot3d import Axes3D
__all__ = ['Axes3D']

color_index = 0  # Current color index
# Your data loading code remains unchanged
contour_lines = []

global settings
settings = {"current_line": 30, "theme_color": "☼", "saves": []}
themes = {
    "☼": { 'bg' :"white", 'fg': "black"},
    "☾": {'bg': 'black', 'fg': 'white'},
    "🕹": {'bg': 'black', 'fg': '#3dcc3e'}
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


fig = plt.figure()
plt.subplots_adjust(wspace=0, hspace=0)
ax= fig.add_subplot(221, projection="3d")
ay = fig.add_subplot(223, projection="3d")
ab = fig.add_subplot(222)

# Button for changing background color
# ax_button = plt.axes([0.81, 0.05, 0.05, 0.075])  # Adjust these values as needed for your layout
ax_button = plt.axes(
    [0.91, 0.05, 0.05, 0.075]
)  # Adjust these values as needed for your layout
aw_button = plt.axes(
    [0.81, 0.05, 0.1, 0.075]
)  # Adjust these values as needed for your layout
save_button = Button(aw_button, "Save")


def save(event):
    if settings["current_line"] in settings["saves"]:
        settings["saves"].remove(settings["current_line"])
        save_button.label.set_text("Save")
    else:
        settings["saves"].append(settings["current_line"])
        save_button.label.set_text("Undo")
    draw()


save_button.on_clicked(save)

radio = RadioButtons(
    ax_button,
    (tuple(key for key in themes.keys())),
)
d = [ax, ay, ab]
d3 = [ax, ay]
for a in d:
    if a in d3:
        a.view_init(elev=20.0, azim=-35)


def theme(label):
    settings["theme_color"] = label
    # ax_button.set_facecolor(bg_colors[settings['theme_color']])
    for a in d:
        a.set_xlabel("X Label", color=themes[label]['fg'])
        a.set_ylabel("Y Label", color=themes[label]['fg'])
        a.set_facecolor(themes[label]['bg'])
        a.spines["bottom"].set_color(themes[label]['fg'])
        a.spines["top"].set_color(themes[label]['fg'])
        a.spines["left"].set_color(themes[label]['fg'])
        a.spines["right"].set_color(themes[label]['fg'])
        a.xaxis.label.set_color(themes[label]['fg'])
        a.yaxis.label.set_color(themes[label]['fg'])
        a.tick_params(axis="x", colors=themes[label]['fg'])
        a.tick_params(axis="y", colors=themes[label]['fg'])
        if a in d3:
            a.set_ylabel("Z Label", color=themes[label]['fg'])
            a.tick_params(axis="z", colors=themes[label]['fg'])
            a.zaxis.label.set_color(themes[label]['fg'])
    fig.set_facecolor(themes[label]['bg'])
    draw()


radio.on_clicked(theme)

# ax['color'].set_facecolor(radio_background)


# Adding a slider for controlling the Z plane visibility
ax_slider = plt.axes([0.2, 0.01, 0.65, 0.03], facecolor="lightgoldenrodyellow")
slider = Slider(ax_slider, "Z Max", min_z, max_z, valinit=settings['current_line'], valstep=change)

# Update function for the slider
print("ylim", lim_max_y, lim_min_y)
print("xlim", lim_max_x, lim_min_x)
print("center_x", center_x)
print("center_y", center_y)


def draw():
    for a in d:
        a.cla()
        a.set_xlabel("Pixels", color=themes[settings['theme_color']]['fg'])
        a.set_ylabel("Pixels", color=themes[settings['theme_color']]['fg'])
        a.set_xlim([lim_min_x, lim_max_x])
        a.set_ylim([lim_min_y, lim_max_y])
        # Hides all the axis stuff
        a.set_axis_off()
        if a in d3:
            a.set_zlabel("MM", color=themes[settings['theme_color']]['fg'])
            a.set_zlim([min_z, max_z])

    ## Vectors Start
    data = np.loadtxt(os.path.join(os.getcwd(), "contours_vectors", "vectors.stance"))
    origin = data[0, :3]
    # Plot unit vectors (assumed to be rows 2 to 4 in the data)
    for i in range(1, 4):
        ax.quiver(
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
    ax.quiver(
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
    ax.quiver(
        *force_origin,
        *force_direction,
        color="red",
        linewidth=2,
        arrow_length_ratio=0.1,
        alpha=0.5
    )
    ## Vectors END
    for line in contour_lines:
        line_color = themes[settings["theme_color"]]['fg']
        if line["z"][0] in settings["saves"]:
            line_color = "blue"
        if settings["current_line"] == line["z"][0]:
            line_color = "#FF00FF"
        if (
            settings["current_line"] == line["z"][0]
            and line["z"][0] in settings["saves"]
        ):
            line_color = "#8000FF"

        ax.plot(line["x"], line["y"], line["z"], color=line_color, linewidth=0.3)
        ay.plot(line["x"], line["y"], line["z"], color=line_color, linewidth=0.3)
        if settings["current_line"] == line["z"][0]:
            ab.plot(line["x"], line["y"], color=line_color)

    fig.canvas.draw_idle()


draw()


def on_move(event):
    if event.inaxes == ax:
        ay.view_init(elev=ax.elev, azim=ax.azim)
        ay.set_xlim(ax.get_xlim())
        ay.set_ylim(ax.get_ylim())
        ay.set_zlim(ax.get_zlim())
    elif event.inaxes == ay:
        ax.view_init(elev=ay.elev, azim=ay.azim)
        ax.set_xlim(ay.get_xlim())
        ax.set_ylim(ay.get_ylim())
        ax.set_zlim(ay.get_zlim())
    fig.canvas.draw_idle()


c1 = fig.canvas.mpl_connect("motion_notify_event", on_move)
c2 = fig.canvas.mpl_connect("button_release_event", on_move)


def slide(val):
    settings["current_line"] = val
    save_button.label.set_text(
        "Undo" if settings["current_line"] in settings["saves"] else "Save"
    )
    draw()


# aw = fig.add_subplot(111, projection='3d')
#
# # Coordinates for the 8 corners of the cube
# x = [0, 1, 1, 0, 0, 1, 1, 0]
# y = [0, 0, 1, 1, 0, 0, 1, 1]
# z = [0, 0, 0, 0, 1, 1, 1, 1]
#
# # Generate the list of sides to connect
# edges = [
#     (0, 1), (1, 2), (2, 3), (3, 0),  # Bottom face
#     (4, 5), (5, 6), (6, 7), (7, 4),  # Top face
#     (0, 4), (1, 5), (2, 6), (3, 7)   # Sides
# ]
#
# # Plot each edge
# for edge in edges:
#     aw.plot3D([x[edge[0]], x[edge[1]]], [y[edge[0]], y[edge[1]]], [z[edge[0]], z[edge[1]]], 'gray')
#
#
slider.on_changed(slide)
plt.show()

