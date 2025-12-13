from . import SpeakEditor
window = None


def show():
    global window
    if window is None:
        window = SpeakEditor.Dialog()
    window.show()
