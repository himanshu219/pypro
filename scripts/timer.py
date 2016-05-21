import datetime
import time
import sys
import signal
breaktime = datetime.timedelta(0, 0, 0)
def exit_gracefully(signum, frame):
    global breaktime
    previous = datetime.datetime.now()
    signal.signal(signal.SIGINT, original_sigint)        
    try:
        if raw_input("\nReally quit? (y/n)> ").lower().startswith('y'):
            sys.exit(1)                                  
    except KeyboardInterrupt:
        print("Ok ok, quitting")
        sys.exit(1)
                                                         
    signal.signal(signal.SIGINT, exit_gracefully)
    breaktime += (datetime.datetime.now()-previous)
                                                                 
def run_program():
    start = datetime.datetime.now()
    while True:
        now = datetime.datetime.now()
        sys.stdout.write('{0} {1} passed {2} extra\r'.format(now, now-start-breaktime, breaktime))
        sys.stdout.flush()
        # print '{}\r'.format(now),
        time.sleep(1)

if __name__ == '__main__':
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_gracefully)
    run_program()
