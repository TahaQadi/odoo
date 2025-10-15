# Odoo 19.0 ERP System

## Overview
This is a fully configured Odoo 19.0 ERP (Enterprise Resource Planning) system running on Replit. Odoo is a comprehensive suite of business applications including CRM, sales, inventory, accounting, HR, and more.

## Current Status
- ✅ Odoo 19.0 installed and configured
- ✅ PostgreSQL database connected (Replit's built-in Neon database)
- ✅ Web server running on port 5000
- ✅ Proxy mode enabled for Replit environment
- ⏳ Database needs to be initialized through web UI on first use

## Recent Changes
- **2025-10-15**: Initial Odoo 19.0 setup completed
  - Installed all Python dependencies using psycopg2-binary for compatibility
  - Configured Odoo to work with Replit's proxy environment
  - Set up workflow to run Odoo server on port 5000
  - Configured deployment settings for production use

## Getting Started

### First Time Setup
1. The Odoo server is already running - check the webview panel
2. You'll see the Odoo database manager/selector page
3. Create a new database through the web interface:
   - Click "Create Database"
   - Enter a database name (e.g., "odoo")
   - Set a master password (save this securely!)
   - Choose language and country
   - Load demo data (optional - choose "No" for faster setup)
4. Wait for initialization to complete (2-5 minutes)
5. Once initialized, you'll be redirected to the Odoo login page

### Accessing Odoo
- **Development URL**: Check the webview panel or Replit's preview URL
- **Admin Login**: Use the credentials you set during database creation

## Project Architecture

### Configuration Files
- `odoo.conf` - Main Odoo configuration file
  - Database connection: Uses Replit environment variables (PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE)
  - Port: 5000 with proxy mode enabled
  - Admin password: admin123 (change this in production!)
  
- `requirements.txt` - Python dependencies
  - Using psycopg2-binary instead of psycopg2 for Replit compatibility

### Key Directories
- `/odoo` - Core Odoo framework
- `/addons` - Odoo applications and modules
- `odoo-bin` - Main Odoo executable

### Database
- **Type**: PostgreSQL (Replit's built-in Neon database)
- **Connection**: Via environment variables (DATABASE_URL, PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE)
- **SSL Mode**: Required (Odoo reads from environment variables automatically)
- **Note**: Database credentials are managed by Replit and never stored in configuration files

## Important Notes

### Performance Considerations
- Database initialization can take 2-5 minutes due to network latency
- The first load after initialization may be slow
- Subsequent page loads should be faster

### Known Issues
- Database initialization via command line is very slow due to network latency to remote database
- **Solution**: Use the web UI for database creation and initialization (recommended)

### Configuration Details
- **Proxy Mode**: Enabled (required for Replit)
- **Host Interface**: 0.0.0.0 (binds to all interfaces)
- **Port**: 5000 (Replit's standard web port)
- **Workers**: 0 (threading mode for development)
- **Database Listing**: Enabled

## Deployment

The project is configured for deployment with:
- **Target**: VM (always-running for stateful connections)
- **Command**: `python3 ./odoo-bin -c odoo.conf`

To publish your Odoo instance:
1. Click the "Publish" button in Replit
2. Your Odoo instance will be available at a permanent URL
3. Configure custom domain if needed (through Replit settings)

## Troubleshooting

### Odoo Won't Start
1. Check the workflow logs in Replit
2. Verify database connection (environment variables should be set)
3. Restart the workflow if needed

### Database Issues
1. If initialization fails, drop the database and recreate through web UI
2. Check that DATABASE_URL environment variable is set
3. Ensure SSL mode is enabled in config

### Slow Performance
1. Database operations may be slower due to remote database
2. Consider implementing caching if needed
3. Check Replit's resource usage

## User Preferences
- Use Replit's built-in PostgreSQL database
- Prefer web UI for database management over command line
- Keep deployment simple with VM target for state persistence

## Resources
- [Odoo Official Documentation](https://www.odoo.com/documentation/19.0/)
- [Odoo Developer Documentation](https://www.odoo.com/documentation/19.0/developer.html)
- [Replit PostgreSQL Docs](https://docs.replit.com/)
