from pynput import mouse

def on_click(x, y, button, pressed):
    try:
        if pressed:
            print("{} presionado en ({}, {})".format(button,x,y))
        else:
            print("{} liberado en ({}, {})".format(button,x,y))
        
    except KeyboardInterrupt:
        print("[+] Saliendo...")
        exit(0)
        
def on_scroll(x, y, dx, dy):
    try:
        print('Scrolled {0} a {1}'.format('down' if dy < 0 else 'up',(x, y)))  
        #print('Scrolled {1} a {0}'.format('up' if dx > 0 else 'down',(x, y))) 
    except KeyboardInterrupt:
        print("[+] Saliendo...")
        exit(0)
        
def on_move(x, y):
    print('Pointer moved to {0}'.format((x, y)))
         
with mouse.Listener(on_click=on_click, on_scroll=on_scroll) as listener: #añadir no_move=on_move si queremos monitorizar los movimientos
    listener.join()

    