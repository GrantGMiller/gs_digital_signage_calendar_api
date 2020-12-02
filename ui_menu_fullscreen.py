import time

from extronlib_pro import event, Button

FULLSCREEN_VIDEO = 'Fullscreen Video'


def Setup(tlp, menuTable):
    menuTable.AddNewRowData({'Option': FULLSCREEN_VIDEO})
    menuTable.SortByColumnName('Option')

    oldCallback = menuTable.CellTapped

    @event(menuTable, 'CellTapped')
    def MenuTableEvent(t, cell):
        print('ui_fullscreen MenuTableEvent(', t, cell)
        if oldCallback:
            oldCallback(t, cell)

        if cell.GetValue() == FULLSCREEN_VIDEO:
            tlp.HideAllPopups()
            tlp.ShowPopup('Fullscreen Preview')
            Button(tlp, 19908).HidePopup('Fullscreen Preview')

    print('ui_menu_fullscreen', oldCallback.__module__ if oldCallback else 'None', 'oldCallback=', oldCallback)
    time.sleep(1)
