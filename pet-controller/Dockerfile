FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Create non-root user
RUN groupadd -r petcontroller && useradd -r -g petcontroller petcontroller
RUN chown -R petcontroller:petcontroller /app
USER petcontroller

# Run the controller
CMD ["python", "-m", "src.controller"]