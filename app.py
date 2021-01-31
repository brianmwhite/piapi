from flask import Flask
from flask import request
import sonos_control as sc
import hue_control

app = Flask(__name__)
# python3 -m flask run

##########################
# huego endpoints
##########################


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

###################################
# sonos sleep/whitenoise endpoints
###################################


@app.route("/sonos/sleep/owen")
def route_sonos_sleep_owen():
    return sc.sonos_whitenoise_start(sc.SONOS_OWENS_ROOM, 60)


@app.route("/sonos/wake/owen")
def sonos_wake_owen():
    return sc.sonos_whitenoise_stop(sc.SONOS_OWENS_ROOM)


@app.route("/sonos/sleep/bedroom")
def route_sonos_sleep_bedroom():
    return sc.sonos_whitenoise_start(sc.SONOS_BEDROOM)


@app.route("/sonos/wake/bedroom")
def route_sonos_wake_bedroom():
    return sc.sonos_whitenoise_stop(sc.SONOS_BEDROOM)

###################################
# sonos misc endpoints
###################################


@app.route("/sonos/downstairs/owen")
def route_sonos_play_owen_downstairs():
    return sc.sonos_play_owen_downstairs()


@app.route("/sonos/<speaker>/<playlist>")
def route_sonos_playlist(speaker, playlist):
    volume = request.args.get('volume')
    shuffle = request.args.get('shuffle')
    repeat = request.args.get('repeat')
    
    return sc.sonos_play_playlist(speaker, playlist, volume, shuffle, repeat)


@app.route("/sonos/officestop")
def route_sonos_office_stop():
    return sc.sonos_office_stop()


@app.route("/sonos/officeunmute")
def route_sonos_office_unmute():
    return sc.sonos_office_unmute()


@app.route("/sonos/ungroup/all")
def route_sonos_ungroup_all():
    return sc.sonos_ungroup_all()
