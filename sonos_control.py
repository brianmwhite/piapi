import os
import requests
import jmespath

# jishi / node-sonos-http-api
# https://github.com/jishi/node-sonos-http-api

SONOS_API_IP = os.environ["SONOS_API_IP"]
SONOS_API_URL = f"http://{SONOS_API_IP}"

SONOS_OWENS_ROOM = "Owen%E2%80%99s%20Room"
SONOS_BEDROOM = "Bedroom"
SONOS_LIVINGROOM = "Living%20Room"
SONOS_OFFICE = "Office"
SONOS_DOWNSTAIRS = "Downstairs"

WHITE_NOISE_TRACK_TITLE = "Beach with Cross Fade"


def sonos_api_call(action, url):
    json = "{}"
    try:
        print(url)
        r = requests.get(url)
        json = r.json()
        # print(json)
    except:
        pass
    return json


def sonos_whitenoise_is_on(sonos_player):
    try:
        json = sonos_api_call(
            f"[{sonos_player}] get state", f"{SONOS_API_URL}/{sonos_player}/state")
        if json["playbackState"] == "PLAYING" and json["currentTrack"]["title"] == WHITE_NOISE_TRACK_TITLE:
            return True
        else:
            return False
    except:
        return False


def sonos_whitenoise_start(speaker, volume=40):
    sonos_api_call(f"[{speaker}] pause", f"{SONOS_API_URL}/{speaker}/pause")
    sonos_api_call(f"[{speaker}] ungroup", f"{SONOS_API_URL}/{speaker}/leave")
    sonos_api_call(f"[{speaker}] set volume",
                   f"{SONOS_API_URL}/{speaker}/volume/{volume}")
    sonos_api_call(f"[{speaker}] start Sleep playlist",
                   f"{SONOS_API_URL}/{speaker}/playlist/Sleep")


def sonos_whitenoise_stop(speaker, volume=20):
    sonos_api_call(f"[{speaker}] pause", f"{SONOS_API_URL}/{speaker}/pause")
    sonos_api_call(f"[{speaker}] set volume",
                   f"{SONOS_API_URL}/{speaker}/volume/{volume}")


def sonos_play_owen_downstairs():
    sonos_api_call("[downstairs] ungroup",
                   f"{SONOS_API_URL}/{SONOS_DOWNSTAIRS}/leave")
    sonos_api_call("[downstairs] set volume",
                   f"{SONOS_API_URL}/{SONOS_DOWNSTAIRS}/volume/35")
    sonos_api_call("[downstairs] start Owen playlist",
                   f"{SONOS_API_URL}/{SONOS_DOWNSTAIRS}/playlist/Owen")

    return '{"status":"success"}'


def sonos_play_playlist(speaker, playlist, volume=None, shuffle=None, repeat=None):
    sonos_api_call(f"[{speaker}] ungroup", f"{SONOS_API_URL}/{speaker}/leave")

    if volume != None:
        sonos_api_call("[{speaker}] set volume", f"{SONOS_API_URL}/{speaker}/volume/{volume}")
    
    if shuffle != None:
        sonos_api_call("[{speaker}] set shuffle", f"{SONOS_API_URL}/{speaker}/shuffle/{shuffle}")

    if repeat != None: 
        sonos_api_call("[{speaker}] set repeat", f"{SONOS_API_URL}/{speaker}/repeat/{repeat}")

    sonos_api_call("[{speaker}] start playlist", f"{SONOS_API_URL}/{speaker}/playlist/{playlist}")

    return '{"status":"success"}'


def sonos_office_stop():
    sonos_api_call("[office] mute", f"{SONOS_API_URL}/{SONOS_OFFICE}/mute")
    sonos_api_call("[office] ungroup", f"{SONOS_API_URL}/{SONOS_OFFICE}/leave")
    return '{"status":"success"}'


def sonos_office_unmute():
    sonos_api_call("[office] unmute", f"{SONOS_API_URL}/{SONOS_OFFICE}/unmute")
    return '{"status":"success"}'


def sonos_ungroup_all():
    zone_json_results = sonos_api_call(
        "return zones status", f"{SONOS_API_URL}/zones")
    search_expression = jmespath.compile("[].members[].roomName")
    sonos_players = search_expression.search(zone_json_results)
    for individual_player in sonos_players:
        sonos_api_call(f"ungroup {individual_player}",
                       f"{SONOS_API_URL}/{individual_player}/leave")
        pass
    return '{"status":"success"}'
