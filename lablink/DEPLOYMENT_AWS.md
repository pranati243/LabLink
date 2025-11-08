# AWS Deployment Guide

This guide provides step-by-step instructions for deploying LabLink on Amazon Web Services (AWS) using EC2 and RDS.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     AWS Cloud                            │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  VPC (Virtual Private Cloud)                      │  │
│  │                                                    │  │
│  │  ┌─────────────────┐      ┌──────────────────┐  │  │
│  │  │  EC2 Instance   │      │  RDS PostgreSQL  │  │  │
│  │  │  (Application)  │─────▶│  (Database)      │  │  │
│  │  │  - Docker       │      │                  │  │  │
│  │  │  - Nginx        │      │  Port: 5432      │  │  │
│  │  │  Port: 80, 443  │      └──────────────────┘  │  │
│  │  └─────────────────┘                             │  │
│  │         │                                         │  │
│  │         │                                         │  │
│  └─────────┼─────────────────────────────────────────┘  │
│            │                                             │
│  ┌─────────▼─────────┐                                  │
│  │  S3 Bucket        │                                  │
│  │  (Optional)       │                                  │
│  │  Component Images │                                  │
│  └───────────────────┘                                  │
└─────────────────────────────────────────────────────────┘
              │
              │ HTTPS
              ▼
         Internet Users
```

## Prerequisites

- AWS Account with billing enabled
- AWS CLI installed and configured (optional but recommended)
- SSH key pair for EC2 access
- Domain name (optional, for SSL/HTTPS)
- Basic knowledge of Linux command line

## Cost Estimate

Using AWS Free Tier eligible resources:
- **EC2 t2.micro**: Free tier (750 hours/month for 12 months)
- **RDS db.t3.micro**: Free tier (750 hours/month for 12 months)
- **EBS Storage**: 30 GB free tier
- **Data Transfer**: 15 GB free tier

**After free tier**: ~$15-25/month for small deployment

## Part 1: AWS RDS PostgreSQL Setup

### Step 1: Create RDS Database Instance

1. **Login to AWS Console**
   - Go to [AWS Console](https://console.aws.amazon.com/)
   - Navigate to RDS service

2. **Create Database**
   - Click "Create database"
   - Choose "Standard create"
   - Engine type: **PostgreSQL**
   - Version: **PostgreSQL 14.x** (latest 14.x version)

3. **Templates**
   - Select **Free tier** (for testing/development)
   - Or **Production** for production use

4. **Settings**
   - DB instance identifier: `lablink-db`
   - Master username: `lablink_admin`
   - Master password: Create a strong password (save it securely!)
   - Confirm password

5. **Instance Configuration**
   - DB instance class: **db.t3.micro** (Free tier eligible)
   - Storage type: **General Purpose SSD (gp2)**
   - Allocated storage: **20 GB**
   - Disable storage autoscaling (for cost control)

6. **Connectivity**
   - Virtual Private Cloud (VPC): Default VPC
   - Subnet group: Default
   - Public access: **Yes** (for initial setup; restrict later)
   - VPC security group: Create new
     - Name: `lablink-rds-sg`
   - Availability Zone: No preference
   - Database port: **5432**

7. **Additional Configuration**
   - Initial database name: `lablink`
   - DB parameter group: default
   - Backup retention: 7 days (or as needed)
   - Disable encryption (for free tier) or enable for production
   - Disable Enhanced monitoring (to stay in free tier)

8. **Create Database**
   - Review settings
   - Click "Create database"
   - Wait 5-10 minutes for creation

### Step 2: Configure RDS Security Group

1. **Find Security Group**
   - Go to EC2 → Security Groups
   - Find `lablink-rds-sg` (or the one created with RDS)

2. **Edit Inbound Rules**
   - Click "Edit inbound rules"
   - Add rule:
     - Type: **PostgreSQL**
     - Protocol: **TCP**
     - Port: **5432**
     - Source: **Custom** → `0.0.0.0/0` (temporary, will restrict later)
     - Description: "PostgreSQL access"
   - Save rules

3. **Note RDS Endpoint**
   - Go back to RDS → Databases
   - Click on `lablink-db`
   - Copy the **Endpoint** (e.g., `lablink-db.xxxxx.us-east-1.rds.amazonaws.com`)
   - Save this for later use

### Step 3: Initialize RDS Database

From your local machine:

```bash
# Install PostgreSQL client if not already installed
# macOS:
brew install postgresql

# Linux:
sudo apt install postgresql-client

# Windows: Download from postgresql.org

# Connect to RDS
psql -h lablink-db.xxxxx.us-east-1.rds.amazonaws.com \
     -U lablink_admin \
     -d lablink \
     -p 5432

# Enter password when prompted

# Verify connection
\l
\q
```

## Part 2: AWS EC2 Instance Setup

### Step 1: Launch EC2 Instance

1. **Navigate to EC2**
   - AWS Console → EC2 → Instances
   - Click "Launch instances"

2. **Name and Tags**
   - Name: `lablink-server`

3. **Application and OS Images**
   - Quick Start: **Ubuntu**
   - Ubuntu Server 22.04 LTS (Free tier eligible)
   - Architecture: **64-bit (x86)**

4. **Instance Type**
   - Select **t2.micro** (Free tier eligible)
   - 1 vCPU, 1 GB RAM

5. **Key Pair**
   - Create new key pair or select existing
   - Key pair name: `lablink-key`
   - Key pair type: **RSA**
   - Private key format: **.pem** (for SSH)
   - Download and save securely

6. **Network Settings**
   - VPC: Default VPC
   - Subnet: No preference
   - Auto-assign public IP: **Enable**
   - Firewall (security groups): Create new
     - Security group name: `lablink-ec2-sg`
     - Description: "LabLink application server"
     - Inbound rules:
       - SSH (22) from My IP
       - HTTP (80) from Anywhere
       - HTTPS (443) from Anywhere
       - Custom TCP (5000) from Anywhere (for testing)

7. **Configure Storage**
   - Size: **20 GB** (Free tier: up to 30 GB)
   - Volume type: **gp2**

8. **Advanced Details** (optional)
   - Leave defaults

9. **Launch Instance**
   - Review and click "Launch instance"
   - Wait 2-3 minutes for instance to start

### Step 2: Connect to EC2 Instance

1. **Get Instance Details**
   - Go to EC2 → Instances
   - Select `lablink-server`
   - Copy **Public IPv4 address** (e.g., `54.123.45.67`)

2. **Set Key Permissions** (first time only)
   ```bash
   # macOS/Linux:
   chmod 400 lablink-key.pem
   
   # Windows: Use PuTTY or WSL
   ```

3. **Connect via SSH**
   ```bash
   ssh -i lablink-key.pem ubuntu@54.123.45.67
   
   # Accept fingerprint when prompted
   # You should see: ubuntu@ip-xxx-xxx-xxx-xxx:~$
   ```

### Step 3: Install Docker on EC2

```bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Install required packages
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add ubuntu user to docker group
sudo usermod -aG docker ubuntu

# Verify installation
docker --version
docker-compose --version

# Log out and back in for group changes to take effect
exit
ssh -i lablink-key.pem ubuntu@54.123.45.67
```

### Step 4: Deploy Application on EC2

```bash
# Install Git
sudo apt install -y git

# Clone repository
git clone <your-repository-url>
cd lablink

# Or upload files via SCP from local machine:
# scp -i lablink-key.pem -r /path/to/lablink ubuntu@54.123.45.67:~/

# Create production environment file
nano .env
```

Add the following to `.env`:
```bash
# Database Configuration
DATABASE_URL=postgresql://lablink_admin:YOUR_RDS_PASSWORD@lablink-db.xxxxx.us-east-1.rds.amazonaws.com:5432/lablink

# Security
JWT_SECRET_KEY=GENERATE_STRONG_RANDOM_KEY_HERE
SECRET_KEY=GENERATE_ANOTHER_STRONG_KEY_HERE

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# CORS Configuration
CORS_ORIGINS=http://54.123.45.67,https://yourdomain.com

# JWT Configuration
JWT_ACCESS_TOKEN_EXPIRES=1

# Optional: AWS S3 for images
# AWS_S3_BUCKET=lablink-images
# AWS_ACCESS_KEY_ID=your_access_key
# AWS_SECRET_ACCESS_KEY=your_secret_key
# AWS_REGION=us-east-1
```

**Generate secure keys:**
```bash
# Generate JWT secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate Flask secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Save and exit (Ctrl+X, Y, Enter)

```bash
# Initialize database on RDS
cd backend

# Install psycopg2 for database connection
pip3 install psycopg2-binary

# Initialize database
python3 init_db.py init

# Load seed data
python3 seed_data.py

# Return to project root
cd ..

# Build and start Docker containers
docker-compose up -d --build

# Verify containers are running
docker-compose ps

# Check logs
docker-compose logs -f backend
```

### Step 5: Configure Security Group for EC2-RDS Communication

1. **Update RDS Security Group**
   - Go to EC2 → Security Groups
   - Select `lablink-rds-sg`
   - Edit inbound rules
   - Modify PostgreSQL rule:
     - Source: **Custom** → Select `lablink-ec2-sg` (EC2 security group)
     - This restricts database access to only the EC2 instance
   - Remove the `0.0.0.0/0` rule (if you added it earlier)
   - Save rules

2. **Verify Connection**
   ```bash
   # From EC2 instance
   docker-compose exec backend python -c "from app import db; print('Database connected!' if db.engine.connect() else 'Connection failed')"
   ```

### Step 6: Access the Application

1. **Via Public IP**
   - Open browser: `http://54.123.45.67:5000`
   - Or access frontend: Upload frontend files to EC2 and serve via Nginx

2. **Test API**
   ```bash
   curl http://54.123.45.67:5000/health
   ```

## Part 3: Configure Nginx Reverse Proxy (Recommended)

### Install and Configure Nginx

```bash
# Install Nginx
sudo apt install -y nginx

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/lablink
```

Add configuration:
```nginx
server {
    listen 80;
    server_name 54.123.45.67;  # Replace with your domain if you have one

    # Frontend files
    root /home/ubuntu/lablink/frontend;
    index login.html;

    # Serve frontend files
    location / {
        try_files $uri $uri/ =404;
    }

    # Proxy API requests to Flask backend
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:5000/health;
    }
}
```

Save and exit.

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/lablink /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

# Enable Nginx to start on boot
sudo systemctl enable nginx
```

Now access the application at: `http://54.123.45.67`

## Part 4: Configure Domain and SSL (Optional)

### Step 1: Configure Domain

1. **Point Domain to EC2**
   - Go to your domain registrar (GoDaddy, Namecheap, etc.)
   - Add A record:
     - Name: `@` (or `lablink`)
     - Type: `A`
     - Value: `54.123.45.67` (your EC2 public IP)
     - TTL: 3600

2. **Wait for DNS Propagation** (5-30 minutes)
   ```bash
   # Check DNS
   nslookup yourdomain.com
   ```

### Step 2: Install SSL Certificate with Let's Encrypt

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com

# Follow prompts:
# - Enter email address
# - Agree to terms
# - Choose to redirect HTTP to HTTPS (recommended)

# Verify auto-renewal
sudo certbot renew --dry-run

# Certificate will auto-renew every 90 days
```

### Step 3: Update Application Configuration

```bash
# Update .env file
nano .env

# Update CORS_ORIGINS
CORS_ORIGINS=https://yourdomain.com

# Restart application
docker-compose restart backend
```

Now access via: `https://yourdomain.com`

## Part 5: Optional S3 Integration for Component Images

> **📘 For detailed S3 integration instructions, see [AWS_S3_INTEGRATION.md](AWS_S3_INTEGRATION.md)**
> 
> The guide below provides a quick overview. For comprehensive instructions including:
> - Detailed IAM policy configuration
> - Code examples for S3 upload/delete
> - Frontend integration
> - Troubleshooting common issues
> - Cost optimization strategies
> 
> Please refer to the dedicated S3 integration guide.

### Step 1: Create S3 Bucket

1. **Navigate to S3**
   - AWS Console → S3
   - Click "Create bucket"

2. **Bucket Settings**
   - Bucket name: `lablink-images-<unique-id>`
   - Region: Same as EC2 (e.g., us-east-1)
   - Uncheck "Block all public access"
   - Acknowledge warning
   - Enable versioning (optional)
   - Create bucket

3. **Configure Bucket Policy**
   - Select bucket → Permissions → Bucket policy
   - Add policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::lablink-images-<unique-id>/*"
        }
    ]
}
```

### Step 2: Create IAM User for S3 Access

1. **Navigate to IAM**
   - AWS Console → IAM → Users
   - Click "Add users"

2. **User Details**
   - User name: `lablink-s3-user`
   - Access type: **Programmatic access**
   - Click "Next"

3. **Set Permissions**
   - Attach policies directly
   - Select **AmazonS3FullAccess** (or create custom policy)
   - Click "Next" → "Create user"

4. **Save Credentials**
   - Copy **Access key ID**
   - Copy **Secret access key**
   - Save securely (you won't see secret again!)

### Step 3: Configure Application for S3

```bash
# Update .env on EC2
nano .env

# Add S3 configuration
AWS_S3_BUCKET=lablink-images-<unique-id>
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_REGION=us-east-1

# Restart application
docker-compose restart backend
```

### Step 4: Update Application Code (if needed)

Add S3 upload functionality to `backend/component_routes.py`:

```python
import boto3
from botocore.exceptions import ClientError
import os

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)

def upload_to_s3(file, filename):
    """Upload file to S3 bucket"""
    bucket = os.getenv('AWS_S3_BUCKET')
    try:
        s3_client.upload_fileobj(
            file,
            bucket,
            filename,
            ExtraArgs={'ACL': 'public-read', 'ContentType': file.content_type}
        )
        return f"https://{bucket}.s3.amazonaws.com/{filename}"
    except ClientError as e:
        print(f"S3 upload error: {e}")
        return None
```

## Monitoring and Maintenance

### CloudWatch Monitoring

1. **Enable CloudWatch**
   - EC2 → Instances → Select instance
   - Actions → Monitor and troubleshoot → Manage CloudWatch alarms

2. **Create Alarms**
   - CPU utilization > 80%
   - Disk space < 20%
   - Network errors

### Application Logs

```bash
# View application logs
docker-compose logs -f backend

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# View system logs
sudo journalctl -u docker -f
```

### Backup Strategy

1. **RDS Automated Backups**
   - Already configured (7-day retention)
   - Manual snapshots: RDS → Databases → Actions → Take snapshot

2. **EC2 Snapshots**
   - EC2 → Volumes → Select volume
   - Actions → Create snapshot

3. **Application Backup**
   ```bash
   # Backup application files
   tar -czf lablink-backup-$(date +%Y%m%d).tar.gz /home/ubuntu/lablink
   
   # Upload to S3
   aws s3 cp lablink-backup-*.tar.gz s3://your-backup-bucket/
   ```

### Updates and Maintenance

```bash
# Update application code
cd ~/lablink
git pull origin main

# Rebuild and restart
docker-compose up -d --build

# Update system packages
sudo apt update
sudo apt upgrade -y

# Restart if kernel updated
sudo reboot
```

## Security Best Practices

1. **Restrict Security Groups**
   - SSH only from your IP
   - RDS only from EC2 security group
   - Use VPN for admin access

2. **Use IAM Roles** (instead of access keys)
   - Create IAM role for EC2
   - Attach S3 access policy
   - Attach role to EC2 instance

3. **Enable MFA**
   - Enable MFA on AWS root account
   - Enable MFA on IAM users

4. **Regular Updates**
   - Keep system packages updated
   - Update Docker images regularly
   - Monitor security advisories

5. **Use Secrets Manager**
   - Store database passwords in AWS Secrets Manager
   - Rotate credentials regularly

6. **Enable VPC Flow Logs**
   - Monitor network traffic
   - Detect suspicious activity

## Cost Optimization

1. **Use Free Tier**
   - t2.micro EC2 (750 hours/month)
   - db.t3.micro RDS (750 hours/month)
   - 30 GB EBS storage

2. **Stop Instances When Not Needed**
   ```bash
   # Stop EC2 (keeps data, stops charges)
   aws ec2 stop-instances --instance-ids i-xxxxx
   
   # Stop RDS (stops charges, keeps data)
   aws rds stop-db-instance --db-instance-identifier lablink-db
   ```

3. **Use Reserved Instances** (for production)
   - 1-year or 3-year commitment
   - Up to 75% savings

4. **Monitor Costs**
   - Set up billing alerts
   - Use AWS Cost Explorer
   - Review monthly bills

## Troubleshooting

### Cannot Connect to EC2

```bash
# Check security group allows SSH from your IP
# Verify key file permissions: chmod 400 lablink-key.pem
# Check instance is running
# Verify public IP hasn't changed (use Elastic IP)
```

### Cannot Connect to RDS

```bash
# Check security group allows PostgreSQL from EC2
# Verify endpoint is correct
# Check credentials
# Ensure RDS is in same VPC as EC2
```

### Application Not Starting

```bash
# Check Docker logs
docker-compose logs backend

# Check environment variables
cat .env

# Verify database connection
docker-compose exec backend python -c "from app import db; db.engine.connect()"

# Check disk space
df -h
```

### High Costs

```bash
# Check running instances
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State.Name]'

# Check RDS instances
aws rds describe-db-instances --query 'DBInstances[*].[DBInstanceIdentifier,DBInstanceStatus]'

# Review billing dashboard
# Stop unused resources
```

## Next Steps

- Set up automated backups
- Configure monitoring and alerts
- Implement CI/CD pipeline
- Set up staging environment
- Configure auto-scaling (for production)
- Implement caching (Redis/ElastiCache)
- Set up CDN (CloudFront) for static files

## Additional Resources

- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [AWS RDS Documentation](https://docs.aws.amazon.com/rds/)
- [Docker Documentation](https://docs.docker.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
