FROM python:3.11-slim

# Install Chrome + dependencies
RUN apt-get update && apt-get install -y wget gnupg unzip curl \
    && wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb 2>/dev/null || apt-get install -f -y \
    && rm -f google-chrome-stable_current_amd64.deb \
    && apt-get clean

# Install chromedriver manually (match Chrome version)
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1) \
    && echo "Chrome version: $CHROME_VERSION" \
    && curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_VERSION}" -o /tmp/chromedriver_version \
    && DRIVER_VERSION=$(cat /tmp/chromedriver_version) \
    && echo "Chromedriver version: $DRIVER_VERSION" \
    && wget -q "https://storage.googleapis.com/chrome-for-testing-public/${DRIVER_VERSION}/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip \
    && unzip -q /tmp/chromedriver.zip -d /tmp/ \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/bin/chromedriver \
    && chmod +x /usr/bin/chromedriver \
    && rm -rf /tmp/chromedriver.zip /tmp/chromedriver-linux64 /tmp/chromedriver_version

# Install Python dependencies
RUN pip install selenium==4.25.0 pytest==7.4.0 pytest-html==4.1.1

WORKDIR /tests
