import extronlib

try:
    extronlib.ExportForGS(
        r'C:\Users\gmiller\Desktop\Grants GUIs\GS Modules\Digital Signage Calendar API\Pycharm Export')
    raise Exception('Fake')

except Exception as e:
    if 'Fake' in e.args:
        # raise e
        pass

import devices
import ui

for tlp in devices.tlps:
    ui.Setup(tlp)

print('end main.py')