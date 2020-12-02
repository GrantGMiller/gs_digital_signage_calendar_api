import time
from persistent_variables import PersistentVariables
import gs_tools
from extronlib_pro import event, Label, Button, Wait
from gs_oauth_tools import AuthManager
import ui_menu_settings

SERVICE_ACCOUNT = 'Service Accounts'
NEW_SERVICE_ACCOUNT = '< New Service Account >'

pv = PersistentVariables('service_accounts.json')


# store data like this:
# pv.Set('serviceAccounts', {
#   str(oauthToolsID): str(user.EmailAddress)
# }


def Setup(tlp_, menuTable, input_, table_, showMessageCallback_, changeCallback_):
    global tlp, showMessageCallback, changeCallback, input, table
    table = table_
    tlp = tlp_
    input = input_
    showMessageCallback = showMessageCallback_
    changeCallback = changeCallback_

    menuTable.AddNewRowData({'Option': SERVICE_ACCOUNT})
    menuTable.SortByColumnName('Option')

    oldCallback = menuTable.CellTapped

    @event(menuTable, 'CellTapped')
    def MenuTableEvent(t, cell):
        print('ui_menu_serviceaccount MenuTableEvent(', t, cell)
        if oldCallback:
            oldCallback(t, cell)

        if cell.GetValue() == SERVICE_ACCOUNT:
            tlp.SetText(19900, 'Service Accounts')
            tlp.SetVisible(19800, True)
            tlp.SetText(19800, 'Add Serv Account')

            for ID in range(19801, 19805 + 1):
                tlp.SetVisible(ID, False)

            table.SetTableHeaderOrder(['Email', 'Status'])

            table.ClearAllData(forceRefresh=True)
            for ID, email in GetServiceAccounts().items():
                table.AddNewRowData(
                    {'Email': email, 'ID': ID}
                )

            def UpdateTable():
                for ID, email in GetServiceAccounts().items():
                    status = GetStatus(email)
                    table.UpdateRowData(
                        {'ID': ID},
                        {'Status': status},
                    )

            Wait(0, UpdateTable)

            @event(table, 'CellHeld')
            def TableCellHeldEvent(t, cell):

                def DeleteSA(i, v, p=None):
                    if v:
                        pv.PopItem('serviceAccounts', p['ID'])
                        table.DeleteRow({'ID': p['ID']})

                input.GetBoolean(
                    callback=DeleteSA,
                    # function - should take 2 params, the UserInput instance and the value the user submitted
                    feedback_btn=None,
                    passthru=cell.GetRowData(),  # any object that you want to also come thru the callback
                    message='Do you want to delete this Service Account?',
                    long_message='Do you want to delete the Service Account "{}"?'.format(cell.GetRowData()['Email']),
                    true_message=None,
                    false_message=None,
                    true_text='Yes\nDelete',
                    false_text='Cancel',
                )

            @event(Button(tlp, 19800, PressFeedback='State'), 'Released')
            def BtnAddSrvAccountEvent(button, state):
                AddServiceAccount()

            tlp.ShowPopup('Table')
            tlp.HidePopup('Menu')

    print('ui_menu_serviceaccount', oldCallback.__module__ if oldCallback else 'None', 'oldCallback=', oldCallback)
    time.sleep(1)


def AddServiceAccount():
    if not (ui_menu_settings.Get(ui_menu_settings.TENANT_ID, None) and ui_menu_settings.Get(
            ui_menu_settings.CLIENT_ID)):
        showMessageCallback('Error', 'You must first setup the "Client ID" and "Tenant ID" in the Settings menu.')
        return

    lblAddRoom = Label(tlp, 12002)
    btnQR = Button(tlp, 12001)

    tlp.HideAllPopups()
    btnQR.SetVisible(True)
    lblAddRoom.SetText('')
    tlp.ShowPopup('Add Service Account')

    ID = gs_tools.GetRandomPassword(16)

    try:
        authManager = AuthManager(
            microsoftClientID=ui_menu_settings.Get('Client ID'),
            microsoftTenantID=ui_menu_settings.Get('Tenant ID'),
            googleJSONpath='google.json',
            debug=False,
        )
    except Exception as e:
        showMessageCallback('Error 58', str(e))
        raise e

    d = authManager.CreateNewUser(ID, 'Microsoft')

    lblAddRoom.SetText('Scan the QR or go to {}\nthen enter this code:\n\n\n{}'.format(
        d['verification_uri'],
        d['user_code']
    ))

    @Wait(0)
    def Loop():
        i = 0
        while i < 5 * 60:
            i += 1
            user = authManager.GetUserByID(ID)
            if user is None:
                time.sleep(1)
            else:
                tlp.HideAllPopups()
                showMessageCallback('Connected', 'Loading User Info')
                pv.SetItem('serviceAccounts', ID, user.EmailAddress)
                showMessageCallback(
                    'Service Account Added',
                    'The service account\n"{}"\nhas been added.'.format(user.EmailAddress),
                    timeout=5
                )
                changeCallback(pv.Get('serviceAccounts', {}))
                table.AddNewRowData({'Email': user.EmailAddress})
                break


def GetServiceAccounts():
    return pv.Get('serviceAccounts', {})


def GetServiceAccount(email=None, ID=None):
    print('GetServiceAccount(', email, ID)
    # get the ID from the email or vice versa
    if email:
        for theID, theEmail in pv.Get('serviceAccounts', {}).items():
            if theEmail == email:
                return theID
    elif ID:
        return pv.Get('serviceAccounts', {}).get(ID, None)

    else:
        return None


def GetStatus(email):
    user = GetUser(email)
    token = user.GetAcessToken()
    if token:
        return 'Authorized'
    else:
        return 'Error 156: Not Authorized'


def GetUser(email):
    try:
        authManager = AuthManager(
            microsoftClientID=ui_menu_settings.Get('Client ID'),
            microsoftTenantID=ui_menu_settings.Get('Tenant ID'),
            debug=False,
        )
    except Exception as e:
        showMessageCallback('Error 58', str(e))
        raise e
    return authManager.GetUserByID(GetServiceAccount(email=email))


def Get(*a, **k):
    return pv.Get(*a, **k)
