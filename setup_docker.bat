@echo off
echo Setting up X Scraper Docker environment...

REM Create directories on drive E:
echo Creating directories on drive E:...
mkdir "E:\xscraper\mongodb"
mkdir "E:\xscraper\logs"
mkdir "E:\xscraper\auth"

REM Check if Docker is running
echo Checking Docker status...
docker info > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Build and start containers
echo Building and starting containers...
docker-compose build
if %errorlevel% neq 0 (
    echo Error: Failed to build containers!
    pause
    exit /b 1
)

docker-compose up -d
if %errorlevel% neq 0 (
    echo Error: Failed to start containers!
    pause
    exit /b 1
)

echo.
echo Setup completed successfully!
echo.
echo Data directories created at:
echo - E:\xscraper\mongodb
echo - E:\xscraper\logs
echo - E:\xscraper\auth
echo.
echo Containers are now running. To view logs, use:
echo docker-compose logs -f
echo.
echo To stop the service, use:
echo docker-compose down
echo.
pause