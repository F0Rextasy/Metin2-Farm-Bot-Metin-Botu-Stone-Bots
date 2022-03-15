from tkinter import * 
from tkinter import ttk, messagebox
from tkinter import font
import pydirectinput, pyautogui
import keyboard, threading, os, webbrowser, ctypes
import win32gui
from cv2 import cv2
from pynput import keyboard
from vision import Vision
from ekranyakala import ekranYakala
from time import time, sleep

class Window(Frame):
    def __init__(self, master=None, saniye=0):
        Frame.__init__(self, master)
        self.master = master
        self.saniye = saniye

        F1 = Frame(self.master)
        F1.place(x=235,y=110)

        self.start = Button(F1,text="Başla",command=self.thread, font="bold", cursor="hand2", fg="red", width = 10, height=1)
        self.start.grid(row=0, pady=5)
        self.start.config(state=NORMAL,cursor="hand2", bg="red", fg="white")
        self.stop = Button(F1,text="Durdur | F11", command=self.durdur, font="bold", cursor="hand2", fg="green", width = 10, height=1)
        self.stop.grid(row=1)
        self.stop.config(state=DISABLED,cursor="arrow",bg="white", disabledforeground="red")

        F2 = LabelFrame(self.master,
                            text="Durum",
                            font="bold",
                            fg="red")
        F2.place(x=225, y=25)
        F3 = LabelFrame(self.master,
                            text="Ayarlar",
                            font="bold",
                            fg="red")
        F3.place(x=20, y=25)

        # Durum
        self.metinSayisi = 0
        self.durum = Label(F2, text="Pasif", font="bold", fg="red")
        self.durum.grid()
        self.bulunanMetin = Label(F2, text="Bulunan Metin: 0", fg="blue")
        self.bulunanMetin.grid(row=1, sticky=W)
        self.zaman = Label(F2, text="Geçen Zaman: 00:00:00", fg="green")
        self.zaman.grid(row=2,sticky=W)

        # Ayarlar
        self.ara = Button(F3, text="Ara", width=5, cursor="hand2", command=self.ara)
        self.ara.grid(row=0, column=1, sticky=W, pady=10)
        v1 = StringVar()
        self.windowName = ttk.Combobox(F3, width=17,textvariable=v1, state="readonly")
        self.windowName.grid(row=0, sticky=W, padx=2)
        Label(F3,text="Metin Taşı Kesme Süresi").grid(row=2, sticky=W)
        self.kesimsuresi = Spinbox(F3, from_=3, to = 999, width=5)
        self.kesimsuresi.grid(row=2, sticky=W, column=1)

        self.var1 = IntVar(value=0)
        self.var2 = IntVar(value=0)
        self.kilitle = Checkbutton(F3, text="Kilitle",command=self.userKilit, variable=self.var1, onvalue = 1, offvalue = 0)
        self.kilitle.grid(row=3, column=1,pady=5, sticky=W)

    def ara(self):
        liste = []
        def winEnumHandler(hwnd, ctx):  #açık pencere isimlerini listeler
            if win32gui.IsWindowVisible(hwnd):
                if win32gui.GetWindowText(hwnd) == "":
                    return
                liste.append(win32gui.GetWindowText(hwnd))
                self.windowName.config(values=(liste))
        win32gui.EnumWindows(winEnumHandler, None)

    def userKilit(self):
        if self.var1.get() == 1:
            self.kesimsuresi.config(state="disabled")
            self.windowName.config(state="disabled")
            self.ara.config(state="disabled")
        else:
            self.kesimsuresi.config(state="normal")
            self.windowName.config(state="normal")
            self.windowName.config(state="readonly")
            self.ara.config(state="normal")

    def zamanlayici(self):
        if self.sureBaslat == True:
            self.saniye += 1
            seconds = self.saniye % (24 * 3600)
            hour = seconds // 3600
            seconds %= 3600
            minutes = seconds // 60
            seconds %= 60
            self.master.after(1000, self.zamanlayici)
            return self.zaman.configure(text="Geçen Zaman: %02d:%02d:%02d" % (hour, minutes, seconds))

    def thread(self):
        threading.Thread(target=self.basla).start()

    def basla(self):
        try:
            if self.windowName.get() == "":
                messagebox.showwarning("Hata","Başlamadan Önce Oyun Ekranını Seç")
                return

            wincap = ekranYakala(self.windowName.get())
            # Model dosya yolu
            self.cascade = cv2.CascadeClassifier(r"C:/Users/MadLe/OneDrive/Masaüstü/metin2bot/cascade/cascade.xml")

            self.vision = Vision(None)
            self.loop_time = time()

            self.metine_vur = False
            self.s = 1
            self.s1 = 0
            self.kontrol = 0
            self.saniye = 0
            
            self.start.config(state=DISABLED, cursor="arrow", bg="white", disabledforeground="red")
            self.kesimsuresi.config(state="disabled")
            self.windowName.config(state="disabled")
            self.ara.config(state="disabled", cursor="arrow")
            self.kilitle.config(state="disabled")

            anons = Label(self.master, fg="red", font=("Comic Sans MS", 13, "bold"))
            anons.place(x=75, y=150)
            don = 4
            for _ in range(1,4):
                don -= 1
                sleep(1)
                print("Başlıyor:", don)
                anons["text"] = ("Başlıyor",don)
            anons.after(1000, anons.destroy)

            self.sureBaslat = True
            self.zamanlayici()
            self.durum["text"] = "Aktif"
            self.bulunanMetin["text"] = "Bulunan Metin: 0"
            threading.Thread(target=self.saldir(self.kesimsuresi.get(), wincap)).start()
        except Exception as e:
            print("wincap hatası", e)
            messagebox.showerror("Hata: Ekran Bulunamadı", f"Seçilen isimde ekran bulunamadı.\n{e}")
    def durdur(self):
        self.sureBaslat = False
        self.durum["text"] = "Pasif"
        self.start.config(state=NORMAL,cursor="hand2", bg="red", fg="white")
        self.kilitle.config(state="normal")

    def dur(self, key):
        if key == keyboard.Key.f11:
            print("Tuşa Basıldı", key)
            self.durdur()
            return False

    def saldir(self, saniye, wincap):
        try:
            self.metine_vur = False
            self.s1 = 0
            self.kontrol = 0
            with keyboard.Listener(on_press=self.dur) as dur:   
                while True:
                    if not dur.running:
                        print("Çıkıldı")
                        break
                    else:
                        ss = wincap.get_screenshot()
                        rectangles = self.cascade.detectMultiScale(ss)

                        if not self.metine_vur:
                            self.metine_vur = True
                            thrd = threading.Thread(target=self.metinevur, args=(rectangles,saniye, wincap))
                            thrd.start()

        except Exception as e:
            self.durdur()
            print("Func: saldir - ",e)
            messagebox.showerror("Hata: saldir", f"Hata Oluştu.\n{e}")

    def metinevur(self,rectangles, metinKesmeSuresi, wincap):
        if len(rectangles) > 0:
            targets = self.vision.get_click_points(rectangles)
            target = wincap.get_screen_position(targets[0])
            pyautogui.moveTo(x=target[0], y=target[1]+5)
            pydirectinput.press("z", presses=1)
            sleep(0.4)
            pyautogui.click(button='left')
            pydirectinput.press("z", presses=1)
            print(self.s,"      Metin Bulundu")
            self.bulunanMetin["text"] = (f"Bulunan Metin: {self.s}")
            sleep(6)    # Metine gitme süresi. Metin taşına yetişemiyorsa bu süreyi arttırın.
            start = time()
            sleep(1)
            pydirectinput.press("z", presses=2)
            sleep(0.1)
            self.s += 1
        else:
            self.s1 += 1
            # print(self.s1, "Bulunamadı")
            pydirectinput.press("e", presses=6)
            pydirectinput.press("f", presses=6)
            self.kontrol += 1
            if self.kontrol >= 3:
                # print("Kontrol", self.kontrol)
                self.kontrol = 0

        self.metine_vur = False

root = Tk()
app = Window(root)
root.wm_title("Metin2 Metin Botu | 14.12.2021")

windowWidth = root.winfo_reqwidth()
windowHeight = root.winfo_reqheight()
positionRight = int(root.winfo_screenwidth()/3 - windowWidth/2)
positionDown = int(root.winfo_screenheight()/3 - windowHeight/2)
root.geometry(f"390x210+{positionRight}+{positionDown}")
root.resizable(width=False, height=False)
def callback(url):
    webbrowser.open_new(url)
me = Label(root, text="Developer: yazilimfuryasi.com | @yazilimfuryasi", fg="#6E7371",cursor="hand2",font="Verdana 7 bold")
me.pack(side=BOTTOM)
adres = "https://www.instagram.com/yazilimfuryasi/"
me.bind("<Button-1>", lambda e: callback(adres))

root.mainloop()
