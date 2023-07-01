FROM python
COPY . /app
WORKDIR /app
EXPOSE 5000
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "app.py"]