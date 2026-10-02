import sys
from fltk import*
import socket

class Mytile(Fl_Button): #creates buttons with other atrributes
    def __init__(self, x,y,w,h,r,c):
        super().__init__(x,y,w,h)
        self.loc = (r,c)
        self.Blank = True #booleans used to descibe properties of tiles
        self.Miss = False
        self.Ship = False
        self.Hit = False
        self.mine = False #keeps track of which grids are server's and client's
        
    def print(self):
        print(self.loc, self.Blank,self.Ship,self.Miss,self.Hit, self.mine)
        
class Ships(Fl_Window):
    def __init__(self,x,y,w,h):
        Fl_Window.__init__(self,x,y,w,h,'Battle Ship '+sys.argv[1])
        self.callback(self.close) #close window callback
        
        self.begin()
        tip = 'Starting Game'
        self.bx = Fl_Box(500,560,150,30)
        self.bx.box(FL_SHADOW_BOX)
        self.bx.redraw()
        self.bx.label(tip)
        self.end()
        
        self.Ltheirs = []
        self.Lmine = []
        self.indexL = []
        self.init = True #used to set up board
        self.counterser = 0 #counts ships placed
        self.countercli = 0 #counts ships placed by opponent
        self.turn = 0 #counterser for turns taken
        
        self.sunk = 0
        self.conn=0
        self.host = sys.argv[2]
        self.port=int(sys.argv[3])
        self.s=socket.socket(socket.AF_INET,socket.SOCK_STREAM) #creates socket s
        
        self.blank = Fl_PNG_Image("blank.png").copy(100,100)
        self.ship = Fl_PNG_Image("ship.png").copy(100,100)
        self.hit = Fl_PNG_Image("hit.png").copy(100,100)
        self.miss = Fl_PNG_Image("miss.png").copy(100,100)
        
        if sys.argv[1] == "server":
            self.myturn = True
            self.s.bind((self.host, self.port)) # server must bind and listen
            self.s.listen()
            Fl.add_fd(self.s.fileno(), self.acceptconn)
            self.grid(self.Lmine,50,True)
            self.grid(self.Ltheirs,600,False)

        elif sys.argv[1]=='client':
            self.myturn = False
            try:
                self.s.connect( (self.host,self.port) ) #client connects to server
                Fl.add_fd(self.s.fileno(), self.recvdata)
                self.grid(self.Ltheirs,50,False)
                self.grid(self.Lmine,600,True)
                
            except:
                print("Server needs to start first")
                self.s.close()
                sys.exit(1)
                
        
    def grid(self,L,offset,whose):
        for r in range(5):
            L.append([])
            for c in range(5):
                self.begin()
                but = Mytile(c*100+offset,r*100+50,100,100,r,c) #buttons are created in another class "Mytile"
                but.image(self.blank)
                but.mine = whose
                but.callback(self.but_cb)
                self.indexL.append((r,c))
                L[-1].append(but)
                
        self.resizable(self) #cannot resize images, only window and widgets
        self.end()
        
    def but_cb(self,wid):
        if self.init and wid.mine:
            if self.counterser < 5 and sys.argv[1] == 'server':
                if wid.Blank:
                    wid.image(self.ship)
                    wid.Blank = False
                    wid.Ship = True
                    self.counterser += 1
                    try:
                        self.conn.sendall(str(self.counterser).encode())
                    except:
                        print("Client has not yet connected, or has disconnected")
                    print(self.counterser, self.countercli)
            elif self.countercli < 5 and sys.argv[1] == 'client':
                if wid.Blank:
                    wid.image(self.ship)
                    wid.Blank = False
                    wid.Ship = True
                    self.countercli += 1
                    try:
                        self.s.sendall(str(self.countercli).encode())
                    except:
                        print('Server may have disconnected')
                    print(self.countercli, self.counterser)
                    
            if self.counterser == 5 and self.countercli == 5:
                self.init = False
                # Initial setup of Green/Red button
                if sys.argv[1] == 'server':
                    self.bx.label('My Turn')
                    self.bx.color(FL_GREEN)
                    self.bx.redraw()
                else:
                    self.bx.label('Opponents Turn')
                    self.bx.color(FL_RED)
                    self.bx.redraw()

            else:
                self.init = True

        if self.init == False and self.myturn:
            if wid.mine == False:
                L = ['q',str(self.turn),str(wid.loc[0]),str(wid.loc[1])]
                dat = ' '.join(L)
                self.myturn = False
                self.bx.label('Opponents Turn')
                self.bx.color(FL_RED)
                self.bx.redraw()
                if sys.argv[1] == "server":
                    try:
                        self.conn.sendall(dat.encode())
                    except:
                        print("Client has not yet connected, or has disconnected")
                elif sys.argv[1]=="client":
                    try:
                        self.s.sendall(dat.encode())
                    except:
                        print('Server may have disconnected')
                        self.s.close()
                        self.hide()

    def acceptconn(self, fd):
        if self.conn == 0: #only allow one client to connect
            self.conn, addr = self.s.accept()
            Fl.add_fd(self.conn.fileno(), self.recvdata)

    def recvdata(self, fd):
        action = ''
        
        if sys.argv[1] == "server":
            data=self.conn.recv(1024) #server communicates through socket conn
            #data is null byte b'' when socket is closed
            if data == b'':
                Fl.remove_fd(self.conn.fileno())
                print('stopped watching socket conn')
                return
                
        elif sys.argv[1]== "client":
            data=self.s.recv(1024) #client communicates through socket s
            if not data: #same as if data == b''
                Fl.remove_fd(self.s.fileno())
                print('stopped watching socket s')
                return
                
        newdat = data.decode()
        
        if len(newdat) > 2:
            dat = newdat.split()
            coord = (int(dat[2]),int(dat[3]))
            
            if dat[0] == 'q':  #recieved question and responding
                self.myturn = True
                self.bx.label('My Turn')
                self.bx.color(FL_GREEN)
                self.bx.redraw()
                b = self.Lmine[coord[0]][coord[1]]
            
                if b.Ship == True:
                    b.image(self.hit)
                    b.redraw()
                    b.Hit = True
                    b.Ship = False
                    b.Blank = False
                    b.Miss = False
                    self.sunk +=1
                    if self.sunk == 5:
                        action = 'over'
                    else:
                        action = 'hit'
                    L = ['r',str(self.turn),str(coord[0]),str(coord[1]),action]
                    sent = ' '.join(L)
                    
                elif b.Hit:
                    L = ['r',str(self.turn),str(coord[0]),str(coord[1]),'miss']
                    sent = ' '.join(L)
                elif b.Miss:
                    L = ['r',str(self.turn),str(coord[0]),str(coord[1]),'miss']
                    sent = ' '.join(L)
                elif b.Blank:
                    L = ['r',str(self.turn),str(coord[0]),str(coord[1]),'miss']
                    sent = ' '.join(L)
                    b.image(self.miss)
                    b.redraw()
                    
                self.turn+=1
                
                if sys.argv[1] == "server":
                    self.conn.sendall(sent.encode())
                else:
                    self.s.sendall(sent.encode())
                if self.sunk == 5:
                    self.gameover("You Lost!")
            elif dat[0] == 'r':
                b = self.Ltheirs[coord[0]][coord[1]]
                self.turn+=1
                self.myturn = False
                self.bx.label('Opponents Turn')
                self.bx.color(FL_RED)
                self.bx.redraw()

                if dat[4] == 'hit':
                    b.image(self.hit)
                    b.redraw()
                    b.Hit = True
                    b.Blank = False
                if dat[4] == 'miss':
                    b.image(self.miss)
                    b.redraw()
                    b.Miss = True
                    b.Blank = False
                if dat[4] == 'over':
                    text = 'You won!'
                    self.gameover(text)
                    
        else:
            dat = int(newdat)
            
            if sys.argv[1] == 'server':
                self.countercli = dat
            else:
                self.counterser = dat
                
            if self.counterser == 5 and self.countercli == 5:
                self.init = False
                #Initial setup of Green/Red light button upon recieve
                if sys.argv[1] == 'server':
                    self.bx.label('My Turn')
                    self.bx.color(FL_GREEN)
                    self.bx.redraw()
                else:
                    self.bx.label('Opponents Turn')
                    self.bx.color(FL_RED)
                    self.bx.redraw()
            
    def close(self, wid):
        if self.conn != 0:
            if sys.argv[1]== "server":
                self.conn.close()
            self.s.close() #close socket s for both client and server
        self.hide()
    
    def gameover(self,text):
        fl_message(sys.argv[1]+', '+text)
        if text == 'You won!':
            self.bx.color(FL_GREEN)
        else:
            self.bx.color(FL_GREEN)
        self.bx.label('Game over!')
        self.bx.redraw()
        self.myturn = False
        
app = Ships(55,55,1150,600)
app.show()
Fl.run()
