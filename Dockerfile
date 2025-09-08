FROM python:3.11
WORKDIR /usr/local/app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code to app folder
COPY app ./app
EXPOSE 8080

# Create non-root user
RUN useradd app
USER app

# Start application with uvicorn
CMD ["uvicorn", "app.core.main:app", "--host", "0.0.0.0", "--port", "8080"]