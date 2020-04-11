from flask import Flask
import time
import requests

app = Flask(__name__)

sonos_api_url = "http://192.168.7.97:5005"
sonos_owens_room = "Owen%E2%80%99s%20Room"
sonos_bedroom = "Bedroom"
sonos_livingroom = "Living%20Room"

def sonos_api_call(action, url):
    r = requests.get(url)
    time.sleep(.25)
    print(f"{action}={r.json()}")
    return r.json()

@app.route("/sonos/sleep/all")
def sonos_sleep_all():
    sonos_api_call("[bedroom] pause", f"{sonos_api_url}/{sonos_bedroom}/pause")
    sonos_api_call("[living room] pause", f"{sonos_api_url}/{sonos_livingroom}/pause")
    sonos_api_call("[owen's room] pause", f"{sonos_api_url}/{sonos_owens_room}/pause")

    sonos_api_call("[bedroom]  ungroup", f"{sonos_api_url}/{sonos_bedroom}/leave")
    sonos_api_call("[living room] ungroup", f"{sonos_api_url}/{sonos_livingroom}/leave")
    sonos_api_call("[owen's room] ungroup", f"{sonos_api_url}/{sonos_owens_room}/leave")
    
    sonos_api_call("[bedroom] set volume", f"{sonos_api_url}/{sonos_bedroom}/volume/40")
    sonos_api_call("[living room] set volume", f"{sonos_api_url}/{sonos_livingroom}/volume/50")
    sonos_api_call("[owen's room] set volume", f"{sonos_api_url}/{sonos_owens_room}/volume/60")
    
    sonos_api_call("[living room] join bedroom",f"{sonos_api_url}/{sonos_livingroom}/join/{sonos_bedroom}")
    sonos_api_call("[owen's room] join bedroom",f"{sonos_api_url}/{sonos_owens_room}/join/{sonos_bedroom}")

    sonos_api_call("[bedroom/group] crossfade on", f"{sonos_api_url}/{sonos_bedroom}/crossfade/on")
    sonos_api_call("[bedroom/group] repeat one", f"{sonos_api_url}/{sonos_bedroom}/repeat/one")
    
    sonos_api_call("[bedroom/group] start Sleep playlist", f"{sonos_api_url}/{sonos_bedroom}/playlist/Sleep")
    
    return '{"status":"success"}'

@app.route("/sonos/wake/all")
def sonos_wake_all():
    sonos_api_call("[bedroom] pause", f"{sonos_api_url}/{sonos_bedroom}/pause")
    sonos_api_call("[living room] pause", f"{sonos_api_url}/{sonos_livingroom}/pause")
    sonos_api_call("[owen's room] pause", f"{sonos_api_url}/{sonos_owens_room}/pause")

    sonos_api_call("[bedroom]  ungroup", f"{sonos_api_url}/{sonos_bedroom}/leave")
    sonos_api_call("[living room] ungroup", f"{sonos_api_url}/{sonos_livingroom}/leave")
    sonos_api_call("[owen's room] ungroup", f"{sonos_api_url}/{sonos_owens_room}/leave")

    sonos_api_call("[bedroom] set volume", f"{sonos_api_url}/{sonos_bedroom}/volume/20")
    sonos_api_call("[living room] set volume", f"{sonos_api_url}/{sonos_livingroom}/volume/30")
    sonos_api_call("[owen's room] set volume", f"{sonos_api_url}/{sonos_owens_room}/volume/20")

    sonos_api_call("[bedroom] crossfade off", f"{sonos_api_url}/{sonos_bedroom}/crossfade/off")
    sonos_api_call("[bedroom] repeat off", f"{sonos_api_url}/{sonos_bedroom}/repeat/off")

    sonos_api_call("[living room] crossfade off", f"{sonos_api_url}/{sonos_livingroom}/crossfade/off")
    sonos_api_call("[living room] repeat off", f"{sonos_api_url}/{sonos_livingroom}/repeat/off")

    sonos_api_call("[owen's room] crossfade off", f"{sonos_api_url}/{sonos_owens_room}/crossfade/off")
    sonos_api_call("[owen's room] repeat off", f"{sonos_api_url}/{sonos_owens_room}/repeat/off")

    return '{"status":"success"}'

@app.route("/sonos/sleep/owen")
def sonos_sleep_owen():
    sonos_api_call("[owen's room] pause", f"{sonos_api_url}/{sonos_owens_room}/pause")
    
    sonos_api_call("[owen's room] ungroup", f"{sonos_api_url}/{sonos_owens_room}/leave")
    
    sonos_api_call("[owen's room] set volume", f"{sonos_api_url}/{sonos_owens_room}/volume/60")

    sonos_api_call("[owen's room] turn off shuffle", f"{sonos_api_url}/{sonos_owens_room}/shuffle/off")
    sonos_api_call("[owen's room] turn on crossfade", f"{sonos_api_url}/{sonos_owens_room}/crossfade/on")
    sonos_api_call("[owen's room] turn on repeat:one", f"{sonos_api_url}/{sonos_owens_room}/repeat/one")
    
    sonos_api_call("[owen's room] start Sleep playlist", f"{sonos_api_url}/{sonos_owens_room}/playlist/Sleep")
    return '{"status":"success"}'

@app.route("/sonos/wake/owen")
def sonos_wake_owen():
    sonos_api_call("[owen's room] pause", f"{sonos_api_url}/{sonos_owens_room}/pause")
    sonos_api_call("[owen's room] ungroup", f"{sonos_api_url}/{sonos_owens_room}/leave")

    sonos_api_call("[owen's room] set volume", f"{sonos_api_url}/{sonos_owens_room}/volume/20")

    sonos_api_call("[owen's room] crossfade off", f"{sonos_api_url}/{sonos_owens_room}/crossfade/off")
    sonos_api_call("[owen's room] repeat off", f"{sonos_api_url}/{sonos_owens_room}/repeat/off")

    return '{"status":"success"}'