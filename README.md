# Automatyczne-wykrywanie-i-klasyfikacja-zdarze-dla-system-w-monitorowania-warunk-w-rodowiskowych

## VPN i połączenie do Datahub
Aby móc korzystać z danych rzeczywistych niezbędne jest połączenie z Platformą DataHub. 
W tym celu przed uruchomieniem należy połączyć się do VPN'a sieci FSLAB.

## Pozyskiwanie danych
data_manager.py odpowiada za pobieranie i uaktualnianie danych. Uruchomienie skryptu powoduje utworzenie katalogu 
oraz tworzy pliki nazwa_stacji.csv do których zapisywane są pobrane dane oraz każda ich aktualizacja.

## Data Flow

![schemat_magisterka drawio](https://github.com/user-attachments/assets/47232062-e11e-4aea-8998-df989bb5a0d1)


## Data Crawler
odpowiedzialny za pobieranie i przygotowanie danych do klasyfikacji

## Anomalies Simulator
Modyfikuje dane uzyskane z sieci pomiarowej i zwraca niezbędny do uczenia zestaw etykiet

## Testing Module
Przyjmuje na wejściu zdefiniowany rozmiar wejścia, zwracając wyniki uczenia i klasyfikacji dla wybranej konfiguracji
