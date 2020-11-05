from extronlib_pro import event
import ui_menu_serviceaccount
from persistent_variables import PersistentVariables

ADD_CALENDAR = 'Add Calendar'
NEW_SERVICE_ACCOUNT = '< New Service Account >'

pv = PersistentVariables('calendars.json')


# store data like:
# { str(impersonationEmail):str(oauthID):, ...}

def Setup(tlp, menuTable, input, showMessageCallback, changeCallback):
    menuTable.AddNewRowData({'Option': ADD_CALENDAR})
    menuTable.SortByColumnName('Option')

    oldCallback = menuTable.CellReleased

    @event(menuTable, 'CellReleased')
    def MenuTableEvent(table, cell):
        if oldCallback:
            oldCallback(table, cell)

        if cell.GetValue() == ADD_CALENDAR:
            AddRoom()
            tlp.HidePopup('Menu')

    def AddRoom():
        options = list(ui_menu_serviceaccount.GetServiceAccounts().values())
        options.append(NEW_SERVICE_ACCOUNT)
        input.GetList(
            options=options,  # list()
            callback=SelectedServiceAccount,
            # function - should take 2 params, the UserInput instance and the value the user submitted
            feedback_btn=None,  # the button that the user's selection will be .SetText() to
            passthru=None,  # any object that you want to pass thru to the callback
            message='Select a Service Account',  # prompt to display to user
            sort=False,  # bool
            sortFunc=None,  # a function that acts like sorted()
            highlight=None,  # list of str, if str is matched in the list, it will be highlighted
            multiselect=False
        )

    def SelectedServiceAccount(input, value, passthru=None):

        if value == NEW_SERVICE_ACCOUNT:
            ui_menu_serviceaccount.AddServiceAccount()
        else:
            showMessageCallback('Loading...', 'Please Wait...')
            user = ui_menu_serviceaccount.GetUser(email=value)

            def SaveRoom(ui, value, passthru=None):
                impersonation = value
                showMessageCallback('Loading', 'Please Wait...')

                changeCallback(impersonation)
                showMessageCallback(
                    'Room Added',
                    'Room\n"{}"\nhas been added.'.format(value),
                    timeout=5,
                )
                pv.Set(impersonation, user.ID)

            tlp.HideAllPopups()
            input.GetKeyboard(
                kb_popup_name='Keyboard',
                message='Enter the Room Account Email Address',
                callback=SaveRoom,
            )
            input.SetKeyboardText(value)


def Get(*a, **k):
    return pv.Get(*a, **k)
