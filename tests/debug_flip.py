import faulthandler
from psychopy import visual

faulthandler.enable()
faulthandler.dump_traceback_later(5, repeat=True)

win = visual.Window(
    size=(400, 300),
    fullscr=False,
    checkTiming=False,
    waitBlanking=False,
    winType="pyglet",
    # winType="glfw",
)

print("Backend:", type(win.backend).__name__, flush=True)

# # Workaround
# backend = win.backend
# print(
#     "DisplayLink handler exists:",
#     hasattr(backend, "refreshEventHandlerMacOS"),
#     flush=True,
# )
# if hasattr(backend, "refreshEventHandlerMacOS"):
#     delattr(backend, "refreshEventHandlerMacOS")
#     print("Disabled DisplayLink wait", flush=True)

try:
    print("Before flip", flush=True)
    win.flip()
    print("After flip", flush=True)
finally:
    print("Before close", flush=True)
    win.close()
    print("After close", flush=True)
    faulthandler.cancel_dump_traceback_later()