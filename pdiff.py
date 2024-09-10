#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Comparison Tool

Das Skript 'pdiff' vergleicht Bilder auf der Grundlage eines Wahrnehmungshashs der imagehash-Bibliothek. 

Features:
 - Vergleich mehrerer Bilder
 - Vergleich zweier bestimmter Bilder
 - Unterstützung für verschiedene Bildformate (JPG, PNG, BMP, GIF, TIFF, WEBP, PPM)
 - Anzeige der prozentualen Abweichung
 - Filterung von ähnlichen Bildern (5% oder weniger Unterschied)
 - Tabellenausgabe der Ergebnisse
    - Anzeige der Dateigröße
    - Anzeige der Pixelgröße
    - Anzeige von Hash-Werten (MD5, SHA256, etc.)
    - Anzeige der Vergleichszeit je Bildpaar
    - Anzeige einer ID-Spalte mit fortlaufender Nummerierung
- Generierung von Berichten in einem HTML Format zur besseren visuellen darstellung
- Export Formate (HTML, CSV, JSON)
- Statistische Ausgabe für Vergleiche (Perfomance, Anzahl der Vergleiche, etc.)
- Unterstützung für verschiedene Hash-Algorithmen (MD5, SHA256, etc.)

Author: Robert Tulke
Date: 2024-11-08
"""


import os
import hashlib
import argparse
import time
import json
import csv
from PIL import Image
import imagehash
import concurrent.futures
from tabulate import tabulate 

# Unterstützte Bild-Formate
SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp', '.ppm']

# Funktionen zum Konvertieren von Bytes in ein menschenlesbares Format
def human_readable_size(size, decimal_places=2):
    """Convert bytes into a human-readable format (KB, MB, etc.)."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:              # Einheiten für die Dateigröße
        if size < 1024.0:                                   # Größe kleiner als 1024 Bytes
            return f"{size:.{decimal_places}f} {unit}"      # Größe und Einheit zurückgeben
        size /= 1024.0                                      # Größe durch 1024 teilen

# Funktion zum Berechnen des Hash-Werts für eine Datei
def calculate_hash(file_path, hash_algorithm):
    """Calculate the hash for the file at the given path using the specified hash algorithm."""
    hash_func = hashlib.new(hash_algorithm)                 # Hash-Algorithmus auswählen 
    with open(file_path, "rb") as f:                        # Datei im Binärmodus öffnen
        for byte_block in iter(lambda: f.read(4096), b""):  # Datei in Blöcken von 4096 Bytes lesen
            hash_func.update(byte_block)                    # Hash für jeden Block berechnen
    return hash_func.hexdigest()                            # Hash-Wert als Hexadezimalzahl zurückgeben

# Funktion zum Ermitteln der Bildabmessungen
def get_image_dimensions(file_path):
    """Get the dimensions (width x height) of the image."""
    with Image.open(file_path) as img:                      # Bild mit Pillow öffnen
        return img.size  # Returns (width, height)          # Bildgröße zurückgeben

# Klasse zum Vergleichen von Bildern
class ImageComparator:
    #  Konstruktor der Klasse ImageComparator
    def __init__(self, input_paths, percent=100, similar=False, output_file=None, output_format=None, show_time=False, show_table=False, show_id=False, hash_algorithm=None, show_pixel_size=False, show_file_size=False, show_stats=False):
        self.input_paths = input_paths                      # Die Pfade zu den Eingabebildern    
        self.percent = percent                              # Der Prozentsatz der maximalen Abweichung, der als identisch betrachtet wird
        self.similar = similar                              # Filtert ähnliche Bilder (5% oder weniger Unterschied)
        self.output_file = output_file                      # Der Dateipfad für die Ausgabe
        self.output_format = output_format                  # Das Ausgabeformat (csv, html, json)
        self.show_time = show_time                          # Steuert die Ausgabe der Vergleichszeit
        self.show_table = show_table                        # Steuert die Ausgabe der Ergebnisse als Tabelle
        self.show_id = show_id                              # Steuert die Ausgabe der ID-Spalte
        self.hash_algorithm = hash_algorithm                # Steuert die Ausgabe des Hash-Werts
        self.show_pixel_size = show_pixel_size              # Steuert die Ausgabe der Pixelgröße
        self.show_file_size = show_file_size                # Steuert die Ausgabe der Dateigröße
        self.show_stats = show_stats                        # Steuert die Ausgabe der Statistiken
        self.max_hash_value = 64                            # Der maximale Hash-Wert für den durchschnittlichen Hash, da der average_hash einen 8x8-Hash verwendet, beträgt die maximale Differenz 64
        self.max_difference = self.max_hash_value * (self.percent / 100)  # Maximale Differenz basierend auf dem Prozentsatz

    # Funktion zum Berechnen des Wahrnehmungshashs
    def calculate_phash(self, image_path):
        with Image.open(image_path) as img:                 # Bild mit Pillow öffnen
            return imagehash.average_hash(img)              # Durchschnittlichen Hash für das Bild berechnen und zurückgeben

    # Funktion zum Vergleichen von Hashes
    def compare_hashes(self, hash1, hash2):
        """Compare two perceptual hashes."""
        return hash1 - hash2                                # Differenz zwischen den Hashes berechnen und zurückgeben

    # Funktion zum Vergleichen 2er Bildern basierend auf dem Wahrnehmungshash 
    def compare_images(self, image1, image2):
        start_time = time.time()                                        # Startzeit für jedes Paar    

        hash1 = self.calculate_phash(image1)                            # Wahrnehmungshash für Bild 1 berechnen
        hash2 = self.calculate_phash(image2)                            # Wahrnehmungshash für Bild 2 berechnen
        
        difference = self.compare_hashes(hash1, hash2)                  # Hashes vergleichen
        difference_percent = (difference / self.max_hash_value) * 100   # Differenz in Prozent umrechnen
        is_within_percent = difference_percent <= self.percent          # Überprüfen, ob die Differenz innerhalb des zulässigen Prozentsatzes liegt

        end_time = time.time()                                          # Endzeit für jedes Paar
        comparison_time = end_time - start_time                         # Vergleichszeit berechnen von Start- und Endzeit
        
        return (image1, image2, difference_percent, is_within_percent, comparison_time) # Ergebnisse zurückgeben, Bild 1, Bild 2, Differenz, Prozent, Vergleichszeit

    # Funktion zum Vergleichen mehrerer Bilder
    def compare_multiple_images(self, image_list):
        image_pairs = [(image_list[i], image_list[j]) for i in range(len(image_list)) for j in range(i + 1, len(image_list))] # Bildpaare erstellen aus der Liste der Bilder
       
        all_differences = [] # Liste für alle Unterschiede erstellen 
        
        
        with concurrent.futures.ThreadPoolExecutor() as executor:                                           # Multithreading für parallele Ausführung
            futures = [executor.submit(self.compare_images, pair[0], pair[1]) for pair in image_pairs]      # Vergleich für jedes Bildpaar ausführen
            
            for future in concurrent.futures.as_completed(futures):                                         # Ergebnisse verarbeiten, wenn sie verfügbar sind
                image1, image2, difference_percent, is_within_percent, comparison_time = future.result()    # Ergebnisse abrufen
                if is_within_percent:                                                                       # Nur Ergebnisse hinzufügen, die innerhalb des zulässigen Prozentsatzes liegen
                    all_differences.append({                                                                # Ergebnisse hinzufügen
                        "image1": image1,   
                        "image2": image2, 
                        "difference": difference_percent,                                                   # Differenz in Prozent
                        "comparison_time": comparison_time,                                                 # Vergleichszeit
                    })
        
        all_differences.sort(key=lambda x: x['difference'])                                                 # Ergebnisse nach Differenz sortieren   
        
        return all_differences                                                                              # Ergebnisse zurückgeben                      

    # Funktion zum Überprüfen, ob die Datei ein unterstütztes Bildformat ist
    def is_supported_image(self, file_path):
        return any(file_path.lower().endswith(ext) for ext in SUPPORTED_FORMATS)                            # Überprüfen, ob die Dateiendung in der Liste der unterstützten Formate enthalten ist

    # Funktion zur Ermittlung der Dateigröße
    def get_image_size(self, file_path):
        return human_readable_size(os.path.getsize(file_path))                                              # Dateigröße in ein menschenlesbares Format umwandeln

    # Funktion zum Generieren der Tabellendaten
    def generate_table_data(self, all_differences):
        table_data = []                                                                                     # Tabelle für die Daten erstellen                    
        headers = []                                                                                        # Kopfzeile für die Tabelle erstellen    

        # Spaltenüberschriften hinzufügen wenn --id angegeben ist
        if self.show_id:
            headers.append("ID")

        headers.extend(["Image 1", "Image 2", "Difference (%)"])    # Spaltenüberschriften hinzufügen 

        # Dateigröße hinzufügen wenn --file-size angegeben ist (je Bild)
        if self.show_file_size:
            headers.append("Image 1 Size")
            headers.append("Image 2 Size")

        # Pixelgröße hinzufügen wenn --pixel-size angegeben ist (je Bild)
        if self.show_pixel_size:
            headers.append("Image 1 Dimensions")
            headers.append("Image 2 Dimensions")

        # Hash-Werte hinzufügen wenn --hash angegeben ist (je Bild)
        if self.hash_algorithm:
            headers.append(f"Image 1 {self.hash_algorithm.upper()} Hash")
            headers.append(f"Image 2 {self.hash_algorithm.upper()} Hash")

        # Vergleichszeit hinzufügen wenn --time angegeben ist
        if self.show_time:
            headers.append("Comparison Time")

        # Tabellendaten generieren
        for index, diff in enumerate(all_differences, start=1):
            row = []

            # ID hinzufügen wenn --id angegeben ist
            if self.show_id:
                row.append(index)

            # Bildnamen hinzufügen, Dateiname extrahieren, differenz in Prozent hinzufügen (je Bild)
            image1_name = os.path.basename(diff['image1'])
            image2_name = os.path.basename(diff['image2'])
            
            row.extend([
                image1_name,
                image2_name,
                f"{diff['difference']:.2f}%"
            ])

            # Dateigröße hinzufügen wenn --file-size angegeben ist (je Bild)
            if self.show_file_size:
                image1_size = self.get_image_size(diff['image1'])
                image2_size = self.get_image_size(diff['image2'])
                row.append(image1_size)
                row.append(image2_size)

            # Pixelgröße hinzufügen wenn --pixel-size angegeben ist (je Bild)
            if self.show_pixel_size:
                image1_dimensions = f"{get_image_dimensions(diff['image1'])[0]}x{get_image_dimensions(diff['image1'])[1]} px"
                image2_dimensions = f"{get_image_dimensions(diff['image2'])[0]}x{get_image_dimensions(diff['image2'])[1]} px"
                row.append(image1_dimensions)
                row.append(image2_dimensions)

            # Hash-Werte hinzufügen wenn --hash angegeben ist (je Bild)
            if self.hash_algorithm:
                image1_hash = calculate_hash(diff['image1'], self.hash_algorithm)
                image2_hash = calculate_hash(diff['image2'], self.hash_algorithm)
                row.append(image1_hash)
                row.append(image2_hash)

            # Berechnungszeit hinzufügen wenn --time angegeben ist (je Bildpaar)
            if self.show_time:
                row.append(f"{diff['comparison_time']:.4f} seconds")

            table_data.append(row) # Zeile zur Tabelle hinzufügen 

        return headers, table_data # Kopfzeile und Tabellendaten zurückgeben

    # Funktion zum Filtern ähnlicher Bilder (5% oder weniger Unterschied) wenn -s oder --similar angegeben ist
    def filter_similar_images(self, all_differences):
        if self.similar:
            return [diff for diff in all_differences if diff['difference'] <= 5.0]
        return all_differences

    # Funktion zum Ausgeben der Unterschiede in der Konsole als Texttabelle, wenn -t verwendet wird, oder als einfache Ausgabe, wenn nicht.
    def print_differences(self, all_differences):
        if not all_differences:
            print(f"No images found that match the specified deviation of {self.percent}%.")
            return

        # Filter für ähnliche Bilder anwenden, wenn -s verwendet wird
        all_differences = self.filter_similar_images(all_differences)

        # Erstellen der Kopfzeile und der Tabellendaten
        headers, table_data = self.generate_table_data(all_differences)

        # Tabellenausgabe, wenn -t verwendet wird
        if self.show_table:
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
        else:
            # Einfache Ausgabe der Unterschiede
            for index, diff in enumerate(all_differences, start=1):
                output = ""

                # Hinzufügen der Spalte ID, wenn --id verwendet wird
                if self.show_id:
                    output += f"ID: {index}, "

                # Anzeigen der Bildnamen je Bildpaar
                output += f"Image 1: {os.path.basename(diff['image1'])}, Image 2: {os.path.basename(diff['image2'])}, "

                # Anzeigen der Differenz in Prozent
                output += f"Difference: {diff['difference']:.2f}%"

                # Anzeigen der Vergleichszeit, wenn --time verwendet wird
                if self.show_time:
                    output += f", Comparison time: {diff['comparison_time']:.4f} seconds"

                # Anzeigen des Hash-Werts, wenn --hash verwendet wird
                if self.hash_algorithm:
                    image1_hash = calculate_hash(diff['image1'], self.hash_algorithm)
                    image2_hash = calculate_hash(diff['image2'], self.hash_algorithm)
                    output += f", Image 1 {self.hash_algorithm.upper()} Hash: {image1_hash}, Image 2 {self.hash_algorithm.upper()} Hash: {image2_hash}"

                # Anzeigen der Pixelgröße, wenn --pixel-size (-P) verwendet wird
                if self.show_pixel_size:
                    image1_dimensions = f"{get_image_dimensions(diff['image1'])[0]}x{get_image_dimensions(diff['image1'])[1]} px"
                    image2_dimensions = f"{get_image_dimensions(diff['image2'])[0]}x{get_image_dimensions(diff['image2'])[1]} px"
                    output += f", Image 1 Dimensions: {image1_dimensions}, Image 2 Dimensions: {image2_dimensions}"

                # Anzeigen der Dateigröße, wenn --file-size (-F) verwendet wird
                if self.show_file_size:
                    image1_size = self.get_image_size(diff['image1'])
                    image2_size = self.get_image_size(diff['image2'])
                    output += f", Image 1 Size: {image1_size}, Image 2 Size: {image2_size}"

                print(output)

    # Funktion zum Generieren eines HTML-Berichts unter Verwendung des Moduls tabulate
    def generate_html_report(self, all_differences):
        headers, table_data = self.generate_table_data(all_differences) # Kopfzeile und Tabellendaten generieren

        # Ermitteln des Bildverzeichnisses basierend auf den Eingabemöglickeiten, um die relativen Pfade zu berechnen
        if len(self.input_paths) == 1 and os.path.isdir(self.input_paths[0]):   # Verzeichnismodus
            image_directory = self.input_paths[0]                               # Bildverzeichnis festlegen    
        else:
            image_directory = os.path.dirname(self.input_paths[0])              # 2-Bild-Modus, Bildverzeichnis festlegen

        # Aktualisieren der Tabellendaten mit Bild-Tags anstelle von Dateinamen
        updated_table_data = [] # Aktualisierte Tabellendaten erstellen
        for row in table_data:  # Für jede Zeile in den Tabellendaten
            updated_row = []

            # ID-Spalte hinzufügen, wenn --id angegeben ist
            if self.show_id:
                id_column = row[0]
                image1_name = str(row[1])
                image2_name = str(row[2])
            else:
                # ID-Spalte nicht vorhanden
                image1_name = str(row[0])
                image2_name = str(row[1])

            # Bildpfade für Bild 1 und Bild 2 erstellen
            image1_path = os.path.join(image_directory, image1_name)
            image2_path = os.path.join(image_directory, image2_name)

            relative_image1_path = os.path.relpath(image1_path, os.path.dirname(self.output_file))
            relative_image2_path = os.path.relpath(image2_path, os.path.dirname(self.output_file))

            # Bild-Tags für Bild 1 und Bild 2 erstellen und Bildnamen hinzufügen - max. Breite 200px, abgerundete Ecken 8px 
            image1_tag = f"<img src='{relative_image1_path}' alt='Image 1' style='max-width: 200px; border-radius: 8px;'><br><small>{image1_name}</small>"
            image2_tag = f"<img src='{relative_image2_path}' alt='Image 2' style='max-width: 200px; border-radius: 8px;'><br><small>{image2_name}</small>"

            # ID-Spalte hinzufügen, wenn --id angegeben ist
            if self.show_id:
                updated_row.append(id_column) 

            updated_row.extend([image1_tag, image2_tag] + row[3:] if self.show_id else [image1_tag, image2_tag] + row[2:])  # Spaltenreihenfolge beibehalten
            updated_table_data.append(updated_row)

        # HTML-Inhalt für den Bericht erstellen,sowie die Tabelle mit den aktualisierten Daten ansonsten keine Daten verfügbar
        if not updated_table_data:
            print("No data available for HTML report.")
            return

        # HTML-Header und -Stil definieren
        html_content = f"""
        <html>
        <head>
            <title>Image Comparison Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; color: #333; font-size: 10px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 10px; border: 1px solid #ddd; text-align: center; }}
                th {{ background-color: #4CAF50; color: white; }}
                img {{ border-radius: 15px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); }}
                small {{ display: block; margin-top: 5px; font-size: 10px; color: #555; }}  /* Style for image captions */
                p {{ margin-top: 5px; font-size: 10px; color: #555; }}
                h1 {{ font-size: 20px; }}  /* Set font size for the heading */
            </style>
        </head>
        <body>
            <h1>Image Comparison Report</h1>
            <table>
                {tabulate(updated_table_data, headers=headers, tablefmt="unsafehtml")}
            </table>
        </body>
        </html>
        """

        # HTML-Datei schreiben
        with open(self.output_file, 'w') as f:
            f.write(html_content)

        print(f"HTML report generated: {self.output_file}")

    # Funktion zum Generieren eines CSV-Berichts
    def generate_csv_report(self, all_differences):
        # Filter für ähnliche Bilder anwenden, wenn -s verwendet wird
        filtered_differences = self.filter_similar_images(all_differences)

        headers, table_data = self.generate_table_data(filtered_differences)

        # Schreiben der CSV-Datei
        with open(self.output_file, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(headers)  
            csv_writer.writerows(table_data)

        print(f"CSV report generated: {self.output_file}")

    # Funktion zum Generieren eines JSON-Berichts
    def generate_json_report(self, all_differences):
        """Generate a JSON report."""
        # Filter für ähnliche Bilder anwenden, wenn -s verwendet wird
        filtered_differences = self.filter_similar_images(all_differences)

        headers, table_data = self.generate_table_data(filtered_differences)
        json_data = [dict(zip(headers, row)) for row in table_data] 

        # Schreiben der JSON-Datei
        with open(self.output_file, 'w') as jsonfile:
            json.dump(json_data, jsonfile, indent=4)

        print(f"JSON report generated: {self.output_file}")

    # Funktion zum Ausgeben von Statistiken über die Vergleiche
    def print_stats(self, total_comparison_time, num_comparisons):
        """Print statistics about the comparisons."""
        if num_comparisons > 0:
            avg_time = total_comparison_time / num_comparisons
            print(f"\n--- Statistics ---")
            print(f"Total time for comparing all images: {total_comparison_time:.4f} seconds")
            print(f"Average time per comparison: {avg_time:.4f} seconds")
            print(f"Total number of comparisons: {num_comparisons}")
        else:
            print("\nNo comparisons made.")

    # Funktion zum Verarbeiten der Eingaben und Ausführen der Bildvergleiche
    def process(self):
        total_comparison_time = 0.0 # Gesamtvergleichszeit für alle Bilder Startwert
        num_comparisons = 0         # Anzahl der Vergleiche Startwert

        # Überprüfen, ob die Eingabe ein Verzeichnis oder zwei spezifische Bilddateien sind
        if len(self.input_paths) == 1:
 
            # Verzeichnismodus
            directory = self.input_paths[0]
            if not os.path.isdir(directory):
                print(f"The directory '{directory}' does not exist.")
                return

            # Liste der Bilddateien im Verzeichnis erstellen
            image_list = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and self.is_supported_image(f)]

            # Fehlermeldung, wenn keine unterstützten Bilddateien gefunden wurden
            if not image_list:
                print(f"No supported image files found in directory '{directory}'.")
                return

            all_differences = self.compare_multiple_images(image_list) # Vergleich mehrerer Bilder durchführen

            # Gesamtvergleichszeit und Anzahl der Vergleiche berechnen
            total_comparison_time = sum(diff['comparison_time'] for diff in all_differences)
            num_comparisons = len(all_differences)

            # Unterschiede in der Konsole ausgeben
            self.print_differences(all_differences)

            # Bericht generieren basierend auf dem ausgewählten Ausgabeformat
            if self.output_file and self.output_format == 'html':
                self.generate_html_report(all_differences)
            elif self.output_file and self.output_format == 'csv':
                self.generate_csv_report(all_differences)
            elif self.output_file and self.output_format == 'json':
                self.generate_json_report(all_differences)

        # Zwei-Bild-Modus
        elif len(self.input_paths) == 2:

            image1, image2 = self.input_paths

            # Fehlermeldung, wenn eine oder beide der angegebenen Dateien keine unterstützten Bilddateien sind
            if not (self.is_supported_image(image1) and self.is_supported_image(image2)):
                print(f"One or both of the specified files are not supported image files.")
                return

            # Bildvergleich durchführen
            image1, image2, difference_percent, is_within_percent, comparison_time = self.compare_images(image1, image2)

            # Unterschiede in der Konsole ausgeben und Bericht generieren basierend auf dem ausgewählten Ausgabeformat
            if is_within_percent:
                output = f"'{image1}' and '{image2}' are within the specified deviation (Difference: {difference_percent:.2f}%)"
                if self.show_time:
                    output += f", Comparison time: {comparison_time:.4f} seconds"
                print(output)

        
                total_comparison_time = comparison_time
                num_comparisons = 1
                
                # Bericht generieren basierend auf dem ausgewählten Ausgabeformat
                if self.output_file and self.output_format == 'html':
                    self.generate_html_report([{
                        "image1": image1,
                        "image2": image2,
                        "difference": difference_percent,
                        "comparison_time": comparison_time,
                    }])
                elif self.output_file and self.output_format == 'csv':
                    self.generate_csv_report([{
                        "image1": image1,
                        "image2": image2,
                        "difference": difference_percent,
                        "comparison_time": comparison_time,
                    }])
                elif self.output_file and self.output_format == 'json':
                    self.generate_json_report([{
                        "image1": image1,
                        "image2": image2,
                        "difference": difference_percent,
                        "comparison_time": comparison_time,
                    }])

        # Ausgabe der Statistiken, wenn --stats verwendet wird
        if self.show_stats:
            self.print_stats(total_comparison_time, num_comparisons)

# Hauptfunktion zum Ausführen des Skripts
def main():
    # Parameter und Argumente verarbeiten
    parser = argparse.ArgumentParser(description="Compare images in a directory or two specific image files using hashes.")
    parser.add_argument('-i', '--input', type=str, nargs='+', required=True, help='Path to a directory or to two image files')
    parser.add_argument('-p', '--percent', type=int, default=100, help='Percentage of maximum deviation that is considered identical (e.g., -p 80 means 20%% deviation allowed)')
    parser.add_argument('-s', '--similar', action='store_true', help='Only print images with up to 5%% difference')
    parser.add_argument('-o', '--output', type=str, nargs=2, help='Output format and file, e.g., "-o html output.html" or "-o csv output.csv" or "-o json output.json"')
    parser.add_argument('-T', '--time', action='store_true', help='Display comparison time for each image pair')
    parser.add_argument('-t', '--table', action='store_true', help='Display comparison results as a text table')
    parser.add_argument('-N', '--id', action='store_true', help='Add an ID column with a running number')
    parser.add_argument('-H', '--hash', type=str, help='Display hash for the specified algorithm (e.g., sha256, md5, etc.)')
    parser.add_argument('-P', '--pixel-size', action='store_true', help='Display image dimensions in pixels (width x height) in the table')
    parser.add_argument('-F', '--file-size', action='store_true', help='Display file size of images in the table')
    parser.add_argument('-S', '--stats', action='store_true', help='Display statistics: total time, average time per comparison, and number of comparisons')
    args = parser.parse_args()

    # Überprüfen, ob der angegebene Hash-Algorithmus verfügbar ist, wenn --hash verwendet wird
    if args.hash and args.hash not in hashlib.algorithms_available:
        print(f"Error: The specified hash algorithm '{args.hash}' is not available in hashlib.")
        return

    # Überprüfen, ob der angegebene Ausgabeformat unterstützt wird
    output_format = None
    output_file = None
    if args.output:
        output_format, output_file = args.output
        if output_format not in ['html', 'csv', 'json']:
            print(f"Error: Unsupported output format '{output_format}'. Supported formats are 'html', 'csv', and 'json'.")
            return

    # ImageComparator-Objekt erstellen und den Vergleichsprozess starten
    comparator = ImageComparator(
        input_paths=args.input,             # Pfade zu den Eingabebildern
        percent=args.percent,               # Prozentsatz der maximalen Abweichung
        similar=args.similar,               # Filtert ähnliche Bilder (5% oder weniger Unterschied)
        output_file=output_file,            # Dateipfad für die Ausgabe
        output_format=output_format,        # Ausgabeformat (csv, html, json)
        show_time=args.time,                # Steuert die Ausgabe der Vergleichszeit
        show_table=args.table,              # Steuert die Ausgabe der Ergebnisse als Tabelle
        show_id=args.id,                    # Steuert die Ausgabe der ID-Spalte
        hash_algorithm=args.hash,           # Steuert die Ausgabe des Hash-Werts
        show_pixel_size=args.pixel_size,    # Steuert die Ausgabe der Pixelgröße
        show_file_size=args.file_size,      # Steuert die Ausgabe der Dateigröße
        show_stats=args.stats               # Steuert die Ausgabe der Statistiken
    )
    comparator.process()

if __name__ == "__main__":
    main()
