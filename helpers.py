from extronlib_pro import (
    EthernetClientInterface,
    File,
)
from urllib.request import urlopen
from gs_tools import IncrementIP
import json
from player_helpers import SMD202_Player
from persistent_variables import PersistentVariables

DEBUG = True
if DEBUG is False:
    print = lambda *a, **k: None

SMD_202_PART_NUMBER = '60-1306-01'
MEDIA_PATH = '/media'


def FindAllSMDs(startIP, endIP, callback):
    ip = startIP
    while ip != endIP:
        client = EthernetClientInterface(ip, 23)
        if client.Connect(1) == 'Connected':
            print(ip, 'Connected')
            res = client.SendAndWait('n', 1)
            if res:
                res = res.decode()
                if SMD_202_PART_NUMBER in res:
                    callback(ip)
            client.Disconnect()

        ip = IncrementIP(ip)


class PlayerManager:
    def __init__(self, proc):
        self._proc = proc

        self._players = list()
        self._pv = PersistentVariables('PlayerManager_{}.json'.format(self._proc.SerialNumber))

        for playerIP, playerPassword in self._pv.Get('players', {}).items():
            player = SMD202_Player(connectionParameters={
                'IPAddress': playerIP,
                'IPPort': 23,
                'PlainPassword': playerPassword
            })
            self.RegisterPlayer(player)

        if not File.Exists(MEDIA_PATH):
            File.MakeDir(MEDIA_PATH)

    @property
    def Players(self):
        return self._players.copy()

    @staticmethod
    def FileExistsInMemory(filename):
        for path in File.ListDirWithSub():
            if filename == path.split('/')[-1]:
                return path

        return False

    def ClearProcMediaFiles(self):
        used, total = self._proc.UserUsage()
        print('ClearProcMediaFiles used=', used, ', total=', total, ', percent=', (used / total) * 100)
        if used / total > 0.8:
            # There is less than 20% of the file space clear all the media files
            File.DeleteDirRecursive(MEDIA_PATH)

    def RegisterPlayer(self, player):
        print('RegisterPlayer(', player)
        self._players.append(player)
        self._pv.SetItem(
            'players',
            player.IPAddress,
            player.GetPlainPassword(),
        )

    def DeletePlayer(self, playerMAC=None, playerIP=None, player=None):
        print('DeletePlayer(', playerMAC)

        if playerIP is None and playerMAC is None and player is None:
            raise ValueError('You must pass keyword "playerMAC" or "playerIP" or "player"')

        for thisPlayer in self._players.copy():
            if playerMAC and thisPlayer.MACAddress == playerMAC:
                self.DeletePlayer(player=thisPlayer)

            elif playerIP and playerIP == thisPlayer.IPAddress:
                self.DeletePlayer(player=thisPlayer)

            elif player and player == thisPlayer:
                self._players.remove(thisPlayer)

                self._pv.PopItem(
                    'players',
                    thisPlayer.IPAddress,
                )

    def GetPlayerFromMAC(self, playerMAC):
        for player in self._players:
            if player.MACAddress == playerMAC:
                return player
