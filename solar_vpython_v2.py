# solar_vpython_v2.py
# VPython Solar System (v2) - Adds Hindi names, click-for-info, camera auto-fly, presets, realistic/visible scale toggle
# Requirements: pip install vpython
# Run: python solar_vpython_v2.py

from vpython import *
import math, time, random

# ---------- Raw planet data ----------
# name_en, name_hi, true_distance_AU (for reference), visual_distance, true_radius_km (for reference), visual_radius, color, orbital_period_days
planet_data = [
    ("Mercury", "बुध (Budh)", 0.39, 1.0, 2440, 0.03, color.gray(0.6), 88),
    ("Venus",   "शुक्र (Shukra)", 0.72, 1.5, 6052, 0.06, color.orange, 225),
    ("Earth",   "पृथ्वी (Prithvi)", 1.0, 2.0, 6371, 0.065, color.blue, 365),
    ("Mars",    "मंगल (Mangal)", 1.52, 2.6, 3390, 0.05, color.red, 687),
    ("Jupiter", "बृहस्पति (Brihaspati)", 5.2, 4.5, 69911, 0.18, color.yellow, 4333),
    ("Saturn",  "शनि (Shani)", 9.58, 6.0, 58232, 0.15, color.white, 10759),
    ("Uranus",  "अरुण (Arun)", 19.2, 7.5, 25362, 0.12, color.cyan, 30687),
    ("Neptune", "वरुण (Varun)", 30.05, 8.5, 24622, 0.12, color.magenta, 60190)
]

# ---------- Two scale presets ----------
# Visible (exaggerated so you can see) and Realistic (closer to true ratios, but still scaled)
scale_presets = {
    "visible": {"scale_distance": 1.6, "scale_radius": 10, "speed_multiplier": 0.5},
    "realistic": {"scale_distance": 0.8, "scale_radius": 1.2, "speed_multiplier": 0.5}
}
current_scale_mode = "visible"
scale = scale_presets[current_scale_mode]

# ---------- Scene ----------
scene.title = "3D Solar System - VPython v2 (Click planets, camera presets, auto-fly)"
scene.width = 1100
scene.height = 700
scene.background = color.black
scene.autoscale = False
scene.range = 10

scene.caption = """
Controls:
- Mouse drag: rotate view
- Mouse scroll / pinch: zoom
- Click a planet to show details
- Space: Pause/Resume
- +/- keys: Speed up / Slow down
"""

# ---------- Sun ----------
sun = sphere(pos=vector(0,0,0), radius=0.1*scale["scale_radius"], color=color.orange, emissive=True)
local_light(pos=vector(0,0,0), color=color.white)
sun_glow = sphere(pos=sun.pos, radius=sun.radius*2.2, color=color.orange, opacity=0.08)

# ---------- Stars ----------
stars = []
for i in range(220):
    theta = random.random()*2*math.pi
    phi = math.acos(2*random.random()-1)
    r = random.uniform(15, 35)
    x = r*math.sin(phi)*math.cos(theta)
    y = r*math.sin(phi)*math.sin(theta)
    z = r*math.cos(phi)
    s = sphere(pos=vector(x,y,z), radius=0.02, color=color.white, emissive=True, opacity=0.8)
    stars.append(s)

# ---------- Create planets, rings, labels ----------
planets = []
labels = []
for idx, (ename, hname, true_au, vis_dist, true_km, vis_rad, col, period) in enumerate(planet_data):
    R = vis_dist * scale["scale_distance"]
    r_vis = vis_rad * scale["scale_radius"] / 2.8
    p = sphere(pos=vector(R,0,0), radius=r_vis, color=col, make_trail=True, retain=300, shininess=0.6)
    ang_speed = (2*math.pi) / period
    ring = curve(pos=[vector(R*math.cos(t), R*math.sin(t), 0) for t in [i*0.05 for i in range(0, int(2*math.pi/0.05))]], color=color.white, radius=0.002, opacity=0.18)
    lbl = label(pos=p.pos, text=f"{ename}\n{hname}", xoffset=0, yoffset=20, space=20, height=10, border=4, font='sans')
    planets.append({
        "ename": ename, "hname": hname, "obj": p, "radius": R, "ang": 0.0, "ang_speed": ang_speed, "period": period,
        "true_au": true_au, "true_km": true_km, "vis_dist": vis_dist, "vis_rad": vis_rad
    })
    labels.append(lbl)

# ---------- UI Widgets ----------
speed_scale = scale["speed_multiplier"]
is_paused = False
auto_fly = False
camera_presets = []
preset_index = -1

# Info pane (right side)
info_slot = wtext(text="\n\nClick a planet to see details here.\n", pos=None)
wtext(text="\n\n")  # spacing

# Speed slider
def set_speed(s):
    global speed_scale
    speed_scale = s.value
speed_slider = slider(min=0.05, max=4.0, value=speed_scale, length=200, bind=set_speed, right=15)
wtext(text='  Speed scale\n\n')

# Zoom slider
def set_zoom(s):
    scene.range = s.value
zoom_slider = slider(min=5, max=40, value=scene.range, length=200, bind=set_zoom, right=15)
wtext(text='  Camera range\n\n')

# Pause button
def toggle_pause(b):
    global is_paused
    is_paused = not is_paused
    b.text = "Resume" if is_paused else "Pause"
btn_pause = button(text="Pause", bind=toggle_pause, right=15)

# Scale toggle (visible / realistic)
def toggle_scale(b):
    global current_scale_mode, scale
    current_scale_mode = "realistic" if current_scale_mode=="visible" else "visible"
    scale = scale_presets[current_scale_mode]
    b.text = f"Scale: {current_scale_mode}"
    # update planets sizes & radii immediately
    for idx, pdata in enumerate(planets):
        pdata["radius"] = pdata["vis_dist"] * scale["scale_distance"]
        pdata["obj"].radius = pdata["vis_rad"] * scale["scale_radius"] / 2.8
        # reposition to current angle
        a = pdata["ang"]
        x = pdata["radius"] * math.cos(a)
        y = pdata["radius"] * math.sin(a)
        z = 0.07 * pdata["radius"] * math.sin(a*0.5 + idx)
        pdata["obj"].pos = vector(x,y,z)
btn_scale = button(text=f"Scale: {current_scale_mode}", bind=toggle_scale, right=15)

# Auto-fly toggle
def toggle_autofly(b):
    global auto_fly
    auto_fly = not auto_fly
    b.text = "Auto-fly: On" if auto_fly else "Auto-fly: Off"
btn_autofly = button(text="Auto-fly: Off", bind=toggle_autofly, right=15)

# Save preset
def save_preset(b):
    global camera_presets, preset_index
    preset = {
        "center": scene.center,
        "range": scene.range,
        "forward": scene.forward,
        "up": scene.up
    }
    camera_presets.append(preset)
    preset_index = len(camera_presets)-1
    info_slot.text = info_slot.text + f"\nSaved preset #{preset_index+1}"
btn_save = button(text="Save preset", bind=save_preset, right=15)

# Next preset
def next_preset(b):
    global preset_index, camera_presets
    if not camera_presets:
        info_slot.text = info_slot.text + "\nNo presets saved yet."
        return
    preset_index = (preset_index + 1) % len(camera_presets)
    p = camera_presets[preset_index]
    scene.center = p["center"]
    scene.range = p["range"]
    scene.forward = p["forward"]
    scene.up = p["up"]
    info_slot.text = info_slot.text + f"\nLoaded preset #{preset_index+1}"
btn_next = button(text="Next preset", bind=next_preset, right=15)

# Reset view
def reset_view(b):
    scene.center = vector(0,0,0)
    scene.range = 10
    scene.forward = vector(0, -0.3, -1)
    scene.up = vector(0,1,0)
btn_reset = button(text="Reset view", bind=reset_view, right=15)

# ---------- Click handler: show planet info ----------
def on_mousedown(evt):
    # non-blocking handler; use scene.mouse.pick to find clicked object
    picked = scene.mouse.pick
    if picked is None:
        return
    # find which planet (match object)
    for pdata in planets:
        if pdata["obj"] is picked:
            # show info in right pane
            en = pdata["ename"]; hi = pdata["hname"]
            da = pdata["true_au"]; km = pdata["true_km"]; per = pdata["period"]
            info_slot.text = (f"\nSelected: {en} / {hi}\n"
                              f"Distance (AU): {da}\n"
                              f"Radius (km): {km}\n"
                              f"Orbital period (days): {per}\n"
                              f"Visual distance: {pdata['vis_dist']}\n")
            # temporarily highlight planet (pulse)
            orig_col = pdata["obj"].color
            pdata["obj"].color = color.white
            def restore(col, o):
                rate(30)
                time.sleep(0.08)
                o.color = col
            # simple delayed restore (non-blocking-ish)
            # we just schedule by setting a small attribute to check in main loop
            pdata["_pulse"] = {"time": time.time(), "orig": orig_col}
            return

scene.bind('mousedown', on_mousedown)

# ---------- Keyboard ----------
def keydown(evt):
    global speed_scale, is_paused
    s = evt.key
    if s == ' ':
        is_paused = not is_paused
        btn_pause.text = "Resume" if is_paused else "Pause"
    elif s == '+':
        speed_scale *= 1.2
        speed_slider.value = speed_scale
    elif s == '-':
        speed_scale /= 1.2
        speed_slider.value = speed_scale

scene.bind('keydown', keydown)

# ---------- Animation loop ----------
dt = 0.02
t_start = time.time()
while True:
    rate(1/dt)
    if is_paused:
        continue

    # update planets
    for i, pdata in enumerate(planets):
        R = pdata["radius"]
        # advance angle scaled by speed_scale
        pdata["ang"] += pdata["ang_speed"] * speed_scale * dt * 30
        a = pdata["ang"]
        x = R * math.cos(a)
        y = R * math.sin(a)
        z = 0.07 * R * math.sin(a*0.5 + i)
        pdata["obj"].pos = vector(x,y,z)
        labels[i].pos = pdata["obj"].pos + vector(0, pdata["obj"].radius*3.5, 0)
        # handle pulse restore if scheduled
        if "_pulse" in pdata:
            if time.time() - pdata["_pulse"]["time"] > 0.12:
                pdata["obj"].color = pdata["_pulse"]["orig"]
                del pdata["_pulse"]

    # sun glow pulsation
    sun_glow.radius = sun.radius * (2.0 + 0.06*math.sin(time.time()*0.6))

    # auto-fly camera: orbit the camera around center slowly
    if auto_fly:
        ang = 0.2 * (time.time() - t_start)
        dist = scene.range
        # compute a moving forward vector to simulate circling
        scene.forward = vector(math.cos(ang)*0.2, -0.3, math.sin(ang)*0.8)

    # small UI info update
    # keep info text minimal; UI widgets already show values
    # (we append nothing here to avoid spamming)
