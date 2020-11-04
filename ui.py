import devices
from extronlib_pro import Button, Level, Label, event, Timer
from scrolling_table import ScrollingTable
import ui_menu_serviceaccount
import ui_menu_calendar
import ui_menu_smd
from sync import SyncCalendarsAndPlayers
from user_input_tools import UserInputClass
from version import VERSION
from persistent_variables import PersistentVariables

pv = PersistentVariables('ui.json')


def Setup(tlp):
    tlp.SetText(11001, 'Version: {}'.format(VERSION))

    Button(tlp, 13002, PressFeedback='State').HidePopup('Message')

    def ShowMessage(title, body, timeout=60):
        tlp.SetText(13000, title)
        tlp.SetText(13001, body)
        tlp.ShowPopup('Message', timeout)

    userInput = UserInputClass(tlp)  # a helper to get various inputs from the user like strings, numbers, ip addresses
    userInput.SetupKeyboard(
        kb_popup_name='Keyboard',  # str() #default popup name
        kb_btn_submit=Button(tlp, 9202, PressFeedback='State'),  # Button()
        kb_btn_cancel=Button(tlp, 9207, PressFeedback='State'),  # Button()
        kb_other_popups={},
        # {'Integer': 'User Input - Integer', 'Float': 'User Input - Float', 'AlphaNumeric': 'User Input - AlphaNumeric'}

        KeyIDs=[ID for ID in range(9000, 9043 + 1)],  # list()
        BackspaceID=9200,  # int()
        ClearID=9209,  # int()
        SpaceBarID=9106,  # int()
        ShiftID=9206,  # int()
        SymbolID=9203,
        FeedbackObject=Button(tlp, 9208),  # object with .SetText() method
        kb_btn_message=Button(tlp, 9201),
        kb_class=None,
        kb_class_kwargs=None,
    )
    btnListScrollUp = Button(tlp, 15011, PressFeedback='State')
    btnListScrollDown = Button(tlp, 15009, PressFeedback='State')

    userInput.SetupList(
        list_popup_name='User Input - List',  # str()
        list_btn_hide=Button(tlp, 15001, PressFeedback='State'),  # Button object
        list_btn_table=[
            Button(tlp, ID, PressFeedback='State') for ID in range(15002, 15007 + 1)
        ],  # list() of Button objects
        list_btn_scroll_up=btnListScrollUp,  # Button object
        list_btn_scroll_down=btnListScrollDown,  # Button object
        list_label_message=Label(tlp, 15000),  # Button/Label object
        list_label_scroll=None,  # Button/Label object
        list_level_scroll=Level(tlp, 15010),
        list_btn_ok=Button(tlp, 15008, PressFeedback='State'),  # used for multiselect
        list_popup_name_multiselect='User Input - List',
    )
    userInput.SetupBoolean(
        bool_popup_name='User Input - Confirm',  # str()

        bool_btn_true=Button(tlp, 16003, PressFeedback='State'),  # Button()
        bool_btn_false=Button(tlp, 16004, PressFeedback='State'),  # Button()
        bool_btn_cancel=Button(tlp, 16001, PressFeedback='State'),  # Button()

        bool_btn_message=Label(tlp, 16000, ),
        bool_btn_long_message=Label(tlp, 16002, ),
        bool_btn_true_explaination=Label(tlp, 16005, ),
        bool_btn_false_explanation=Label(tlp, 16006, ),
    )

    # Page: Main ######################################################
    btnMenu = Button(tlp, 11000, holdTime=1, PressFeedback='State')

    @event(btnMenu, ['Tapped', 'Held'])
    def BtnMenuEvent(button, state):
        if state == 'Tapped':
            btnMenu.ShowPopup('Menu')
        elif state == 'Held':
            UpdateMainPage()

    Button(tlp, 17103).HidePopup('Menu')

    mainTable = ScrollingTable()

    btnMainTableScrollUp = Button(tlp, 10010, PressFeedback='State', holdTime=0.2, repeatTime=0.1)
    btnMainTableScrollDown = Button(tlp, 10011, PressFeedback='State', holdTime=0.2, repeatTime=0.1)

    mainTable.RegisterScrollUpButton(btnMainTableScrollUp)
    mainTable.RegisterScrollDownButton(btnMainTableScrollDown)

    @event([btnMainTableScrollUp, btnMainTableScrollDown], ['Pressed', 'Repeated'])
    def MainTableScrollEvent(button, state):
        if button == btnMainTableScrollUp:
            mainTable.ScrollUp()
        elif button == btnMainTableScrollDown:
            mainTable.ScrollDown()

    mainTable.RegisterScrollUpDownLevel(Level(tlp, 10009))

    mainTable.RegisterHeaderButtons(
        *[Button(tlp, ID) for ID in range(10300, 10303 + 1)],
    )
    mainTable.SetTableHeaderOrder([
        'Status',
        'Calendar',
        'Player IP',
        'File',
    ])

    for row in range(0, 8 + 1):
        tlp.SetVisible(10000 + row, False)
        tlp.SetVisible(10100 + row, False)
        tlp.SetVisible(10200 + row, False)
        tlp.SetVisible(10400 + row, False)

        mainTable.RegisterRowButtons(
            row,
            Button(tlp, 10000 + row, PressFeedback='State'),
            Button(tlp, 10100 + row, PressFeedback='State'),
            Button(tlp, 10200 + row, PressFeedback='State'),
            Button(tlp, 10400 + row, PressFeedback='State'),
        )

    mainTable.HideEmptyRows(True)

    @event(mainTable, 'CellReleased')
    def MainTableTouchEvent(table, cell):
        if cell.GetHeader() == 'Calendar':
            def CalendarSelected(input, value, passthru=None):
                impersonation = value
                pv.SetItem('link', impersonation, cell.GetRowData()['Player IP'])
                UpdateMainPage()

            userInput.GetList(
                options=[calendar for _, calendar in ui_menu_calendar.Get().items()],  # list()
                callback=CalendarSelected,
                # function - should take 2 params, the UserInput instance and the value the user submitted
                feedback_btn=None,  # the button that the user's selection will be .SetText() to
                passthru=None,  # any object that you want to pass thru to the callback
                message=None,  # prompt to display to user
                sort=True,  # bool
                sortFunc=None,  # a function that acts like sorted()
                highlight=None,  # list of str, if str is matched in the list, it will be highlighted
                multiselect=False
                # True will allow the user to select more than one item from the list, the user must then press the OK button

            )

    def SetStatusCell(cell):
        # Set the color
        if cell.button.Text == 'Connected':
            cell.button.SetState(1)  # GREEN
        elif cell.button.Text == 'Disconnected':
            cell.button.SetState(0)  # RED

        cell.button.SetText('')

    mainTable.AddCustomRule('Status', SetStatusCell)

    def UpdateMainPage(*a, **k):
        print('UpdateMainPage(', a, k)
        for player in devices.manager.Players:
            print('player=', player)
            if not mainTable.has_row({'Player IP': player.IPAddress}):
                mainTable.AddNewRowData({'Player IP': player.IPAddress})

            print(player.GetConnectionStatus(), player)

            mainTable.UpdateRowData(
                {'Player IP': player.IPAddress},
                {
                    'Status': player.GetConnectionStatus(),
                    'File': player.GetCurrentPlayingFile(),
                }
            )

        for impersonation, ip in pv.Get('link', {}).items():
            print('impersonation=', impersonation, ', ip=', ip)
            mainTable.UpdateRowData(
                {'Player IP': ip},
                {'Calendar': impersonation},
            )

        SyncCalendarsAndPlayers()

    timerMainPage = Timer(60, UpdateMainPage)

    # Popup: Table ###################################################################
    # This generalTable is for generic use by other modules
    Button(tlp, 19901, PressFeedback='State').HidePopup('Table')
    Button(tlp, 19905, PressFeedback='State').HidePopup('Table')

    generalTable = ScrollingTable()

    generalTable.RegisterHeaderButtons(
        Button(tlp, 19906, PressFeedback='State'),
        Button(tlp, 19907, PressFeedback='State'),
    )

    for i in range(0, 6 + 1):
        generalTable.RegisterRowButtons(
            i,
            Button(tlp, 19000 + i, PressFeedback='State', holdTime=1),
            Button(tlp, 19100 + i, PressFeedback='State', holdTime=1)
        )

    btnTableScrollUp = Button(tlp, 19902, PressFeedback='State', repeatTime=0.1, holdTime=0.2)
    btnTableScrollDown = Button(tlp, 19903, PressFeedback='State', repeatTime=0.1, holdTime=0.2)

    generalTable.RegisterScrollUpButton(btnTableScrollUp)
    generalTable.RegisterScrollDownButton(btnTableScrollDown)
    generalTable.RegisterScrollUpDownLevel(Level(tlp, 19904))

    @event([btnTableScrollUp, btnTableScrollDown], ['Pressed', 'Repeated'])
    def BtnTableScrollEvent(button, state):
        if button == btnTableScrollUp:
            generalTable.ScrollUp()
        elif button == btnTableScrollDown:
            generalTable.ScrollDown()

    # Popup: Menu #####################################################################

    menuTable = ScrollingTable()

    btnMenuTableScrollUp = Button(tlp, 17100, PressFeedback='State', holdTime=0.2, repeatTime=0.1)
    btnMenuTableScrollDown = Button(tlp, 17101, PressFeedback='State', holdTime=0.2, repeatTime=0.1)

    menuTable.RegisterScrollUpButton(btnMenuTableScrollUp)
    menuTable.RegisterScrollDownButton(btnMenuTableScrollDown)

    @event([btnMenuTableScrollUp, btnMenuTableScrollDown], ['Pressed', 'Repeated'])
    def MainTableScrollEvent(button, state):
        if button == btnMenuTableScrollUp:
            menuTable.ScrollUp()
        elif button == btnMenuTableScrollDown:
            menuTable.ScrollDown()

    for row in range(0, 6 + 1):
        menuTable.RegisterRowButtons(
            row,
            Button(tlp, 17000 + row, PressFeedback='State'),
        )
    menuTable.SetTableHeaderOrder(['Option'])

    menuTable.HideEmptyRows(True)

    # menu options
    def ServiceAccountChangeCallback(serviceAccountDict):
        print('ServiceAccountChangeCallback(', serviceAccountDict)

    ui_menu_serviceaccount.Setup(tlp, menuTable, userInput, generalTable, ShowMessage, ServiceAccountChangeCallback)

    def RoomChangeCallback(impersonation):
        print('RoomChangeCallback(', impersonation)

    ui_menu_calendar.Setup(tlp, menuTable, userInput, ShowMessage, RoomChangeCallback)

    def SMDChangeCallback(*a, **k):
        print('SMDChangeCallback(', a, k)
        UpdateMainPage()

    ui_menu_smd.Setup(tlp, menuTable, userInput, generalTable, ShowMessage, SMDChangeCallback)

    # Popup: Add Service Account ##############################################
    Button(tlp, 12003, PressFeedback='State').HidePopup('Add Service Account')

    # INIT ####################################################################
    tlp.HideAllPopups()
    UpdateMainPage()