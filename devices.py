from extronlib_pro import (
    ProcessorDevice, UIDevice,
)
from helpers import PlayerManager

proc = ProcessorDevice('ProcessorAlias')
manager = PlayerManager(proc)
tlps = [
    UIDevice('PanelAlias')
]
