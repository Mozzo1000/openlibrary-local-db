FROM python:3.12.4
WORKDIR /app

COPY README.md pyproject.toml ./
COPY api ./api

RUN pip install .

EXPOSE 5000
CMD ["gunicorn", "-b", ":5000", "api.app:app"]