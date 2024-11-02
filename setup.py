from cx_Freeze import setup, Executable

setup(
    name="MyApp",
    version="1.0",
    description="My application description",
    executables=[Executable("main.py")],
    options={
        'build_exe': {
            'include_files': ["D:\\test\\ForFM\\DataMatrixPrint\\.venv\\Lib\\site-packages\\pylibdmtx\\libdmtx-64.dll", "D:\\test\\ForFM\\DataMatrixPrint\\.venv\\Lib\\site-packages\\pypdfium2_raw\\pdfium.dll"],
        },
    },
)
