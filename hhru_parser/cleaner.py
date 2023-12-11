from datetime import datetime
import time 
tm = 1702273167
def cleaner():
    
    while True:
        print(int(time.time()) - tm)
        time.sleep(1)
if __name__ == "__main__":
    cleaner()