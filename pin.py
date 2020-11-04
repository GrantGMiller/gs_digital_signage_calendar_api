from gs_tools import HashIt
from persistent_variables import PersistentVariables

pv = PersistentVariables('pin.json')


class VerifyPin:
    def __init__(self, input):
        self._input = input

    def __call__(self, func):
        def CheckPin(input, value, passthru=None):
            if pv.Get('PIN', None) == HashIt(value):
                func(True)
            else:
                func(False)

        self._input.GetKeyboard(
            kb_popup_name='User Input - Number',
            kb_popup_timeout=0,
            callback=CheckPin,
            # function - should take 2 params, the UserInput instance and the value the user submitted
            feedback_btn=None,  # button to assign submitted value
            password_mode=True,  # mask your typing with '****'
            text_feedback=None,  # button() to show text as its typed
            passthru=None,  # any object that you want to also come thru the callback
            message='Enter your PIN',
            allowCancel=True,  # set to False to force the user to enter input):
            disableKeyCallback=False,  # temporarily disable the keyCallback
        )


def ChangePIN(input, allowCancel=True, callbackSuccess=None, callbackFailed=None):
    print('ChangePIN(', input, allowCancel)

    def SaveNewPIN(input, value, passthru=None):
        print('SaveNewPIN(', input, value, passthru)
        if value == pv.Get('TempPIN', None):
            pv.Set('PIN', HashIt(value))
            pv.Set('TempPIN', None)  # erase the temp PIN
            if callbackSuccess:
                callbackSuccess(True)
        else:
            if not allowCancel:
                GetFirstPIN('PINs did not match. Enter a new PIN')
            else:
                if callbackFailed:
                    callbackFailed('The PINs did not match. Please try again')

    def GetConfirmPIN():
        print('GetConfirmPIN()')
        input.GetKeyboard(
            kb_popup_name='User Input - Number',
            kb_popup_timeout=0,
            callback=SaveNewPIN,
            # function - should take 2 params, the UserInput instance and the value the user submitted
            feedback_btn=None,  # button to assign submitted value
            password_mode=True,  # mask your typing with '****'
            text_feedback=None,  # button() to show text as its typed
            passthru=None,  # any object that you want to also come thru the callback
            message='Enter the PIN again.',
            allowCancel=allowCancel,  # set to False to force the user to enter input):
            disableKeyCallback=False,  # temporarily disable the keyCallback
        )

    def SaveTempPIN(input, value, passthru=None):
        print('SaveTempPIN(', input, value, passthru)
        pv.Set('TempPIN', value)
        GetConfirmPIN()

    def GetFirstPIN(msg=None):
        print('GetFirstPIN(msg=', msg)
        input.GetKeyboard(
            kb_popup_name='User Input - Number',
            kb_popup_timeout=0,
            callback=SaveTempPIN,
            # function - should take 2 params, the UserInput instance and the value the user submitted
            feedback_btn=None,  # button to assign submitted value
            password_mode=True,  # mask your typing with '****'
            text_feedback=None,  # button() to show text as its typed
            passthru=None,  # any object that you want to also come thru the callback
            message=msg or 'Enter a new PIN',
            allowCancel=allowCancel,  # set to False to force the user to enter input):
            disableKeyCallback=False,  # temporarily disable the keyCallback
        )

    if pv.Get('PIN', None) is None:
        # no pin has been setup yet
        GetFirstPIN()
    else:
        # a PIN already exists
        # first confirm the old PIN, then setup the new PIN
        def CheckPin(input, value, passthru=None):
            print('90 CheckPin(', input, value, passthru)
            if pv.Get('PIN', None) == HashIt(value):
                GetFirstPIN()

            elif allowCancel is False:
                input.GetKeyboard(
                    kb_popup_name='User Input - Number',
                    kb_popup_timeout=0,
                    callback=CheckPin,
                    # function - should take 2 params, the UserInput instance and the value the user submitted
                    feedback_btn=None,  # button to assign submitted value
                    password_mode=True,  # mask your typing with '****'
                    text_feedback=None,  # button() to show text as its typed
                    passthru=None,  # any object that you want to also come thru the callback
                    message='Incorrect PIN. Enter the existing PIN.',
                    allowCancel=allowCancel,  # set to False to force the user to enter input):
                    disableKeyCallback=False,  # temporarily disable the keyCallback
                )

            elif allowCancel is True:
                if callbackFailed:
                    callbackFailed('This is not the existing PIN')

        input.GetKeyboard(
            kb_popup_name='User Input - Number',
            kb_popup_timeout=0,
            callback=CheckPin,
            # function - should take 2 params, the UserInput instance and the value the user submitted
            feedback_btn=None,  # button to assign submitted value
            password_mode=True,  # mask your typing with '****'
            text_feedback=None,  # button() to show text as its typed
            passthru=None,  # any object that you want to also come thru the callback
            message='Enter the existing PIN.',
            allowCancel=allowCancel,  # set to False to force the user to enter input):
            disableKeyCallback=False,  # temporarily disable the keyCallback
        )


def GetPIN():
    # this returns the hash of the PIN, not the PIN itself
    ret = pv.Get('PIN', None)
    print('GetPIN() return', ret)
    return ret
