::Check to see if wia is currently registered with this machine (Won't be if it's XP)
IF NOT EXIST C:\WINDOWS\system32\wiaaut.dll (
    echo Could not find wia, going to register the dll
    regsvr32.exe wiaaut.dll
) ELSE (
    echo Found it!
)