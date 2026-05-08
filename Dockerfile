FROM python:3.11-slim

# Install Chrome
RUN apt-get update && apt-get install -y wget gnupg unzip \
    && wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb 2>/dev/null || apt-get install -f -y \
    && rm -f google-chrome-stable_current_amd64.deb \
    && apt-get clean

# Install Python dependencies (webdriver-manager auto-downloads chromedriver)
RUN pip install selenium==4.25.0 pytest==7.4.0 pytest-html==4.1.1 webdriver-manager==4.0.1

WORKDIR /tests
