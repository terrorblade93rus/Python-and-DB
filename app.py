from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import joinedload
from models import Publisher, Book, Shop, Stock, Sale
import os

# Подключение к PostgreSQL
DB_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/mydatabase')

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Получаем имя или id издателя
publisher_input = input("Введите имя или идентификатор издателя: ")

# Проверяем, ввел ли пользователь id или имя
if publisher_input.isdigit():
    publisher_query = session.query(Publisher).filter(Publisher.id == int(publisher_input))
else:
    publisher_query = session.query(Publisher).filter(Publisher.name.ilike(f"%{publisher_input}%"))

# Получаем издателя (проверка на существование)
publisher = publisher_query.first()
if not publisher:
    print("Издатель не найден.")
    exit()

# Запрос для получения данных о продаже книг этого издателя
results = (
    session.query(Book.title, Shop.name, Sale.price, Sale.date_sale)
    .join(Stock, Book.id == Stock.id_book)
    .join(Sale, Stock.id == Sale.id_stock)
    .join(Shop, Stock.id_shop == Shop.id)
    .filter(Book.id_publisher == publisher.id)
    .options(joinedload(Book.publisher))
    .all()
)

# Вывод результатов построчно
if results:
    print(f"Факты покупки книг издателя {publisher.name}:\n")
    for book_title, shop_name, price, date_sale in results:
        print(f"Название книги: {book_title} | Магазин: {shop_name} | Цена: {price} | Дата продажи: {date_sale}")
else:
    print(f"Нет данных о продажах книг издателя {publisher.name}.")