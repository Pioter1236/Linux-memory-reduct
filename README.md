# Linux-memory-reduct
RAM ZRAM SWAP linux
# Zorin OS RAM Indicator (Mem Reduct style)

Lekki wskaźnik zużycia pamięci RAM przeznaczony dla systemów Zorin OS / GNOME, inspirowany aplikacją Mem Reduct. Wyświetla na pasku zadań samą czytelną liczbę procentową ze zmiennym kolorem oraz rozwijane menu ze szczegółami **RAM, ZRAM i SWAP**.

## Funkcje
- **Dynamiczna ikona:** Samodzielna liczba procentowa na pasku zadań (bez brzydkich ramek).
- **Progi kolorystyczne:**
  - `0% - 75%`: Zielony
  - `76% - 89%`: Żółty
  - `90% - 100%`: Czerwony
- **Menu po kliknięciu:** Pokazuje dokładne użycie **RAM**, **ZRAM** oraz wydzielonego **SWAP** (bez dublowania ZRAM w swapie).
- **Narzędzia:** Opcja czyszczenia pamięci podręcznej systemowej (*Drop Caches*).
- **Autostart:** Automatyczne uruchamianie po zalogowaniu do systemu.

## Instalacja jednym poleceniem

Sklonuj repozytorium, a następnie w folderze projektu uruchom skrypt instalacyjny:

```bash
chmod +x install.sh
./install.sh
