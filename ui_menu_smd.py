import time

from extronlib_pro import Wait, event, Button
from persistent_variables import PersistentVariables
import aes_tools
import devices
from helpers import FindAllSMDs
import player_helpers

PLAYERS = 'Players'

pv = PersistentVariables('smds.json')  # , fileClass=aes_tools.File, fileMode='b')


# 'found_smds': [],

def Setup(tlp, menuTable, userInput, generalTable, showMessageCallback, smdChangeCallback):
    menuTable.AddNewRowData({'Option': PLAYERS})
    menuTable.SortByColumnName('Option')

    oldCallback = menuTable.CellTapped

    @event(menuTable, 'CellTapped')
    def MenuTableEvent(t, cell):
        print('ui_menu_smd', t, cell)
        if oldCallback:
            oldCallback(t, cell)

        if cell.GetValue() == PLAYERS:
            print('27')
            tlp.SetText(19900, 'Players')
            tlp.SetVisible(19900, True)

            tlp.SetText(19800, 'Add Player')
            tlp.SetVisible(19800, True)

            for ID in range(19801, 19805 + 1):
                tlp.SetVisible(ID, False)

            @event(Button(tlp, 19800, PressFeedback='State'), 'Released')
            def BtnAddPlayerEvent(button, state):

                def PasswordEntered(input, value, passthru=None):
                    player = player_helpers.SMD202_Player(
                        connectionParameters={
                            'IPAddress': passthru['ip'],
                            'IPPort': 23,
                            'PlainPassword': value,
                        }
                    )
                    devices.manager.RegisterPlayer(player)
                    showMessageCallback('Player Added', 'The player "{}" has been added'.format(passthru['ip']))
                    smdChangeCallback()
                    generalTable.AddNewRowData({
                        'IP Address': player.IPAddress,
                        'Status': player.GetConnectionStatus(),
                    })

                def IPEntered(input, value, passthru=None):
                    userInput.GetKeyboard(
                        kb_popup_name='Keyboard',
                        kb_popup_timeout=0,
                        callback=PasswordEntered,
                        # function - should take 2 params, the UserInput instance and the value the user submitted
                        feedback_btn=None,  # button to assign submitted value
                        password_mode=False,  # mask your typing with '****'
                        text_feedback=None,  # button() to show text as its typed
                        passthru={'ip': value},  # any object that you want to also come thru the callback
                        message='Enter the Password of the player',
                        allowCancel=True,  # set to False to force the user to enter input
                        disableKeyCallback=False,  # temporarily disable the keyCallback
                    )

                userInput.GetKeyboard(
                    kb_popup_name='User Input - IP Address',
                    kb_popup_timeout=0,
                    callback=IPEntered,
                    # function - should take 2 params, the UserInput instance and the value the user submitted
                    feedback_btn=None,  # button to assign submitted value
                    password_mode=False,  # mask your typing with '****'
                    text_feedback=None,  # button() to show text as its typed
                    passthru=None,  # any object that you want to also come thru the callback
                    message='Enter the IP Address of the player',
                    allowCancel=True,  # set to False to force the user to enter input
                    disableKeyCallback=False,  # temporarily disable the keyCallback
                )

            generalTable.ClearAllData(forceRefresh=True)
            generalTable.SetTableHeaderOrder(['IP Address', 'Status'])
            for player in devices.manager.Players:
                generalTable.AddNewRowData({
                    'IP Address': player.IPAddress,
                    'Status': player.GetConnectionStatus(),
                })

            tlp.ShowPopup('Table')
            tlp.HidePopup('Menu')

    print('ui_menu_smd', oldCallback.__module__ if oldCallback else 'None', 'oldCallback=', oldCallback)
    time.sleep(1)


def AutoDiscoverSMDs():
    procIP = devices.proc.IPAddress
    prefix = '.'.join(procIP.split('.')[:3])
    startIP = prefix + '.0'
    endIP = prefix + '.255'
    print('FindAllSMDs(', startIP, endIP)

    def FoundSMDCallack(ip):
        print('FoundSMDCallback(', ip)
        pv.Append('found_smds', ip, allowDuplicates=False)

    FindAllSMDs(startIP, endIP, FoundSMDCallack)

# Wait(0, AutoDiscoverSMDs)
