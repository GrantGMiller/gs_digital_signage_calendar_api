from extronlib_pro import event
from persistent_variables import PersistentVariables
from pin import VerifyPin

SETTINGS = 'Settings'
CLIENT_ID = 'Client ID'
TENANT_ID = 'Tenant ID'
BUFFER_EVENT_SUBJECT = 'Buffer Event Subject'
CREATE_BUFFER_EVENTS = 'Create Buffer Events'
SEND_ROOM_CONTAMINATION_EMAILS = 'Send Room Contamination Emails'

BOOLEAN_SETTINGS = [
]

STRING_SETTINGS = [
    CLIENT_ID,
    TENANT_ID,
]

defaults = {
    BUFFER_EVENT_SUBJECT: '* SCHEDULED FOR CLEANING *',
    CREATE_BUFFER_EVENTS: False,
    SEND_ROOM_CONTAMINATION_EMAILS: False,
    CLIENT_ID: '459ac21c-adde-45a5-abf3-85d757ba2fdf',  # Extron Tenant
    TENANT_ID: '30f18c78-f7ab-4851-9759-88950e65dc4b',  # Extron Tenant
}

pv = PersistentVariables('settings.json')
for key, dValue in defaults.items():
    if pv.Get(key, None) is None:
        pv.Set(key, dValue)


def Setup(tlp, menuTable, table, input, changeCallback, showMessageCallback):
    menuTable.AddNewRowData({'Option': SETTINGS})
    menuTable.SortByColumnName('Option')

    oldCallback = menuTable.CellReleased

    @event(menuTable, 'CellReleased')
    def MenuTableEvent(_, cell):
        if oldCallback:
            oldCallback(table, cell)

        if cell.GetValue() == SETTINGS:
            @VerifyPin(input)
            def DoSettings(correctPin):
                if correctPin is False:
                    showMessageCallback('Wrong PIN', "PIN is incorrect. Try Again", timeout=5)
                    return

                for ID in range(19800, 19805 + 1):
                    tlp.SetVisible(ID, False)

                tlp.SetText(19900, SETTINGS)
                tlp.ShowPopup('Table')
                table.HideEmptyRows(True)

                table.ClearAllData()
                table.SetTableHeaderOrder([
                    'Setting',
                    'Value',
                ])

                for item in BOOLEAN_SETTINGS + STRING_SETTINGS:
                    value = pv.Get(item, None)
                    table.AddNewRowData({
                        'Setting': item,
                        'Value': value,
                    })
                    changeCallback(item, value)

                @event(table, 'CellTapped')
                def TableCellEvent(table, cell):
                    for key in STRING_SETTINGS:
                        if cell.GetRowData().get('Setting') == key:
                            def UpdateKey(i, v, p=None):
                                key = p
                                pv.Set(key, v)
                                table.UpdateRowData(
                                    {'Setting': key},
                                    {'Value': v}
                                )

                            input.GetKeyboard(
                                kb_popup_name='Keyboard',
                                callback=UpdateKey,
                                passthru=key
                            )

                    for key in BOOLEAN_SETTINGS:
                        if cell.GetRowData().get('Setting') == key:
                            currentValue = cell.GetRowData()['Value']
                            newValue = not currentValue
                            pv.Set(key, newValue)
                            table.UpdateRowData(
                                {'Setting': key},
                                {'Value': newValue}
                            )

            tlp.HidePopup('Menu')


def Get(*a, **k):
    return pv.Get(*a, **k)
