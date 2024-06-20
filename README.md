# LocalWebMarket

LocalWebMarket to aplikacja webowa oparta na Flasku, która umożliwia użytkownikom rejestrację, logowanie oraz zarządzanie portfelem akcji. Użytkownicy mogą dodawać akcje do sprzedaży oraz kupować akcje od innych użytkowników. Aplikacja składa się z kilku kluczowych funkcjonalności:

## Opis aplikacji

1. **Rejestracja i logowanie użytkowników**
2. **Dodawanie akcji do sprzedaży**
3. **Zakup akcji**
4. **Zarządzanie portfelem**
5. **Bezpieczeństwo**

## Technologie

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS
- **Baza danych**: MongoDB Atlas

## Funkcjonalności

### Rejestracja i logowanie

- **Rejestracja użytkownika**: Użytkownicy mogą rejestrować się, podając imię, nazwisko, adres email oraz hasło.
- **Logowanie użytkownika**: Po pomyślnej rejestracji, użytkownicy mogą się zalogować, aby uzyskać dostęp do swojego konta.

### Dodawanie akcji do sprzedaży

- **Dodawanie akcji**: Zalogowani użytkownicy mogą dodawać nowe akcje do sprzedaży, określając nazwę, ilość i cenę akcji.

### Zakup akcji

- **Przeglądanie ofert**: Użytkownicy mogą przeglądać oferty akcji innych użytkowników.
- **Zakup akcji**: Użytkownicy mogą kupować akcje, określając ilość, którą chcą zakupić. Zakup jest możliwy tylko, jeśli użytkownik ma wystarczające saldo na koncie.

### Zarządzanie portfelem

- **Przegląd portfela**: Użytkownicy mogą przeglądać posiadane akcje oraz sprawdzać dostępne saldo.
- **Sprzedaż akcji**: Użytkownicy mogą sprzedawać posiadane akcje, określając ilość, którą chcą sprzedać.

### Bezpieczeństwo

- **Haszowanie haseł**: Hasła użytkowników są przechowywane w postaci haszowanej dla zapewnienia bezpieczeństwa.
- **Sesje użytkowników**: Sesje użytkowników są zabezpieczone za pomocą klucza sesji, aby chronić przed nieautoryzowanym dostępem.

## Struktura projektu

- `app.py`: Główny plik aplikacji Flask zawierający logikę rejestracji, logowania, zakupu i sprzedaży akcji.
- `templates/`: Katalog zawierający szablony HTML.
  - `index.html`: Strona główna z formularzami rejestracji i logowania.
  - `account.html`: Strona konta użytkownika z informacjami o jego portfelu akcji.
  - `market.html`: Strona rynku z listą dostępnych akcji.
  - `stock_info.html`: Strona z informacjami o wybranej akcji.
- `static/`: Katalog zawierający pliki statyczne, takie jak arkusze stylów CSS.
