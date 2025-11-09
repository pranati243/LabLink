# LabLink AWS Deployment Guide

## Prerequisites ✅
- [x] AWS RDS Database created
- [x] EC2 instance created
- [x] .pem file downloaded

---

## Step 1: Prepare Your EC2 Instance

### 1.1 Set Permissions on Your .pem File

**Windows (PowerShell):**
```powershell
# Navigate to where your .pem file is
cd C:\path\to\your\pem\file

# Set proper permissions (Windows)
icacls "your-key.pem" /inheritance:r
icacls "your-key.pem" /grant:r "%USERNAME%:R"
```

**Mac/Linux:**
```bash
chmod 400 your-key.pem
```

### 1.2 Connect to Your EC2 Instance

```bash
# Replace with your actual values
ssh -i "your-key.pem" ec2-user@your-ec2-public-ip

# Example:
# ssh -i "lablink-key.pem" ec2-user@54.123.45.67
```

---

## Step 2: Install Docker on EC2

Once connected to your EC2 instance:

```bash
# Update system packages
sudo yum update -y

# Install Docker
sudo yum install docker -y

# Start Docker service
sudo service docker start

# Add ec2-user to docker group (so you don't need sudo)
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version

# Log out and back in for group changes to take effect
exit
```

**Reconnect to EC2:**
```bash
ssh -i "your-key.pem" ec2-user@your-ec2-public-ip
```

---

## Step 3: Transfer Your Application to EC2

### Option A: Using Git (Recommended)

**On your local machine:**
```bash
# If you haven't already, push your code to GitHub
git init
git add .
git commit -m "Ready for AWS deployment"
git branch -M main
git remote add origin https://github.com/yourusername/lablink.git
git push -u origin main
```

**On EC2:**
```bash
# Clone your repository
git clone https://github.com/yourusername/lablink.git
cd lablink
```

### Option B: Using SCP (Direct File Transfer)

**On your local machine (Windows PowerShell):**
```powershell
# Navigate to your project directory
cd C:\Users\Pranati\Documents\LabLink

# Create a zip file
Compress-Archive -Path * -DestinationPath lablink.zip

# Transfer to EC2
scp -i "your-key.pem" lablink.zip ec2-user@your-ec2-public-ip:~/
```

**On EC2:**
```bash
# Install unzip if needed
sudo yum install unzip -y

# Unzip the application
unzip lablink.zip -d lablink
cd lablink
```

---

## Step 4: Configure Environment Variables

**On EC2, create production .env file:**

```bash
# Create .env file
  nano .env
```

**Add the following (replace with your actual values):**

```env
# Database Configuration (Your RDS Database)
DATABASE_URL=postgresql://your_db_user:your_db_password@your-rds-endpoint:5432/lablink

# JWT Configuration (Generate secure keys!)
JWT_SECRET_KEY=your-super-secure-jwt-secret-key-change-this
SECRET_KEY=your-super-secure-secret-key-change-this

# Flask Configuration
FLASK_ENV=production
FLASK_APP=run.py

# CORS Configuration (Your EC2 public IP or domain)
CORS_ORIGINS=http://your-ec2-public-ip,https://your-domain.com

# Optional: AWS S3 for image storage
# AWS_S3_BUCKET=lablink-images
# AWS_REGION=us-east-1
```

**Save and exit:** Press `Ctrl+X`, then `Y`, then `Enter`

**Important:** Generate secure secret keys:
```bash
# Generate random secret keys
python3 -c "import secrets; print(secrets.token_hex(32))"
# Use output for JWT_SECRET_KEY

python3 -c "import secrets; print(secrets.token_hex(32))"
# Use output for SECRET_KEY
```

---

## Step 5: Update Docker Compose for Production

**Edit docker-compose.yml:**
```bash
nano docker-compose.yml
```

**Make sure it looks like this (remove the db service since you're using RDS):**

```yaml
version: '3.8'

services:
  # Flask Backend Service
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: lablink-backend
    restart: unless-stopped
    environment:
      FLASK_ENV: ${FLASK_ENV:-production}
      DATABASE_URL: ${DATABASE_URL}
      SECRET_KEY: ${SECRET_KEY}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      CORS_ORIGINS: ${CORS_ORIGINS}
    ports:
      - "5000:5000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

---

## Step 6: Initialize the Database

**On EC2:**

```bash
# Set environment variables temporarily
export DATABASE_URL="postgresql://your_db_user:your_db_password@your-rds-endpoint:5432/lablink"

# Install Python and dependencies (if not using Docker for this step)
sudo yum install python3 python3-pip -y
pip3 install psycopg2-binary python-dotenv

# Initialize database
python3 backend/init_db.py init

# Seed initial data
python3 backend/seed_data.py
```

---

## Step 7: Start the Application

```bash
# Build and start the Docker containers
docker-compose build
docker-compose up -d

# Check if containers are running
docker ps

# View logs
docker-compose logs -f backend
```

**Press `Ctrl+C` to exit logs**

---

## Step 8: Configure EC2 Security Group

**In AWS Console:**

1. Go to **EC2 Dashboard** → **Security Groups**
2. Select your EC2 instance's security group
3. Click **Edit inbound rules**
4. Add these rules:

| Type | Protocol | Port Range | Source | Description |
|------|----------|------------|--------|-------------|
| HTTP | TCP | 80 | 0.0.0.0/0 | HTTP access |
| HTTPS | TCP | 443 | 0.0.0.0/0 | HTTPS access |
| Custom TCP | TCP | 5000 | 0.0.0.0/0 | Backend API |
| SSH | TCP | 22 | Your IP | SSH access |

5. Click **Save rules**

---

## Step 9: Update Frontend Configuration

**On your local machine, update frontend/config.js:**

```javascript
// Frontend configuration
// Change this to your EC2 public IP or domain
window.APP_CONFIG = {
    API_BASE_URL: 'http://your-ec2-public-ip:5000/api'
    // Or if you have a domain:
    // API_BASE_URL: 'https://api.yourdomain.com/api'
};
```

**Upload the updated frontend to EC2:**

```bash
# On your local machine
scp -i "your-key.pem" frontend/config.js ec2-user@your-ec2-public-ip:~/lablink/frontend/
```

---

## Step 10: Serve the Frontend

### Option A: Using Nginx (Recommended for Production)

**On EC2:**

```bash
# Install Nginx
sudo yum install nginx -y

# Copy frontend files to Nginx directory
sudo cp -r frontend/* /usr/share/nginx/html/

# Start Nginx
sudo service nginx start

# Enable Nginx to start on boot
sudo chkconfig nginx on
```

### Option B: Using Python HTTP Server (Quick Test)

```bash
# Navigate to frontend directory
cd ~/lablink/frontend

# Start simple HTTP server
python3 -m http.server 8000 &
```

---

## Step 11: Access Your Application

**Open your browser and go to:**

- **Frontend:** `http://your-ec2-public-ip` (if using Nginx)
- **Or:** `http://your-ec2-public-ip:8000` (if using Python server)
- **Backend API:** `http://your-ec2-public-ip:5000`
- **Health Check:** `http://your-ec2-public-ip:5000/health`

**Login with:**
- Username: `student` or `faculty`
- Password: `student123` or `faculty123`

---

## Step 12: Set Up Domain (Optional but Recommended)

### 12.1 Point Domain to EC2

1. Go to your domain registrar (GoDaddy, Namecheap, etc.)
2. Add an **A Record**:
   - Name: `@` (or `lablink`)
   - Value: Your EC2 Public IP
   - TTL: 3600

### 12.2 Set Up SSL with Let's Encrypt

**On EC2:**

```bash
# Install Certbot
sudo yum install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow the prompts
# Certbot will automatically configure Nginx for HTTPS
```

### 12.3 Update Frontend Config for HTTPS

```javascript
window.APP_CONFIG = {
    API_BASE_URL: 'https://yourdomain.com/api'
};
```

---

## Troubleshooting

### Check Backend Logs
```bash
docker-compose logs -f backend
```

### Check if Backend is Running
```bash
curl http://localhost:5000/health
```

### Restart Services
```bash
docker-compose restart
```

### Check Database Connection
```bash
docker-compose exec backend python3 -c "from backend.models import db; from backend.app import create_app; app = create_app(); app.app_context().push(); db.session.execute('SELECT 1'); print('Database connected!')"
```

### View All Running Containers
```bash
docker ps -a
```

---

## Maintenance Commands

### Update Application
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### Backup Database
```bash
# From your local machine
pg_dump -h your-rds-endpoint -U your_db_user -d lablink > backup.sql
```

### View Application Logs
```bash
docker-compose logs -f
```

### Stop Application
```bash
docker-compose down
```

### Start Application
```bash
docker-compose up -d
```

---

## Security Checklist

- [ ] Changed default passwords in seed_data.py
- [ ] Generated secure JWT_SECRET_KEY and SECRET_KEY
- [ ] Configured EC2 Security Group properly
- [ ] Set up SSL/HTTPS with Let's Encrypt
- [ ] Restricted SSH access to your IP only
- [ ] Set up RDS security group to only allow EC2 access
- [ ] Enabled CloudWatch monitoring
- [ ] Set up automated backups for RDS
- [ ] Configured log rotation

---

## Next Steps

1. **Set up monitoring** with AWS CloudWatch
2. **Configure auto-scaling** if needed
3. **Set up CI/CD** with GitHub Actions
4. **Add S3 for image storage** (see AWS_S3_INTEGRATION.md)
5. **Set up CloudFront CDN** for better performance
6. **Configure automated backups**

---

## Support

For detailed AWS-specific configurations, see:
- `DEPLOYMENT_AWS.md` - Comprehensive AWS deployment guide
- `AWS_QUICKSTART.md` - Quick AWS setup
- `AWS_S3_INTEGRATION.md` - S3 image storage setup

**Your LabLink system is now deployed on AWS!** 🚀
