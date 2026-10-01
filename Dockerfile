# 1. Pull the official enterprise Python slim engine base image
FROM python:3.12-slim

# 2. Inject R runtime dependencies directly into the system layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    r-base \
    r-cran-jsonlite \
    && rm -rf /var/lib/apt/lists/*

# 3. Form a clean working directory execution boundary inside the container
WORKDIR /app

# 4. Resolve Python ecosystem dependency caches
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Bring in your R dependency parameters programmatically
RUN R -e "install.packages('dplyr', repos='https://r-project.org')"

# 6. Copy the remaining script infrastructure architectures
COPY pipeline.py analytics.R .

# 7. Establish the default container initialization launch path
CMD ["python", "pipeline.py"]
