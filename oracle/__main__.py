from subprocess import Popen, CREATE_NEW_PROCESS_GROUP
import signal
import traceback


procs = {}

def kill(module):
    print(f'Killing {module}...', end='', flush=True)
    procs[module].send_signal(signal.CTRL_C_EVENT)
    procs[module].send_signal(signal.CTRL_BREAK_EVENT)
    procs[module].communicate(timeout=5)
    del procs[module]
    print(' DEAD')

def run(module):
    if module in procs:
        kill(module)
    print(f'Starting {module}...', end='', flush=True)
    procs[module.lower()] = Popen(
        ['python', '-m', module],
        shell=True,
        creationflags=CREATE_NEW_PROCESS_GROUP,
    )
    print(' OK')

def help():
    print('l, ls, list # List servers')
    print('r, restart [server ...] # Restart servers (default all)')
    print('x, exit # Kill servers')
    print('h, help # Docs')
    print()

def ls():
    for i, module in enumerate(procs.keys()):
        print(f'[{i}] {module}')
    print()

def restart(modules):
    try:
        keys = list(procs.keys())
        hit = [
            m if m in keys
            else keys[int(m)]
            for m in modules
        ]
    except Exception:
        print('Invalid server')
        print()
        ls()
        return
    hit = hit or keys
    try:
        for module in hit:
            run(module)
    except Exception:
        print('ERROR')
        raise

help()
run('oracle.api')
run('oracle.gradio')
ls()

try:
    while True:
        command = input('> ').strip().lower().split()
        match command:
            case ['h' | 'help']:
                help()
            case ['l' | 'ls' | 'list']:
                ls()
            case ['r' | 'restart', *servers]:
                restart(servers)
            case ['x']:
                break
            case []:
                pass
            case _:
                help()
except KeyboardInterrupt:
    pass
finally:
    for module in list(procs.keys()):
        try:
            kill(module)
        except Exception:
            print('FAIL')
            traceback.print_exc()
            pass
