# AWS Quick Start - You Have Your EC2 Key!

You've created an EC2 instance and received your private key. Here's what to do next.

## ⚠️ IMPORTANT: Secure Your Private Key First!

The private key you received is like a password - keep it safe!

### Step 1: Save Your Private Key

**Windows:**
```cmd
# Create a .ssh folder if it doesn't exist
mkdir %USERPROFILE%\.ssh

# Save the key
# 1. Open Notepad
# 2. Paste the entire key (including BEGIN and END lines)
# 3. Save as: %USERPROFILE%\.ssh\lablink-key.pem
# 4. Make sure "Save as type" is "All Files" (not .txt)
```

**Mac/Linux:**
```bash
# Create .ssh folder if it doesn't exist
mkdir -p ~/.ssh

# Create the key file
nano ~/.ssh/lablink-key.pem

# Paste the entire key (including BEGIN and END lines)
# Save: Ctrl+X, then Y, then Enter

# Set correct permissions (REQUIRED!)
chmod 400 ~/.ssh/lablink-key.pem
```

Your key should look like this:
```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAvlNWUsQyjUd/JzIlRFFdt4NKhvi+lAuLENHgRLWBZsbIh1IE
...
(many lines)
...
-----END RSA PRIVATE KEY-----
```

---

## Step 2: Get Your EC2 Instance Information

You need to find your EC2 instance's public IP address:

1. **Go to AWS Console**
   - Visit: https://console.aws.amazon.com/
   - Navigate to: **EC2** → **Instances**

2. **Find Your Instance**
   - Look for your instance (probably named something like "lablink-server")
   - Check the **Instance State** - it should be "Running" (green)

3. **Copy the Public IP**
   - Select your instance
   - Look for **Public IPv4 address** (e.g., `54.123.45.67`)
   - Copy this IP address

---

## Step 3: Connect to Your EC2 Instance

### Windows (Using PowerShell or CMD)

```powershell
# Connect via SSH
ssh -i %USERPROFILE%\.ssh\lablink-key.pem ubuntu@YOUR_EC2_PUBLIC_IP

# Replace YOUR_EC2_PUBLIC_IP with your actual IP
# Example: ssh -i %USERPROFILE%\.ssh\lablink-key.pem ubuntu@54.123.45.67
```

**If you get "WARNING: UNPROTECTED PRIVATE KEY FILE":**
```powershell
# Right-click lablink-key.pem → Properties → Security
# Remove all users except yourself
# Give yourself "Read" permission only
```

**Alternative: Use PuTTY**
1. Download PuTTY and PuTTYgen
2. Use PuTTYgen to convert .pem to .ppk
3. Use PuTTY to connect with the .ppk file

### Mac/Linux

```bash
# Connect via SSH
ssh -i ~/.ssh/lablink-key.pem ubuntu@YOUR_EC2_PUBLIC_IP

# Replace YOUR_EC2_PUBLIC_IP with your actual IP
# Example: ssh -i ~/.ssh/lablink-key.pem ubuntu@54.123.45.67
```

**First time connecting:**
- You'll see: "The authenticity of host... can't be established"
- Type: `yes` and press Enter

**Success looks like:**
```
ubuntu@ip-172-31-xx-xx:~$
```

---

## Step 4: Install Docker on EC2

Once connected to your EC2 instance, run these commands:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add ubuntu user to docker group
sudo usermod -aG docker ubuntu

# Verify installation
docker --version
docker-compose --version

# Log out and back in for group changes
exit
```

Then reconnect:
```bash
ssh -i ~/.ssh/lablink-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

---

## Step 5: Set Up PostgreSQL Database

You have two options:

### Option A: Use Docker PostgreSQL (Simpler)

```bash
# Clone your project
git clone <your-repository-url>
cd lablink

# Or upload files from your computer:
# From your local machine (new terminal):
# scp -i ~/.ssh/lablink-key.pem -r /path/to/lablink ubuntu@YOUR_EC2_PUBLIC_IP:~/

# Copy environment file
cp .env.docker .env

# Edit for production
nano .env
```

Update these values in `.env`:
```bash
FLASK_ENV=production
SECRET_KEY=GENERATE_STRONG_KEY_HERE
JWT_SECRET_KEY=GENERATE_STRONG_KEY_HERE
CORS_ORIGINS=http://YOUR_EC2_PUBLIC_IP
```

Generate secure keys:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Then start everything:
```bash
docker-compose up -d
```

### Option B: Use AWS RDS (Production-Ready)

Follow the detailed RDS setup in [DEPLOYMENT_AWS.md](DEPLOYMENT_AWS.md#part-1-aws-rds-postgresql-setup)

---

## Step 6: Configure Security Group

Your EC2 instance needs to allow web traffic:

1. **Go to AWS Console**
   - EC2 → Instances → Select your instance
   - Click on **Security** tab
   - Click on the security group link

2. **Edit Inbound Rules**
   - Click **Edit inbound rules**
   - Add these rules:

| Type | Protocol | Port | Source | Description |
|------|----------|------|--------|-------------|
| SSH | TCP | 22 | My IP | SSH access |
| HTTP | TCP | 80 | 0.0.0.0/0 | Web access |
| HTTPS | TCP | 443 | 0.0.0.0/0 | Secure web |
| Custom TCP | TCP | 5000 | 0.0.0.0/0 | API (testing) |

3. **Save rules**

---

## Step 7: Access Your Application

### Check if it's running:

```bash
# On EC2 instance
docker-compose ps

# Check logs
docker-compose logs -f backend

# Test API
curl http://localhost:5000/health
```

### Access from your browser:

1. **API Endpoint:**
   ```
   http://YOUR_EC2_PUBLIC_IP:5000/health
   ```

2. **Frontend:**
   - Upload frontend files to EC2
   - Or set up Nginx (see Step 8)

---

## Step 8: Set Up Nginx (Recommended)

Nginx will serve your frontend and proxy API requests:

```bash
# Install Nginx
sudo apt install -y nginx

# Create configuration
sudo nano /etc/nginx/sites-available/lablink
```

Paste this configuration:
```nginx
server {
    listen 80;
    server_name YOUR_EC2_PUBLIC_IP;

    # Frontend files
    root /home/ubuntu/lablink/frontend;
    index login.html;

    location / {
        try_files $uri $uri/ =404;
    }

    # API proxy
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /health {
        proxy_pass http://localhost:5000/health;
    }
}
```

Save and enable:
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/lablink /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test and restart
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

Now access your app at:
```
http://YOUR_EC2_PUBLIC_IP
```

---

## Step 9: Test Your Application

1. **Open browser:**
   ```
   http://YOUR_EC2_PUBLIC_IP
   ```

2. **Login with default credentials:**
   - Faculty: `faculty` / `faculty123`
   - Student: `student` / `student123`

3. **Test features:**
   - Browse components
   - Create requests
   - Approve/reject requests

---

## Quick Reference Commands

### SSH Connection
```bash
# Connect to EC2
ssh -i ~/.ssh/lablink-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### Docker Commands
```bash
# View running containers
docker-compose ps

# View logs
docker-compose logs -f

# Restart application
docker-compose restart

# Stop application
docker-compose down

# Rebuild and start
docker-compose up -d --build
```

### Check Status
```bash
# Check if backend is running
curl http://localhost:5000/health

# Check Nginx status
sudo systemctl status nginx

# Check disk space
df -h

# Check memory
free -h
```

---

## Troubleshooting

### Can't connect via SSH

**Problem:** "Permission denied (publickey)"

**Solution:**
```bash
# Check key permissions
ls -l ~/.ssh/lablink-key.pem
# Should show: -r-------- (400)

# Fix permissions
chmod 400 ~/.ssh/lablink-key.pem
```

**Problem:** "Connection refused"

**Solution:**
- Check EC2 instance is running (AWS Console)
- Check security group allows SSH from your IP
- Verify you're using the correct IP address

### Can't access application in browser

**Problem:** "This site can't be reached"

**Solution:**
1. Check security group allows HTTP (port 80)
2. Check Docker containers are running: `docker-compose ps`
3. Check Nginx is running: `sudo systemctl status nginx`
4. Check you're using HTTP not HTTPS: `http://YOUR_IP`

### Database connection errors

**Problem:** "Could not connect to database"

**Solution:**
```bash
# Check database container
docker-compose ps

# Check database logs
docker-compose logs db

# Verify DATABASE_URL in .env
cat .env | grep DATABASE_URL

# Test connection
docker-compose exec backend python -c "from models import db; print('Connected!' if db.engine.connect() else 'Failed')"
```

---

## Next Steps

Once everything is working:

1. ✅ **Set up a domain name** (optional)
   - Point domain to your EC2 IP
   - See [DEPLOYMENT_AWS.md](DEPLOYMENT_AWS.md#part-4-configure-domain-and-ssl-optional)

2. ✅ **Enable HTTPS with SSL**
   - Use Let's Encrypt (free)
   - See SSL setup in deployment guide

3. ✅ **Set up AWS RDS** (for production)
   - Managed PostgreSQL database
   - Better for production than Docker database

4. ✅ **Configure backups**
   - EC2 snapshots
   - Database backups

5. ✅ **Set up monitoring**
   - CloudWatch alarms
   - Log monitoring

---

## Important Security Notes

1. **Never share your private key** - It's like your password
2. **Restrict SSH access** - Only allow your IP in security group
3. **Change default passwords** - Update faculty/student passwords
4. **Use strong secrets** - Generate random SECRET_KEY and JWT_SECRET_KEY
5. **Enable HTTPS** - Use SSL certificate for production
6. **Keep system updated** - Run `sudo apt update && sudo apt upgrade` regularly

---

## Getting Help

- **Detailed AWS Guide:** [DEPLOYMENT_AWS.md](DEPLOYMENT_AWS.md)
- **Docker Guide:** [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)
- **API Documentation:** [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Database Setup:** [DO_I_NEED_POSTGRESQL.md](DO_I_NEED_POSTGRESQL.md)

---

## Summary

You've completed these steps:
1. ✅ Saved your private key securely
2. ✅ Connected to EC2 instance
3. ✅ Installed Docker
4. ✅ Deployed LabLink application
5. ✅ Configured security group
6. ✅ Set up Nginx
7. ✅ Accessed your application

**Your application is now running on AWS!** 🎉

Access it at: `http://YOUR_EC2_PUBLIC_IP`
