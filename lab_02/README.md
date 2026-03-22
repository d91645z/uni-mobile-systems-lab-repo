# Lab 02 – Implementacja symulatora stacji bazowej

## Co zostało zrealizowane
Zaimplementowano symulator stacji bazowej w języku Python w klasie BaseStationSimulator.
Uruchomienie programu wywołuje okno gdzie użytkownik może rozpocząć symulację oraz zmienić jej parametry.
Uruchomienie symulacji pokazuje aktulizujące się w czasie rzeczywistym informacje dotyczące bazy wliczając liczbę obsłużonych, status kolejki, status kanałów i inne ważne dane.
Po przekroczeniu limitu czasu symulacji, symulacja się kończy, wyświetlając wykresy dotyczące zapełnienia kanałów, kolejki oraz zapisuje wynik symulacji do pliku o nazwie "wyniki_symulacji.txt".

## Uruchomienie
Plik lab2.py powinien zostać uruchomiony przez interpreter Pythona wraz z zainstalowanym dodatkowym pakietem matplotlib.

## Trudności / refleksja (opcjonalnie)
Zbyt mała intensywność powoduje brak powstawania kolejki.