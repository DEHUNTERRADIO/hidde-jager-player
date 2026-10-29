# Hidde Jager PLAYER

Zwart-gouden soundboard voor optredens. Werkt offline op de iPad als app op het beginscherm.

## Op de iPad installeren

1. Open de GitHub Pages-link van deze repo in **Safari**.
2. Tik op het deelicoon en kies **Zet op beginscherm**.
3. Open de app via het nieuwe icoon. Vanaf nu werkt hij ook zonder internet.
4. Voeg je mp3/wav-nummers toe (maximaal 100). Ze blijven op de iPad bewaard.

## Bediening

- Tik op een pad: afspelen, nog eens tikken: stoppen.
- Driehoek rechtsonder: huidig nummer langzaam naar volume 0 (duur instelbaar via het tandwiel).
- Timer linksonder: **30** of **60** start een aftelklok, tik op de tijd om te pauzeren, **×** reset. In de laatste 5 minuten kleurt hij oranje, daarna telt hij rood door.
- Toetsenbord: spatie = pauze, Esc = stop, F = fade.

## Aanpassen

De bron is `src/player.html`. Na een wijziging: `python3 build.py`, daarna committen en pushen.
