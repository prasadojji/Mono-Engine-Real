import winreg

progid = "Broker.Application"
try:
    key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, progid + "\\CLSID")
    clsid = winreg.EnumValue(key, 0)[1]
    print(f"CLSID for Broker.Application: {clsid}")
    winreg.CloseKey(key)

    # Optional: Get TypeLib GUID
    clsid_key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f"CLSID\\{clsid}\\TypeLib")
    typelib_guid = winreg.EnumValue(clsid_key, 0)[1]
    print(f"TypeLib GUID: {typelib_guid}")
    winreg.CloseKey(clsid_key)
except Exception as e:
    print(f"Error: {str(e)}")