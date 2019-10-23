import VideoIdExtraction as vie
import sys
import pafy
import vlc

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Youtube Radio'
        self.left = 300
        self.top = 300
        self.width = 320
        self.height = 75
        self.index = -1
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        button1 = QPushButton('Pause', self)#initializing button, with string of the button
        button1.setToolTip('Pause')#Optional, tells what message to be displayed when mouse hovering over it
        button1.move(5, 20)#Position if the button
        button1.clicked.connect(self.pause)#action performed when button is clicked
        
        button2 = QPushButton('Play', self)
        button2.setToolTip('Resume')
        button2.move(105, 20)
        button2.clicked.connect(self.resume)

        button3 = QPushButton('Next', self)
        button3.setToolTip('Next Song')
        button3.move(205, 20)
        button3.clicked.connect(self.next)

        self.show()

    def pause(self):
        playerInst.pause()
        print('Song paused')

    def resume(self):
        playerInst.play()
        print("Resuming song")

    def end(self):
        playerInst.stop()
        print("Song ending")
    

    def loadSong(self, videoIds):

        videoId = videoIds[self.index]
        baseurl = "https://www.youtube.com/watch?v="
        url = baseurl + videoId
        video = pafy.new(url)
        best = video.getbestaudio()#get the best quality audio of the video specified
        playurl = best.url
        print('Song loaded')
        return playurl

    def vlcPlayer(self, videoIds):

        global playerInst
        playurl = self.loadSong(videoIds)
        Instance = vlc.Instance()
        playerInst = Instance.media_player_new()
        Media = Instance.media_new(playurl)
        Media.get_mrl()
        playerInst.set_media(Media)

    def next(self):
        
        try:

            if playerInst:

                playerInst.stop()

            self.index = self.index + 1
            self.vlcPlayer(data)

        except:

            self.index = self.index + 1
            self.vlcPlayer(data)

if __name__ == '__main__':
    
    global data
    completeData = vie.main()
    data = completeData['VID']#get video ids from the data passed
    #data = ['ARnf4ilr9Hc', '7btNir5L8Jc', 'vEetoBuHj8g', 'DbcLg8nRWEg', 'hPbDyqzxQfU', 'tc8DU14qX6I']#completeData['VID']
    print(data)
    app = QApplication(sys.argv)#initializing QApplication
    ex = App()#initializing  our created application
    ex.next()
    sys.exit(app.exec_())#Will keep the app open or else will close after initializing
    