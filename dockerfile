# Use a slim Python 3.10 base image
FROM python:3.10-slim

# Create and set the working directory
WORKDIR /app

# Copy requirements first and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of your code into the container
COPY . .

# Expose port 8080, which Cloud Run expects
EXPOSE 8080

# Use gunicorn to serve your "app" object from app.py
CMD ["gunicorn", "--bind", ":8080", "app:app"]
