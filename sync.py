import ui
import devices
from gs_exchange_interface import EWS
import ui_menu_serviceaccount
import ui_menu_calendar
from extronlib_pro import File, ProgramLog

DIR_MEDIA = '/media/'

SYNC_IN_PROGRESS = False


def SyncCalendarsAndPlayers(progressCallback=None):
    # progressCallback should accept a dict like {str(player.IPAddress): int(percent)}
    print('SyncCalendarsAndPlayers()')
    global SYNC_IN_PROGRESS
    if SYNC_IN_PROGRESS:
        print('Cancelled because SYNC_IN_PROGRESS == True')
        return

    def ProgressCallback(percent):
        print('ProgressCallback(', percent)
        if progressCallback:
            progressCallback({player.IPAddress: percent})

    SYNC_IN_PROGRESS = True
    for player in devices.manager.Players:
        try:
            calendar = None
            for ip, impersonation in ui.pv.Get('link', {}).items():
                if ip == player.IPAddress:
                    calendar = impersonation
                    break

            ews = GetEWS(calendar)
            ews.UpdateCalendar()
            nowEvents = ews.GetNowCalItems()
            if nowEvents:
                for event in nowEvents:
                    print('23 event=', event)
                    if event.HasAttachments():
                        for attach in event.Attachments:
                            path = DIR_MEDIA + attach.Name

                            print('save the file to the IPCP')
                            if devices.manager.FileExistsInMemory(attach.Name):
                                print('the file name exist on IPCP')

                                # if len(attach.Size) != File(path).SizeOf():
                                if File(path).SizeOf() == 0:
                                    print('File size is 0, this is no good')
                                    print('File on IPCP is the wrong size, overwrite it now')
                                    with File(path, 'wb') as file:
                                        file.write(attach.Read())
                                else:
                                    print('The file is on the IPCP and is the right size.')
                            else:
                                print('The file does not exist on the IPCP, write it there now')
                                with File(path, 'wb') as file:
                                    file.write(attach.Read())

                            print('Save the file to the player')

                            if player.FileExistsInMemory(attach.Name):
                                print('The file exists on the player, check the size')
                                if not player.VerifySize(attach.Name, File(path).SizeOf()):
                                    print('The file on player is the wrong size, delete it')
                                    player.DeleteFile(attach.Name)
                                    print('file deleted, load new file to player')

                                    player.LoadFileToMemory(path, progressCallback=ProgressCallback)
                                else:
                                    print('The file size matches on player and IPCP')

                            else:
                                print('File {} does not exists in player memory. Load it now.'.format(attach.Name))
                                player.LoadFileToMemory(path, progressCallback=ProgressCallback)

                            player.PlayFile(attach.Name)
                            break
                        break
                else:
                    print('there are events, but no attachments found, STOP')
                    player.Stop()
            else:
                print('no events happening now, STOP')
                player.Stop()

        except Exception as e:
            print('Exception 26:', e)
            ProgramLog(e)
            # raise e

    SYNC_IN_PROGRESS = False


def GetEWS(impersonation):
    ID = None
    for theEmail, theID in ui_menu_calendar.Get().items():
        if impersonation == theEmail:
            ID = theID
            break

    serviceAccount = None
    for theID, theEmail in ui_menu_serviceaccount.Get('serviceAccounts', {}).items():
        if theID == ID:
            serviceAccount = theEmail
            break

    if not impersonation:
        raise ValueError('Missing impersonation account "{}"'.format(impersonation))

    if not serviceAccount:
        raise ValueError('Missing service account "{}"'.format(serviceAccount))

    user = ui_menu_serviceaccount.GetUser(serviceAccount)
    ews = EWS(
        impersonation=impersonation,
        oauthCallback=user.GetAcessToken,
        authType='Oauth',
        debug=False,
    )
    return ews
