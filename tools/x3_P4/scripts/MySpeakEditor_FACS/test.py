import wuwu.MySpeakEditor_FACS
reload(wuwu.MySpeakEditor_FACS)
from wuwu.MySpeakEditor_FACS import SpeakEditor
reload(SpeakEditor)
window = SpeakEditor.Dialog()
window.show()