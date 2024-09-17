# pdiff

Perceptual Diff `pdiff` ist ein schnelles Bildvergleichsprogramm, das ein Computermodell des menschlichen Sehsystems verwendet, um zwei Bilder zu vergleichen.

![Example](/demo/pdiff_table.png)

Comparison of the visual perception of images

Wahrnehmungsbasierte Bildvergleiche beziehen sich auf Methoden und Techniken zur Bewertung von Unterschieden zwischen Bildern auf der Grundlage der menschlichen visuellen Wahrnehmung und nicht auf rein mathematischen oder pixelbasierten Ansätzen. Diese Art des Vergleichs konzentriert sich darauf, wie Menschen Unterschiede zwischen Bildern wahrnehmen und ist 
besonders nützlich in Bereichen wie der Bewertung der Bildqualität und der Bildverarbeitung.

Wahrnehmungsbasierte Hashes sind ein völlig anderes Konzept als die üblichen kryptografischen Hash-Verfahren wie MD5 oder SHA. Bei kryptografischen Hashes wird ein einseitiger Hashwert auf der Grundlage der Eingabedaten erzeugt. Und aufgrund des Avalanche-Effekts ändert sich der resultierende Hash-Wert vollständig, wenn Sie ein einziges Bit ändern. Aus diesem Grund können zwei Bilder nur dann denselben kryptografischen Hashwert haben, wenn sie exakt gleich sind. Das macht kryptografisches Hashing zu keiner brauchbaren Lösung für dieses Problem.

Im Gegensatz dazu ist ein Wahrnehmungshash ein auf der Bildeingabe basierender Fingerabdruck, der zum Vergleich von Bildern verwendet werden kann, indem die Hamming-Distanz berechnet wird (was im Wesentlichen bedeutet, dass die Anzahl der unterschiedlichen einzelnen Bits gezählt wird). Es gibt verschiedene Algorithmen für das Hashing von Wahrnehmungsbildern, aber alle verwenden ähnliche Schritte, um den Medien-Fingerabdruck zu erzeugen. Der am einfachsten zu erklärende ist der Average Hash (auch aHash genannt). Nehmen wir das folgende Bild und sehen wir uns an, wie es funktioniert.

**1. Verkleinerung**

Zunächst wird das Bild auf 8x8 Pixel verkleinert. Dies ist der schnellste Weg, um hohe Frequenzen und Details zu entfernen. In diesem Schritt werden die ursprüngliche Größe und das Seitenverhältnis ignoriert und immer auf 8x8 reduziert, so dass wir 64 resultierende Pixel haben.

**2. Farbe reduzieren**

Da wir nun 64 Pixel mit ihrem jeweiligen RGB-Wert haben, reduzieren wir die Farbe, indem wir das Bild in Graustufen umwandeln. So bleiben 64 Farbwerte übrig.

**3. Berechnung der durchschnittlichen Farbe**

Dies ist ziemlich selbsterklärend: Berechnen Sie die durchschnittliche Farbe auf der Grundlage der vorherigen 64 Werte.

**4. Den Hash-Wert berechnen**

The final fingerprint is calculated based on whether a pixel is lighter or darker than the average grayscale value we just calculated. Do this for each pixel and you will get a 64-bit hash.

**5. Vergleich von Bildern**

Um doppelte oder ähnliche Bilder zu erkennen, berechnen Sie die Wahrnehmungshashes für beide Bilder:

```
Original:  1100100101101001001111000001100000001000000000000000011100111111
Thumbnail: 1100100101101001001111000001100000001000000000000000011100111111
```

Wie Sie sehen können, sind beide Hashes identisch. Das bedeutet aber nicht, dass ähnliche Bilder immer gleiche Hashes erzeugen! Wenn wir das Originalbild manipulieren und ein Wasserzeichen hinzufügen, erhalten wir diese Hashes:

```
Original:  1100100101101001001111000001100000001000000000000000011100111111
Watermark: 1100100101111001001111000001100000011000000010000000011100111111
```

Wie Sie sehen können, sind diese Hashes sehr ähnlich, aber nicht gleich. Um diese Hashes zu vergleichen, zählen wir die Anzahl der unterschiedlichen Bits (Hamming-Abstand), der in diesem Fall 3 beträgt. Je größer dieser Abstand ist, desto geringer ist die Veränderung der identischen oder ähnlichen Bilder.

**6. Andere Implementierungen**

Die Implementierung von Average Hash ist die einfachste und schnellste, aber sie scheint etwas zu ungenau zu sein und erzeugt einige falsch positive Ergebnisse. Zwei weitere Implementierungen sind Difference Hash (oder dHash) und pHash. Difference Hash folgt denselben Schritten wie Average Hash, erzeugt aber den Fingerabdruck auf der Grundlage, ob das linke Pixel heller ist als das rechte, anstatt einen einzelnen Durchschnittswert zu verwenden. 

Im Vergleich zu Average Hash erzeugt es weniger falsch-positive Ergebnisse, was es zu einer großartigen Standardimplementierung macht. pHash ist eine Implementierung, die sich von den anderen unterscheidet und einige wirklich ausgefallene Dinge tut, um die Genauigkeit zu erhöhen. Sie ändert die Größe eines 32x32-Bildes, ermittelt den Luma-Wert (Helligkeitswert) jedes Pixels und wendet eine "discrete cosine transform" (DCT) auf die Matrix an. 

Anschliessend werden die oberen linken 8x8 Pixel, die die niedrigsten Frequenzen im Bild darstellen, zur Berechnung des resultierenden Hashwerts verwendet, indem jedes Pixel mit dem Medianwert verglichen wird. Aufgrund seiner Komplexität ist es auch das langsamste Verfahren.

## Mögliche Anwendungsbereiche für Perceptual Diff

### Bild- und Videokompression
Kann verwendet werden, um die Auswirkungen verschiedener Komprimierungstechniken auf die visuelle Qualität zu bewerten. Algorithmen wie SSIM helfen sicherzustellen, dass komprimierte Bilder oder Videos für das menschliche Auge visuell akzeptabel bleiben.

### Qualitätssicherung in der digitalen Bildverarbeitung
Bearbeitungsprozesse können überprüft werden, um sicherzustellen, dass sie keine unerwünschten visuellen Artefakte erzeugen.

### Medizinische Bildgebung
Kann dazu beitragen, die Qualität medizinischer Bilder nach der Komprimierung oder Übertragung aufrechtzuerhalten, um sicherzustellen, dass wichtige Informationen erhalten bleiben.

### Bild- und Videoüberwachung
Kann verwendet werden, um die Wirksamkeit von Videoüberwachungssystemen zu bewerten, insbesondere nach der Komprimierung oder bei schlechten Lichtverhältnissen.

### Benchmarking von Bildverarbeitungsalgorithmen
Bietet eine Möglichkeit, Algorithmen auf der Grundlage der wahrgenommenen Bildqualität zu bewerten, anstatt sich nur auf numerische Leistungsindikatoren zu verlassen.

### Wissenschaftliche Forschung
Kann zur Durchführung von Experimenten zur Bestimmung von Wahrnehmungsschwellen und anderen Aspekten der visuellen Verarbeitung verwendet werden.

### E-Commerce und Online Marketing
Es kann auch verwendet werden, um sicherzustellen, dass Bilder auf einer Website nach der Komprimierung immer noch die gewünschte Wirkung erzielen, ohne dass wichtige Details verloren gehen.

### Automatisierte Bildverbesserung
Damit lässt sich feststellen, welche Verbesserungen tatsächlich zu einer wahrnehmbaren Verbesserung der Bildqualität führen.

### Soziale Medien und Bild-/Videodatenbanken
Wird beispielsweise zur Identifizierung von Personen (OSINT) verwendet.

Es wird auch eingesetzt, um kriminelle Inhalte wie Pornografie oder illegale Gegenstände (Waffen, Drogen 
usw.) zu erkennen.

Gesperrte Bilder, z.B. wegen Urheberrechtsverletzungen, können identifiziert werden.

Verringerung des Speicherplatzes in einer Datenbank durch Erkennung bereits vorhandener Bilder.


## Features

 - Vergleich von mehreren Bildern
 - Vergleich von zwei bestimmten Bildern
 - Unterstützung für verschiedene Bildformate (JPG, PNG, BMP, GIF, TIFF, WEBP, PPM)
 - Anzeige der prozentualen Abweichung
 - Filterung ähnlicher Bilder (5% oder weniger Unterschied)
 - Tabellenausgabe der Ergebnisse
    - Anzeige der Dateigröße
    - Anzeige der Pixelgröße
    - Anzeige der Hashwerte (MD5, SHA256, etc.)
    - Anzeige der Vergleichszeit pro Bildpaar
    - Anzeige einer ID-Spalte mit fortlaufender Nummerierung
- Erstellung von Berichten im HTML-Format zur besseren Visualisierung
- Exportformate (HTML, CSV, JSON)
- Statistische Ausgabe für Vergleiche (Leistung, Anzahl der Vergleiche, usw.)
- Unterstützung für verschiedene Hash-Algorithmen (MD5, SHA256, etc.)

## 160.000

Mit pdiff können bis zu 160.000 Bildpaare in einer Stunde verglichen werden.

Getestet mit:
- 4 GB RAM
- 2x vCPU (Apple ARM M3)
- Debian GNU/Linux v12


## Unterstützte Formate

### Export-Formate

- '.csv', '.json', '.html'

#### HTML Report
![HTML_Report](/demo/html_report.png)


#### JSON Report
![JSON Report](/demo/json_report.png)

#### CSV Report
![CSV Report](/demo/csv_report.png)



### Bildformate

- '.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp', '.ppm']

Erweitert, kann im pdiff-Skript geändert werden

- '.PPM', 'pnm', '.ico', '.pdf', '.eps' '.IM', '.DIB', '.MPO', '.tga', '.pcx' ,'.xbm' '.xv'

### Hash-Algorithmen

- 'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512'

Zusätzliche Hash-Funktionen Je nach Betriebssystem und verfügbaren OpenSSL-Bibliotheken können auch die folgenden Hash-Funktionen unterstützt werden:

- 'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512', 'blake2b', 'blake2s', 'shake_128', 'shake_256'


## Benutzerdefinierte Toleranz

Der Parameter -p oder --percent gibt an, um wie viel Prozent die Bilder maximal abweichen dürfen, damit sie noch als „identisch“ gelten. Der Standardwert ist 100, was bedeutet, dass jede Abweichung als Unterschied zählt. Wenn Sie den Wert -p nicht angeben.

Die maximale Abweichung (max_difference) wird anhand des angegebenen Prozentsatzes berechnet. Die maximale Hamming-Distanz für den average_hash beträgt 64 (da der Hash 64 Bit lang ist). Wenn z.B. -p 80 angegeben wird, bedeutet dies, dass ein Unterschied von bis zu 20 % des Maximalwerts (d. h. bis zu 12,8) noch als identisch angesehen wird.

Beim Vergleich verschiedener Bilder habe ich festgestellt, dass Bilder, die sich sehr ähnlich sind, in der Regel eine Abweichung von weniger als 5 % aufweisen. Deshalb habe ich den Parameter -s -simular hinzugefügt, der nur Bilder ausgibt, die eine berechnete Abweichung von 5% haben. Sie können auch -p5 verwenden, um das gleiche Ergebnis zu erhalten.

## Pre-Setup

### Einrichten einer Entwicklungsumgebung

Nicht unbedingt notwendig, denn Sie können das Repo auch als tar.gz herunterladen.

### Git Installation

```
sudo apt install -y git
```

Wenn Sie Ihre Änderungen für das pdiff-Projekt über git einchecken möchten, sollten Sie auch Ihren Namen und Ihre E-Mail-Adresse für git angeben.

```
git config --global user.name "Vorname Nachname"
git config --global user.email "deine@email-adresse.com"
```

## Setup pdiff

### Installation der erforderlichen Python3-Module

Es gibt einige Module, die zusätzlich installiert werden müssen. Die anderen von pdiff verwendeten Module sollten bereits durch die Python-Installation eingerichtet worden sein.

```
pip3 install Image imagehash futures tabulate
```

```
mkdir -p ~/dev/
cd ~/dev/
git clone https://github.com/rtulke/pdiff.git
```

Wir haben nun pdiff heruntergeladen und es befindet sich im Verzeichnis `~/dev` unterhalb Ihres Benutzerverzeichnisses. 

Wenn Sie pdiff als Befehl ausführen wollen, sollten Sie die folgenden Anpassungen vornehmen. Ansonsten müssten Sie immer `python3 pdiff.py <parameter> <argument>.` schreiben.


```
mkdir -p ~/bin/
cd ~/dev/pdiff
cp pdiff.py ~/bin/pdiff
chmod +x ~/bin/pdiff
```

Um den Pfad als Benutzer in Ihrem System bekannt zu machen, können Sie entweder die Datei `~/.profile` oder die Datei `~/.bashrc` bearbeiten und diese zu Ihrer bestehenden Pfadvariable hinzufügen.

Verwenden Sie Ihren bevorzugten Editor und bearbeiten Sie eine der beiden Dateien.

```
vim ~/.bashrc
```

Fügen Sie den folgenden Inhalt in einer neuen Zeile am Ende der Datei ein.

```
export PATH="$PATH:~/bin"
``` 
Damit das Ganze auch im System geladen wird, sollten Sie nun die zuvor ausgewählte Datei `~/.bashrc` oder `~/.profile` erneut laden. Dies tun wir mit `source ~/.bashrc` oder `source ~/.profile`

```
source ~/.bashrc
```

Jetzt sollten Sie den Befehl problemlos ausführen können.

```
pdiff --help

usage: pdiff.py [-h] -i INPUT [INPUT ...] [-p PERCENT] [-s] [-o OUTPUT OUTPUT] [-T] [-t] [-N] [-H HASH] [-P] [-F] [-S]

Compare images in a directory or two specific image files using hashes.

options:
  -h, --help            show this help message and exit
  -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                        Path to a directory or to two image files
  -p PERCENT, --percent PERCENT
                        Percentage of maximum deviation that is considered identical (e.g., -p 80 means 20% deviation allowed)
  -s, --similar         Only print images with up to 5% difference
  -o OUTPUT OUTPUT, --output OUTPUT OUTPUT
                        Output format and file, e.g., "-o html output.html" or "-o csv output.csv" or "-o json output.json"
  -t, --table           Display comparison results as a text table
  -T, --time            Display comparison time for each image pair
  -N, --id              Add an ID column with a running number
  -H HASH, --hash HASH  Display hash for the specified algorithm (e.g., sha256, md5, etc.)
  -P, --pixel-size      Display image dimensions in pixels (width x height) in the table
  -F, --file-size       Display file size of images in the table
  -S, --stats           Display statistics: total time, average time per comparison, and number of comparisons

``` 


## Verwendung

Sie können das Skript nun wie folgt verwenden.

### So vergleichen Sie ein ganzes Verzeichnis

Stellen Sie sicher, dass sich die Bilder im angegebenen Verzeichnis befinden und dass die Bildformate auch von pdiff unterstützt werden. Siehe Unterstützte Bildformate 

```
pdiff -i /pfad/zum/bild-verzeichnis -p 80
```

### Für einen direkten Vergleich von zwei Bilddateien

```
pdfiff -i bild1.jpg bild2.png -p 98
```

### Für einen Vergleich mehrerer Bilder in einem Verzeichnis, bei dem nur Bilder ausgegeben werden, die sich so ähnlich wie möglich sind.

```
pdfiff -i /pfad/zum/bild-verzeichnis -s
```

Ohne den Parameter -p, d.h. es wird der Standardwert (100) verwendet.

```
pdfiff -i bild1.jpg bild2.png 
```

oder

```
pdfiff -i /pfad/zum/bild-verzeichnis
```

Erstellen eines html-Berichts, mit nur ähnlichen Bildern oder geringen Abweichungen.

```
pdiff -i static/ -s -o html index.html
```

Du möchtest gerne alles mögliche anzeigen und sehen?

```
pdiff -i static/ -p90 -t -T -N -H md5 -P -F -S -o html index.html
```

