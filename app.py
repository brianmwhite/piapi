from flask import Flask
import sonos_control
import hue_control

app = Flask(__name__)
#python3 -m flask run

@app.route("/videoalert/on")
def route_huego_video_on_action():
    return hue_control.huego_light_on_to_color("RED")

@app.route("/videoalert/off")
def route_huego_video_off_action():
    return hue_control.huego_light_on_to_color("OFF")

@app.route("/alert/setcolor/<color>")
def route_huego_alert_color_action(color):
    color_name = color.upper()
    return hue_control.huego_light_on_to_color(color_name)

@app.route("/sonos/sleep/all")
def route_sonos_sleep_all():
    return sonos_control.sonos_sleep_all()

@app.route("/sonos/wake/all")
def route_sonos_wake_all():
    return sonos_control.sonos_wake_all()

@app.route("/sonos/get_white_noise_state/owen")
def route_sonos_get_white_noise_state_owen():
    return sonos_control.sonos_get_white_noise_state_owen()

@app.route("/sonos/sleep/owen")
def route_sonos_sleep_owen():
    return sonos_control.sonos_sleep_owen()

@app.route("/sonos/wake/owen")
def sonos_wake_owen():
    return sonos_control.sonos_wake_owen()

@app.route("/sonos/downstairs/owen")
def route_sonos_play_owen_downstairs():
    return sonos_control.sonos_play_owen_downstairs()

@app.route("/sonos/get_white_noise_state/bedroom")
def route_sonos_get_white_noise_state_bedroom():
    return sonos_control.sonos_get_white_noise_state_bedroom()

@app.route("/sonos/sleep/bedroom")
def route_sonos_sleep_bedroom():
    return sonos_control.sonos_sleep_bedroom()

@app.route("/sonos/wake/bedroom")
def route_sonos_wake_bedroom():
    return sonos_control.sonos_wake_bedroom()

@app.route("/sonos/officestop")
def route_sonos_office_stop():
    return sonos_control.sonos_office_stop()

@app.route("/sonos/officeunmute")
def route_sonos_office_unmute():
    return sonos_control.sonos_office_unmute()

@app.route("/sonos/ungroup/all")
def route_sonos_ungroup_all():
    return sonos_control.sonos_ungroup_all()