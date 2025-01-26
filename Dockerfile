FROM python:3.12

# These are for configuring Python in a Docker environment.
# You can freely just copy and paste them
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    # pip:
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_ROOT_USER_ACTION=ignore

# Set the default directory the container's shell should be in when running
WORKDIR /code

# Copy our code to the working directory
COPY ./ /code/

# Install our project, then remove the source code. We only need the built version
RUN pip install --no-cache-dir --upgrade . &&\
        rm -rf pyproject.toml src

# Set the default port to 80, as that's the default HTTP port
ENV PORT=80

# Run our app by default
CMD ["python", "-m", "app"]
