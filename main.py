import ctypes
import random
import ctypes.wintypes
import threading

# рандом переменная
n = 0

# константы для перехвата обоев
WM_SETTINGCHANGE = 0x001A
SPI_SETDESKWALLPAPER = 0x0014

# константы для ошибок
MB_ICONERROR = 0x00000010
MB_OK = 0x00000000
MB_TOPMOST = 0x00040000
MB_SYSTEMMODAL = 0x00001000

# обои
DEFAULT_WALLPAPER = r"C:\Windows\Web\Wallpaper\Windows\img0.jpg"

ctypes.windll.user32.DefWindowProcW.argtypes = [ctypes.wintypes.HWND, ctypes.wintypes.UINT, ctypes.wintypes.WPARAM,
                                                ctypes.wintypes.LPARAM]
ctypes.windll.user32.DefWindowProcW.restype = ctypes.c_int64

is_resetting = False


def show_test_error():  # рандомная ошибка
    n = random.randint(1, 4)

    if n == 1:
        g = str(":D")
    if n == 2:
        g = str("Неа!")
    if n == 3:
        g = str("Попробуй опять :D")
    if n == 4:
        g = str("Хорошая попытка")
    title = "WalpCheck"
    message = (
        g
    )

    ctypes.windll.user32.MessageBoxW(None, message, title, MB_OK | MB_ICONERROR | MB_TOPMOST)  # вызов ошибки


def walpcheck_back():  # возврат обоев
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, DEFAULT_WALLPAPER, 0)


def window_proc(hwnd, msg, wparam, lparam):  # крутая вещь (перехват)
    global is_resetting

    if msg == WM_SETTINGCHANGE:
        if is_resetting:
            return ctypes.windll.user32.DefWindowProcW(hwnd, msg, wparam, lparam)

        try:
            param_str = ctypes.cast(lparam, ctypes.c_wchar_p).value if lparam else ""
        except:
            param_str = ""

        if wparam == SPI_SETDESKWALLPAPER or param_str == "Desktop":
            is_resetting = True
            walpcheck_back()

            threading.Thread(target=show_test_error, daemon=True).start()

            is_resetting = False

    return ctypes.windll.user32.DefWindowProcW(hwnd, msg, wparam, lparam)


def start_monitoring():  # запуск + перехват
    user32 = ctypes.windll.user32
    user32.CreateWindowExW.argtypes = [
        ctypes.wintypes.DWORD,  # 1 dwExStyle
        ctypes.wintypes.LPCWSTR,  # 2 lpClassName
        ctypes.wintypes.LPCWSTR,  # 3 lpWindows Name
        ctypes.wintypes.DWORD,  # 4 dwStyle
        ctypes.c_int,  # 5 x
        ctypes.c_int,  # 6 y
        ctypes.c_int,  # 7 nWidth
        ctypes.c_int,  # 8 nHeight
        ctypes.wintypes.HWND,  # 9 hWndParent
        ctypes.wintypes.HMENU,  # 10 HMENU
        ctypes.wintypes.HINSTANCE,  # hInstance
        ctypes.wintypes.LPVOID  # 11 lpParam
    ]
    user32.CreateWindowExW.restype = ctypes.wintypes.HWND

    WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_int64, ctypes.wintypes.HWND, ctypes.wintypes.UINT, ctypes.wintypes.WPARAM,
                                 ctypes.wintypes.LPARAM)

    class WNDCLASS(ctypes.Structure):
        _fields_ = [("style", ctypes.wintypes.UINT),
                    ("lpfnWndProc", WNDPROC),
                    ("cbClsExtra", ctypes.c_int),
                    ("cbWndExtra", ctypes.c_int),
                    ("hInstance", ctypes.wintypes.HINSTANCE),
                    ("hIcon", ctypes.wintypes.HICON),
                    ("hCursor", ctypes.wintypes.HANDLE),
                    ("hbrBackground", ctypes.wintypes.HBRUSH),
                    ("lpszMenuName", ctypes.wintypes.LPCWSTR),
                    ("lpszClassName", ctypes.wintypes.LPCWSTR)]

    global _wndproc_callback_keep_alive
    _wndproc_callback_keep_alive = WNDPROC(window_proc)

    wc = WNDCLASS()
    wc.lpfnWndProc = _wndproc_callback_keep_alive
    wc.lpszClassName = "WallpaperGuardClass"
    wc.hInstance = ctypes.windll.kernel32.GetModuleHandleW(0)

    ctypes.windll.user32.RegisterClassW(ctypes.byref(wc))

    ctypes.windll.user32.CreateWindowExW(
        0,
        wc.lpszClassName,
        "Guard",
        0,
        0, 0, 0, 0,
        None,
        None,
        wc.hInstance,
        None
    )

    print("запуск")
    try:
        msg = ctypes.wintypes.MSG()
        while ctypes.windll.user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
            ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
            ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    start_monitoring()
