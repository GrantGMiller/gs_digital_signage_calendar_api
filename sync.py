import ui
import devices
from gs_exchange_interface import EWS
import ui_menu_serviceaccount
import ui_menu_calendar
from extronlib_pro import File, ProgramLog

DIR_MEDIA = '/media/'


def SyncCalendarsAndPlayers():
    for player in devices.manager.Players:
        try:
            calendar = None
            for impersonation, ip in ui.pv.Get('link', {}).items():
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
                                print('the file name exist on IPCP, assuming its the right file.')
                                print('Dont want to download the whole file to make sure')

                                # if len(attach.Read()) != File(path).SizeOf():
                                #     print('File on IPCP is the wrong size, overwrite it now')
                                #     with File(path, 'wb') as file:
                                #         file.write(attach.Read())
                                # else:
                                #     print('The file is on the IPCP and is the right size.')
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
                                    player.LoadFileToMemory(path)
                                else:
                                    print('The file size matches on player and IPCP')

                            else:
                                print('File {} does not exists in player memory. Load it now.'.format(attach.Name))
                                player.LoadFileToMemory(path)

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
            raise e


def GetEWS(impersonation):
    ID = None
    for theID, theEmail in ui_menu_calendar.Get().items():
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
        debug=True,
    )
    return ews
