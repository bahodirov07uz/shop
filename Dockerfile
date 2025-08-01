# Rasmiy Python image
FROM python:3.10

# Ishchi katalog
WORKDIR /app

# Fayllarni konteynerga nusxalash
COPY . /app/

# Pipni yangilaymiz va talablarni o‘rnatamiz
RUN pip install --upgrade pip
COPY requirments.txt .
RUN pip install -r requirments.txt

# Port ochamiz
EXPOSE 8000

# Django serverni ishga tushiramiz
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
