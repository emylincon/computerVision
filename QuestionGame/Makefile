filename = VirtualQuestion

clean:
	rm -rf build
	rm -rf dist
	rm ${filename}.spec

build:
	pyinstaller --onefile -w --paths=../venv/Lib/site-packages  ${filename}.py
	mv dist/${filename}.exe questionGame.exe

install: build clean