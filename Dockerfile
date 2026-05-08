FROM python:3.11-slim

RUN apt-get update && apt-get install -y wget gnupg unzip \
    && wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb 2>/dev/null || apt-get install -f -y \
    && rm -f google-chrome-stable_current_amd64.deb \
    && apt-get clean

RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1) \
    && wget -q https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION} -O /tmp/chromedriver_version.txt \
    && DRIVER_VERSION=$(cat /tmp/chromedriver_version.txt) \
    && wget -q https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip -O /tmp/chromedriver.zip \
    && unzip -q /tmp/chromedriver.zip -d /usr/bin/ \
    && chmod +x /usr/bin/chromedriver \
    && rm -f /tmp/chromedriver.zip /tmp/chromedriver_version.txt

RUN pip install selenium==4.25.0 pytest==7.4.0 pytest-html==4.1.1

WORKDIR /tests
