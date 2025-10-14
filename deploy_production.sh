#!/bin/bash

# ChemFactory MES/ERP Production Deployment Script
# Version: 2.0.0
# Date: 2025-10-14

set -e  # Exit on any error

echo "🚀 ChemFactory MES/ERP Production Deployment"
echo "=============================================="
echo "⏰ Started at: $(date)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root. Consider using a non-root user for production."
fi

# Step 1: System Requirements Check
print_info "Checking system requirements..."

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status "Python $PYTHON_VERSION found"
else
    print_error "Python 3 not found. Please install Python 3.11+"
    exit 1
fi

# Check Node.js version
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_status "Node.js $NODE_VERSION found"
else
    print_error "Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Check PostgreSQL
if command -v psql &> /dev/null; then
    print_status "PostgreSQL found"
else
    print_error "PostgreSQL not found. Please install PostgreSQL 13+"
    exit 1
fi

# Check Redis
if command -v redis-cli &> /dev/null; then
    print_status "Redis found"
else
    print_warning "Redis not found. Caching will be disabled."
fi

# Step 2: Create Production Directories
print_info "Creating production directories..."

sudo mkdir -p /var/www/chemfactory/{backend,frontend,uploads,logs,models}
sudo mkdir -p /var/backups/chemfactory
sudo mkdir -p /etc/chemfactory
sudo mkdir -p /var/log/chemfactory

print_status "Production directories created"

# Step 3: Set up Python Virtual Environment
print_info "Setting up Python virtual environment..."

cd /var/www/chemfactory/backend
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r /workspace/chemfactory/backend/requirements.txt
pip install gunicorn uvicorn[standard] psycopg2-binary redis

print_status "Python environment configured"

# Step 4: Set up Node.js Environment
print_info "Setting up Node.js environment..."

cd /var/www/chemfactory/frontend
cp -r /workspace/chemfactory/frontend/* .

# Install Node.js dependencies
npm install --production
npm install -g pm2

print_status "Node.js environment configured"

# Step 5: Database Setup
print_info "Setting up production database..."

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE chemfactory_prod;
CREATE USER chemfactory_user WITH PASSWORD 'secure_password_2025';
GRANT ALL PRIVILEGES ON DATABASE chemfactory_prod TO chemfactory_user;
\q
EOF

# Run database migrations
cd /var/www/chemfactory/backend
source venv/bin/activate
export DATABASE_URL="postgresql://chemfactory_user:secure_password_2025@localhost:5432/chemfactory_prod"
alembic upgrade head

print_status "Database configured and migrated"

# Step 6: Copy Application Files
print_info "Copying application files..."

# Copy backend files
cp -r /workspace/chemfactory/backend/* /var/www/chemfactory/backend/
cp /workspace/chemfactory/.env.production /var/www/chemfactory/backend/.env

# Copy frontend files
cp -r /workspace/chemfactory/frontend/* /var/www/chemfactory/frontend/

# Copy mobile app files
cp -r /workspace/chemfactory/mobile-app /var/www/chemfactory/

print_status "Application files copied"

# Step 7: Set up System Services
print_info "Setting up system services..."

# Create systemd service for backend
sudo tee /etc/systemd/system/chemfactory-backend.service > /dev/null << EOF
[Unit]
Description=ChemFactory MES/ERP Backend API
After=network.target postgresql.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/chemfactory/backend
Environment=PATH=/var/www/chemfactory/backend/venv/bin
ExecStart=/var/www/chemfactory/backend/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create systemd service for frontend
sudo tee /etc/systemd/system/chemfactory-frontend.service > /dev/null << EOF
[Unit]
Description=ChemFactory MES/ERP Frontend
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/chemfactory/frontend
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create nginx configuration
sudo tee /etc/nginx/sites-available/chemfactory > /dev/null << EOF
server {
    listen 80;
    server_name chemfactory.com www.chemfactory.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/chemfactory /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

print_status "System services configured"

# Step 8: Set Permissions
print_info "Setting file permissions..."

sudo chown -R www-data:www-data /var/www/chemfactory
sudo chmod -R 755 /var/www/chemfactory
sudo chmod -R 777 /var/www/chemfactory/uploads
sudo chmod -R 777 /var/www/chemfactory/logs

print_status "File permissions set"

# Step 9: Start Services
print_info "Starting services..."

sudo systemctl daemon-reload
sudo systemctl enable chemfactory-backend
sudo systemctl enable chemfactory-frontend
sudo systemctl start chemfactory-backend
sudo systemctl start chemfactory-frontend

print_status "Services started"

# Step 10: Health Check
print_info "Performing health check..."

sleep 10

# Check backend health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "Backend API is healthy"
else
    print_error "Backend API health check failed"
    exit 1
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    print_status "Frontend is healthy"
else
    print_error "Frontend health check failed"
    exit 1
fi

# Step 11: Seed Production Data
print_info "Seeding production data..."

cd /var/www/chemfactory/backend
source venv/bin/activate
export DATABASE_URL="postgresql://chemfactory_user:secure_password_2025@localhost:5432/chemfactory_prod"
python -c "
from app.utils.seed_data import seed_database
from app.db.database import SessionLocal
db = SessionLocal()
try:
    seed_database(db)
    print('Production data seeded successfully')
finally:
    db.close()
"

print_status "Production data seeded"

# Step 12: Set up Monitoring
print_info "Setting up monitoring..."

# Create monitoring script
sudo tee /usr/local/bin/chemfactory-monitor > /dev/null << 'EOF'
#!/bin/bash
# ChemFactory Monitoring Script

BACKEND_URL="http://localhost:8000/health"
FRONTEND_URL="http://localhost:3000"

# Check backend
if curl -f $BACKEND_URL > /dev/null 2>&1; then
    echo "$(date): Backend OK" >> /var/log/chemfactory/health.log
else
    echo "$(date): Backend FAILED" >> /var/log/chemfactory/health.log
    systemctl restart chemfactory-backend
fi

# Check frontend
if curl -f $FRONTEND_URL > /dev/null 2>&1; then
    echo "$(date): Frontend OK" >> /var/log/chemfactory/health.log
else
    echo "$(date): Frontend FAILED" >> /var/log/chemfactory/health.log
    systemctl restart chemfactory-frontend
fi
EOF

sudo chmod +x /usr/local/bin/chemfactory-monitor

# Add to crontab for monitoring
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/chemfactory-monitor") | crontab -

print_status "Monitoring configured"

# Step 13: Create Backup Script
print_info "Setting up backup system..."

sudo tee /usr/local/bin/chemfactory-backup > /dev/null << 'EOF'
#!/bin/bash
# ChemFactory Backup Script

BACKUP_DIR="/var/backups/chemfactory"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="chemfactory_backup_$DATE.sql"

# Create database backup
pg_dump -h localhost -U chemfactory_user -d chemfactory_prod > $BACKUP_DIR/$BACKUP_FILE

# Compress backup
gzip $BACKUP_DIR/$BACKUP_FILE

# Remove old backups (keep last 30 days)
find $BACKUP_DIR -name "chemfactory_backup_*.sql.gz" -mtime +30 -delete

echo "$(date): Backup completed: $BACKUP_FILE.gz" >> /var/log/chemfactory/backup.log
EOF

sudo chmod +x /usr/local/bin/chemfactory-backup

# Add to crontab for daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/chemfactory-backup") | crontab -

print_status "Backup system configured"

# Final Status
echo ""
echo "🎉 ChemFactory MES/ERP Production Deployment Complete!"
echo "======================================================"
echo ""
print_status "Backend API: http://localhost:8000"
print_status "Frontend: http://localhost:3000"
print_status "API Documentation: http://localhost:8000/docs"
print_status "Admin Panel: http://localhost:3000/admin"
echo ""
print_info "Services Status:"
systemctl status chemfactory-backend --no-pager -l
echo ""
systemctl status chemfactory-frontend --no-pager -l
echo ""
print_info "Next Steps:"
echo "1. Configure SSL certificates"
echo "2. Set up domain name resolution"
echo "3. Configure firewall rules"
echo "4. Set up log rotation"
echo "5. Train users on the system"
echo ""
print_info "Monitoring:"
echo "- Health checks: /usr/local/bin/chemfactory-monitor"
echo "- Logs: /var/log/chemfactory/"
echo "- Backups: /var/backups/chemfactory/"
echo ""
print_status "Deployment completed successfully at $(date)"