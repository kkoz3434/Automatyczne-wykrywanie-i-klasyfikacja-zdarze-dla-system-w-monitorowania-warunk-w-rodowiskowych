# Automatyczne-wykrywanie-i-klasyfikacja-zdarze-dla-system-w-monitorowania-warunk-w-rodowiskowych

## VPN i połączenie do Datahub
Aby móc korzystać z danych rzeczywistych niezbędne jest połączenie z Platformą DataHub. 
W tym celu przed uruchomieniem należy połączyć się do VPN'a sieci FSLAB.

## Pozyskiwanie danych
data_manager.py odpowiada za pobieranie i uaktualnianie danych. Uruchomienie skryptu powoduje utworzenie katalogu 
oraz tworzy pliki nazwa_stacji.csv do których zapisywane są pobrane dane oraz każda ich aktualizacja.