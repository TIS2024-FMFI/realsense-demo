# realsense-demo
## Prerekvizity

### Softvér
- Operačný systém Windows 10/11
- Python 3.11

### Hardvér
- Hĺbková kamera Intel Realsense D455

## Inštalácia

Prvým krokom je stiahnutie celého repozitára (napríklad klikutím na zelené tlačidlo “Code” -> “Download ZIP”). Po rozbalení inštalačného balíčka na užívateľom určenom mieste (najlepšie v prázdnom priečinku) treba vo Windows Powershell spustiť následné príkazy:

- pip install pyrealsense2
- pip install opencv-python
- pip install matplotlib
- pip install numpy
- pip install open3d
- pip install pymeshlab

## Spúšťanie

Pred spustením aplikácie sa uistite, že ste vykonali všetky kroky z predchádzajúcich kapitol a že je kamera pripojená k zariadeniu pomocou pribaleného kábla, alebo iného USB-C – USB-A kábla, ktorý podporuje technológiu USB 3.2.

Aplikáciu spustíte dvojkliknutím na súbor main_gui.py v koreni inštalácie.
