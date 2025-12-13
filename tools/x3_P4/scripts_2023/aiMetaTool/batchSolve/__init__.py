try:
    from importlib import reload
except ImportError:
    pass

from . import solve_anim_all
from . import play_anim_all
from . import solve_ai_speak
reload(solve_anim_all)
reload(play_anim_all)
reload(solve_ai_speak)