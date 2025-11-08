# AWS S3 Integration Guide for LabLink

This guide provides comprehensive instructions for integrating Amazon S3 storage with LabLink to store and serve component images. S3 integration is **optional** but recommended for production deployments to improve scalability and reduce server storage requirements.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step 1: Create S3 Bucket](#step-1-create-s3-bucket)
4. [Step 2: Configure IAM Permissions](#step-2-configure-iam-permissions)
5. [Step 3: Configure Environment Variables](#step-3-configure-environment-variables)
6. [Step 4: Implement S3 Upload in Application](#step-4-implement-s3-upload-in-application)
7. [Step 5: Update Frontend for S3 URLs](#step-5-update-frontend-for-s3-urls)
8. [Testing S3 Integration](#testing-s3-integration)
9. [Troubleshooting](#troubleshooting)
10. [Cost Considerations](#cost-considerations)

## Overview

### Why Use S3 for Component Images?

- **Scalability**: S3 can handle unlimited storage and high traffic
- **Reliability**: 99.999999999% (11 9's) durability
- **Performance**: Global CDN integration with CloudFront
- **Cost-Effective**: Pay only for what you use
- **Reduced Server Load**: Offload image storage from application server

### Architecture

```
┌─────────────────┐
│   User Browser  │
└────────┬────────┘
         │
         │ Upload Image
         ▼
┌─────────────────┐      ┌──────────────────┐
│  LabLink API    │─────▶│   AWS S3 Bucket  │
│  (EC2/Docker)   │      │  lablink-images  │
└─────────────────┘      └──────────────────┘
         │                        │
         │ Store URL              │ Serve Image
         ▼                        ▼
┌─────────────────┐      ┌──────────────────┐
│   PostgreSQL    │      │   User Browser   │
│   (RDS/Local)   │      │  (Direct Access) │
└─────────────────┘      └──────────────────┘
```

## Prerequisites

- AWS Account with billing enabled
- AWS CLI installed (optional but recommended)
- LabLink application deployed or running locally
- Basic understanding of AWS IAM and S3


## Step 1: Create S3 Bucket

### Option A: Using AWS Console (Recommended for Beginners)

1. **Navigate to S3 Service**
   - Login to [AWS Console](https://console.aws.amazon.com/)
   - Search for "S3" in the services search bar
   - Click on "S3" to open the S3 dashboard

2. **Create New Bucket**
   - Click the **"Create bucket"** button
   - You'll see the bucket creation form

3. **Configure Bucket Settings**

   **General Configuration:**
   - **Bucket name**: `lablink-images-<unique-identifier>`
     - Example: `lablink-images-prod-2024` or `lablink-images-dev-abc123`
     - Must be globally unique across all AWS accounts
     - Use lowercase letters, numbers, and hyphens only
     - Cannot contain spaces or uppercase letters
   
   - **AWS Region**: Select the same region as your EC2 instance
     - Example: `us-east-1` (N. Virginia)
     - Example: `us-west-2` (Oregon)
     - Example: `eu-west-1` (Ireland)
     - Choosing the same region reduces latency and data transfer costs

   **Object Ownership:**
   - Select **"ACLs disabled (recommended)"**
   - This is the modern approach for S3 bucket management

   **Block Public Access settings:**
   - **UNCHECK** "Block all public access"
   - Check the acknowledgment box: "I acknowledge that the current settings might result in this bucket and the objects within becoming public"
   - This allows component images to be publicly accessible via URLs

   **Bucket Versioning:**
   - Select **"Disable"** (for cost savings)
   - Or **"Enable"** if you want to keep previous versions of images

   **Tags (Optional):**
   - Add tags for organization:
     - Key: `Project`, Value: `LabLink`
     - Key: `Environment`, Value: `Production` or `Development`

   **Default Encryption:**
   - Select **"Server-side encryption with Amazon S3 managed keys (SSE-S3)"**
   - This is free and provides encryption at rest

   **Advanced Settings:**
   - Leave defaults (Object Lock disabled)

4. **Create Bucket**
   - Review all settings
   - Click **"Create bucket"**
   - You should see a success message

5. **Configure Bucket Policy for Public Read Access**
   
   After bucket creation:
   - Click on your newly created bucket name
   - Go to the **"Permissions"** tab
   - Scroll down to **"Bucket policy"**
   - Click **"Edit"**
   - Paste the following policy (replace `lablink-images-<unique-identifier>` with your actual bucket name):

   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Sid": "PublicReadGetObject",
               "Effect": "Allow",
               "Principal": "*",
               "Action": "s3:GetObject",
               "Resource": "arn:aws:s3:::lablink-images-<unique-identifier>/*"
           }
       ]
   }
   ```

   - Click **"Save changes"**
   - This policy allows anyone to read (download) objects from your bucket

6. **Configure CORS (Cross-Origin Resource Sharing)**
   
   Still in the **"Permissions"** tab:
   - Scroll down to **"Cross-origin resource sharing (CORS)"**
   - Click **"Edit"**
   - Paste the following CORS configuration:

   ```json
   [
       {
           "AllowedHeaders": ["*"],
           "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
           "AllowedOrigins": ["*"],
           "ExposeHeaders": ["ETag"],
           "MaxAgeSeconds": 3000
       }
   ]
   ```

   - Click **"Save changes"**
   - This allows your web application to upload files directly to S3 from the browser

### Option B: Using AWS CLI

If you have AWS CLI installed and configured:

```bash
# Set variables
BUCKET_NAME="lablink-images-prod-2024"
REGION="us-east-1"

# Create bucket
aws s3api create-bucket \
    --bucket $BUCKET_NAME \
    --region $REGION \
    --create-bucket-configuration LocationConstraint=$REGION

# Note: For us-east-1, omit the LocationConstraint:
# aws s3api create-bucket --bucket $BUCKET_NAME --region us-east-1

# Add bucket policy for public read
cat > bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --bucket $BUCKET_NAME \
    --policy file://bucket-policy.json

# Add CORS configuration
cat > cors-config.json << EOF
{
    "CORSRules": [
        {
            "AllowedHeaders": ["*"],
            "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
            "AllowedOrigins": ["*"],
            "ExposeHeaders": ["ETag"],
            "MaxAgeSeconds": 3000
        }
    ]
}
EOF

aws s3api put-bucket-cors \
    --bucket $BUCKET_NAME \
    --cors-configuration file://cors-config.json

# Enable encryption
aws s3api put-bucket-encryption \
    --bucket $BUCKET_NAME \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            }
        }]
    }'

echo "S3 bucket $BUCKET_NAME created successfully!"
```

### Verify Bucket Creation

1. **Via AWS Console:**
   - Go to S3 dashboard
   - You should see your bucket listed
   - Click on it to view details

2. **Via AWS CLI:**
   ```bash
   aws s3 ls
   # Should show your bucket in the list
   ```


## Step 2: Configure IAM Permissions

You need to create IAM credentials that allow your LabLink application to upload files to S3.

### Option A: IAM User with Access Keys (Simpler, Less Secure)

Best for: Development, testing, or when running LabLink outside AWS

1. **Navigate to IAM Service**
   - AWS Console → Search for "IAM"
   - Click on "IAM" to open the IAM dashboard

2. **Create New IAM User**
   - In the left sidebar, click **"Users"**
   - Click **"Create user"** button
   - User name: `lablink-s3-uploader`
   - Click **"Next"**

3. **Set Permissions**
   - Select **"Attach policies directly"**
   - Click **"Create policy"** (opens in new tab)

4. **Create Custom IAM Policy**
   
   In the new tab:
   - Click on the **"JSON"** tab
   - Replace the default policy with the following (replace `lablink-images-<unique-identifier>` with your bucket name):

   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Sid": "ListBucket",
               "Effect": "Allow",
               "Action": [
                   "s3:ListBucket",
                   "s3:GetBucketLocation"
               ],
               "Resource": "arn:aws:s3:::lablink-images-<unique-identifier>"
           },
           {
               "Sid": "UploadAndManageObjects",
               "Effect": "Allow",
               "Action": [
                   "s3:PutObject",
                   "s3:GetObject",
                   "s3:DeleteObject",
                   "s3:PutObjectAcl"
               ],
               "Resource": "arn:aws:s3:::lablink-images-<unique-identifier>/*"
           }
       ]
   }
   ```

   - Click **"Next"**
   - Policy name: `LabLinkS3UploadPolicy`
   - Description: `Allows LabLink to upload and manage component images in S3`
   - Click **"Create policy"**

5. **Attach Policy to User**
   - Go back to the user creation tab
   - Click the refresh button next to "Create policy"
   - Search for `LabLinkS3UploadPolicy`
   - Check the box next to it
   - Click **"Next"**
   - Review and click **"Create user"**

6. **Create Access Keys**
   - Click on the newly created user `lablink-s3-uploader`
   - Go to **"Security credentials"** tab
   - Scroll down to **"Access keys"**
   - Click **"Create access key"**
   - Select use case: **"Application running outside AWS"**
   - Click **"Next"**
   - Description (optional): `LabLink production server`
   - Click **"Create access key"**

7. **Save Credentials Securely**
   - **Access key ID**: `AKIAIOSFODNN7EXAMPLE` (example)
   - **Secret access key**: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` (example)
   - Click **"Download .csv file"** to save credentials
   - **IMPORTANT**: Save these credentials securely! You won't be able to see the secret key again
   - Click **"Done"**

### Option B: IAM Role for EC2 (More Secure, Recommended for Production)

Best for: LabLink running on AWS EC2

1. **Create IAM Role**
   - AWS Console → IAM → **"Roles"**
   - Click **"Create role"**
   - Trusted entity type: **"AWS service"**
   - Use case: **"EC2"**
   - Click **"Next"**

2. **Attach Policy**
   - Search for `LabLinkS3UploadPolicy` (created in Option A step 4)
   - Or create a new policy with the same JSON
   - Check the box next to the policy
   - Click **"Next"**

3. **Name and Create Role**
   - Role name: `LabLinkEC2S3Role`
   - Description: `Allows EC2 instances to upload images to S3`
   - Click **"Create role"**

4. **Attach Role to EC2 Instance**
   - Go to EC2 → Instances
   - Select your LabLink instance
   - Actions → Security → **"Modify IAM role"**
   - Select `LabLinkEC2S3Role`
   - Click **"Update IAM role"**

5. **No Access Keys Needed!**
   - When using IAM roles, your application automatically gets temporary credentials
   - No need to store access keys in environment variables
   - More secure and follows AWS best practices

### IAM Policy Explanation

The custom policy grants these permissions:

- **s3:ListBucket**: List objects in the bucket (useful for debugging)
- **s3:GetBucketLocation**: Get bucket region information
- **s3:PutObject**: Upload new files to S3
- **s3:GetObject**: Download files from S3 (for verification)
- **s3:DeleteObject**: Delete files from S3 (for cleanup)
- **s3:PutObjectAcl**: Set access control on uploaded objects

### Security Best Practices

1. **Use IAM Roles when possible** (Option B) instead of access keys
2. **Rotate access keys regularly** if using Option A (every 90 days)
3. **Never commit access keys to version control**
4. **Use environment variables** to store credentials
5. **Apply principle of least privilege** - only grant necessary permissions
6. **Enable MFA** on IAM users with console access
7. **Monitor IAM activity** using CloudTrail


## Step 3: Configure Environment Variables

### For Development (Local Machine)

1. **Update `.env` file in project root:**

   ```bash
   # AWS S3 Configuration (Optional)
   # Leave these commented out to use local file storage
   # Uncomment and configure to enable S3 storage

   # S3 Bucket name (created in Step 1)
   AWS_S3_BUCKET=lablink-images-prod-2024

   # AWS Region where bucket is located
   AWS_REGION=us-east-1

   # IAM User Access Keys (if using IAM User - Option A)
   AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
   AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

   # If using IAM Role (Option B), leave access keys commented out
   # The application will automatically use the EC2 instance role
   ```

2. **Restart the application:**

   ```bash
   # If using Docker Compose
   docker-compose restart backend

   # If running directly
   # Stop the Flask app (Ctrl+C) and restart:
   python backend/app.py
   ```

### For Production (AWS EC2)

1. **SSH into your EC2 instance:**

   ```bash
   ssh -i lablink-key.pem ubuntu@your-ec2-ip
   ```

2. **Navigate to application directory:**

   ```bash
   cd ~/lablink
   ```

3. **Edit `.env` file:**

   ```bash
   nano .env
   ```

4. **Add S3 configuration:**

   **If using IAM User (Option A):**
   ```bash
   # AWS S3 Configuration
   AWS_S3_BUCKET=lablink-images-prod-2024
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
   AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
   ```

   **If using IAM Role (Option B - Recommended):**
   ```bash
   # AWS S3 Configuration
   AWS_S3_BUCKET=lablink-images-prod-2024
   AWS_REGION=us-east-1
   # No access keys needed - using EC2 IAM role
   ```

5. **Save and exit:**
   - Press `Ctrl+X`
   - Press `Y` to confirm
   - Press `Enter` to save

6. **Restart application:**

   ```bash
   docker-compose restart backend
   ```

### Environment Variable Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `AWS_S3_BUCKET` | Yes | S3 bucket name for storing images | `lablink-images-prod-2024` |
| `AWS_REGION` | Yes | AWS region where bucket is located | `us-east-1`, `us-west-2`, `eu-west-1` |
| `AWS_ACCESS_KEY_ID` | Conditional | IAM user access key (not needed if using IAM role) | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | Conditional | IAM user secret key (not needed if using IAM role) | `wJalrXUtnFEMI/K7MDENG/...` |

### Verify Configuration

Test that environment variables are loaded correctly:

```bash
# Using Docker Compose
docker-compose exec backend python -c "import os; print('S3 Bucket:', os.getenv('AWS_S3_BUCKET')); print('Region:', os.getenv('AWS_REGION'))"

# Running directly
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('S3 Bucket:', os.getenv('AWS_S3_BUCKET')); print('Region:', os.getenv('AWS_REGION'))"
```

Expected output:
```
S3 Bucket: lablink-images-prod-2024
Region: us-east-1
```


## Step 4: Implement S3 Upload in Application

### Install Required Dependencies

1. **Add boto3 to requirements:**

   Edit `backend/requirements.txt` and add:
   ```
   boto3==1.28.85
   botocore==1.31.85
   ```

2. **Install dependencies:**

   ```bash
   # If using Docker Compose
   docker-compose build backend
   docker-compose up -d

   # If running directly
   pip install boto3 botocore
   ```

### Create S3 Utility Module

Create a new file `backend/s3_utils.py`:

```python
"""
S3 utility functions for uploading and managing component images.
"""
import os
import uuid
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from werkzeug.utils import secure_filename

# Initialize S3 client
def get_s3_client():
    """
    Create and return S3 client.
    Uses IAM role credentials if available, otherwise uses access keys.
    """
    region = os.getenv('AWS_REGION', 'us-east-1')
    
    # If access keys are provided, use them
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    if access_key and secret_key:
        return boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
    else:
        # Use IAM role (for EC2 instances)
        return boto3.client('s3', region_name=region)


def is_s3_enabled():
    """Check if S3 integration is enabled via environment variables."""
    return bool(os.getenv('AWS_S3_BUCKET'))


def upload_image_to_s3(file, original_filename):
    """
    Upload an image file to S3 bucket.
    
    Args:
        file: File object from Flask request.files
        original_filename: Original filename from upload
        
    Returns:
        str: Public URL of uploaded file, or None if upload fails
    """
    if not is_s3_enabled():
        return None
    
    bucket_name = os.getenv('AWS_S3_BUCKET')
    
    try:
        # Generate unique filename to prevent collisions
        file_extension = os.path.splitext(secure_filename(original_filename))[1]
        unique_filename = f"components/{uuid.uuid4()}{file_extension}"
        
        # Get S3 client
        s3_client = get_s3_client()
        
        # Determine content type
        content_type = file.content_type or 'image/jpeg'
        
        # Upload file to S3
        s3_client.upload_fileobj(
            file,
            bucket_name,
            unique_filename,
            ExtraArgs={
                'ContentType': content_type,
                'CacheControl': 'max-age=31536000',  # Cache for 1 year
            }
        )
        
        # Generate public URL
        region = os.getenv('AWS_REGION', 'us-east-1')
        s3_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{unique_filename}"
        
        return s3_url
        
    except NoCredentialsError:
        print("ERROR: AWS credentials not found")
        return None
    except ClientError as e:
        print(f"ERROR: S3 upload failed: {e}")
        return None
    except Exception as e:
        print(f"ERROR: Unexpected error during S3 upload: {e}")
        return None


def delete_image_from_s3(image_url):
    """
    Delete an image from S3 bucket.
    
    Args:
        image_url: Full S3 URL of the image
        
    Returns:
        bool: True if deletion successful, False otherwise
    """
    if not is_s3_enabled() or not image_url:
        return False
    
    bucket_name = os.getenv('AWS_S3_BUCKET')
    
    try:
        # Extract key from URL
        # URL format: https://bucket.s3.region.amazonaws.com/key
        if bucket_name in image_url:
            key = image_url.split(f"{bucket_name}.s3.")[-1].split("/", 1)[-1]
        else:
            return False
        
        # Get S3 client
        s3_client = get_s3_client()
        
        # Delete object
        s3_client.delete_object(Bucket=bucket_name, Key=key)
        
        return True
        
    except ClientError as e:
        print(f"ERROR: S3 deletion failed: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error during S3 deletion: {e}")
        return False


def get_s3_upload_url(filename, content_type='image/jpeg'):
    """
    Generate a presigned URL for direct browser upload to S3.
    This allows clients to upload directly to S3 without going through the backend.
    
    Args:
        filename: Original filename
        content_type: MIME type of the file
        
    Returns:
        dict: Contains 'url' for upload and 'fields' for form data, or None if failed
    """
    if not is_s3_enabled():
        return None
    
    bucket_name = os.getenv('AWS_S3_BUCKET')
    
    try:
        # Generate unique filename
        file_extension = os.path.splitext(secure_filename(filename))[1]
        unique_filename = f"components/{uuid.uuid4()}{file_extension}"
        
        # Get S3 client
        s3_client = get_s3_client()
        
        # Generate presigned POST URL
        response = s3_client.generate_presigned_post(
            Bucket=bucket_name,
            Key=unique_filename,
            Fields={'Content-Type': content_type},
            Conditions=[
                {'Content-Type': content_type},
                ['content-length-range', 0, 10485760]  # Max 10MB
            ],
            ExpiresIn=3600  # URL valid for 1 hour
        )
        
        # Add the final URL where file will be accessible
        region = os.getenv('AWS_REGION', 'us-east-1')
        response['file_url'] = f"https://{bucket_name}.s3.{region}.amazonaws.com/{unique_filename}"
        
        return response
        
    except ClientError as e:
        print(f"ERROR: Failed to generate presigned URL: {e}")
        return None
    except Exception as e:
        print(f"ERROR: Unexpected error generating presigned URL: {e}")
        return None
```

### Update Component Routes

Modify `backend/component_routes.py` to use S3 upload:

```python
from s3_utils import upload_image_to_s3, delete_image_from_s3, is_s3_enabled

# In the create/update component endpoint, replace local file save with:

@component_bp.route('/api/components', methods=['POST'])
@jwt_required()
def create_component():
    """Create a new component with optional image upload."""
    try:
        # ... existing validation code ...
        
        # Handle image upload
        image_url = None
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and image_file.filename:
                # Try S3 upload first
                if is_s3_enabled():
                    image_url = upload_image_to_s3(image_file, image_file.filename)
                    if not image_url:
                        return jsonify({'error': 'Failed to upload image to S3'}), 500
                else:
                    # Fallback to local storage
                    # ... existing local storage code ...
                    pass
        
        # ... rest of component creation code ...
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@component_bp.route('/api/components/<int:component_id>', methods=['DELETE'])
@jwt_required()
def delete_component(component_id):
    """Delete a component and its image."""
    try:
        # ... existing code to get component ...
        
        # Delete image from S3 if it exists
        if component.image_url and is_s3_enabled():
            delete_image_from_s3(component.image_url)
        
        # ... rest of deletion code ...
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Add S3 Status Endpoint

Add a health check endpoint to verify S3 configuration:

```python
@component_bp.route('/api/s3/status', methods=['GET'])
@jwt_required()
def s3_status():
    """Check S3 integration status."""
    from s3_utils import is_s3_enabled, get_s3_client
    
    if not is_s3_enabled():
        return jsonify({
            'enabled': False,
            'message': 'S3 integration is not configured'
        }), 200
    
    try:
        # Test S3 connection
        s3_client = get_s3_client()
        bucket_name = os.getenv('AWS_S3_BUCKET')
        s3_client.head_bucket(Bucket=bucket_name)
        
        return jsonify({
            'enabled': True,
            'bucket': bucket_name,
            'region': os.getenv('AWS_REGION'),
            'message': 'S3 is configured and accessible'
        }), 200
        
    except Exception as e:
        return jsonify({
            'enabled': True,
            'error': str(e),
            'message': 'S3 is configured but not accessible'
        }), 500
```


## Step 5: Update Frontend for S3 URLs

The frontend doesn't need major changes since S3 URLs work like regular image URLs. However, you may want to add status indicators.

### Update API Client (frontend/api.js)

Add S3 status check:

```javascript
// Check S3 integration status
async function checkS3Status() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/s3/status`, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            return data;
        }
        return { enabled: false };
    } catch (error) {
        console.error('Failed to check S3 status:', error);
        return { enabled: false };
    }
}
```

### Display S3 Status (Optional)

Add to faculty dashboard to show storage backend:

```javascript
// In faculty_dashboard.js
async function displayStorageInfo() {
    const s3Status = await checkS3Status();
    const storageInfo = document.getElementById('storage-info');
    
    if (s3Status.enabled) {
        storageInfo.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-cloud"></i> 
                Images stored in AWS S3 (${s3Status.bucket})
            </div>
        `;
    } else {
        storageInfo.innerHTML = `
            <div class="alert alert-secondary">
                <i class="fas fa-server"></i> 
                Images stored locally
            </div>
        `;
    }
}
```

### Image Display

S3 URLs work directly in HTML:

```html
<!-- Component image from S3 -->
<img src="https://lablink-images-prod-2024.s3.us-east-1.amazonaws.com/components/abc123.jpg" 
     alt="Component" 
     class="component-image">
```

No changes needed to existing image display code - S3 URLs are drop-in replacements for local URLs.


## Testing S3 Integration

### Test 1: Verify S3 Configuration

```bash
# Check if environment variables are set
docker-compose exec backend python -c "
from s3_utils import is_s3_enabled, get_s3_client
import os

print('S3 Enabled:', is_s3_enabled())
print('Bucket:', os.getenv('AWS_S3_BUCKET'))
print('Region:', os.getenv('AWS_REGION'))

if is_s3_enabled():
    try:
        client = get_s3_client()
        bucket = os.getenv('AWS_S3_BUCKET')
        client.head_bucket(Bucket=bucket)
        print('✓ Successfully connected to S3 bucket')
    except Exception as e:
        print('✗ Failed to connect:', e)
"
```

Expected output:
```
S3 Enabled: True
Bucket: lablink-images-prod-2024
Region: us-east-1
✓ Successfully connected to S3 bucket
```

### Test 2: Upload Test Image via API

```bash
# Create a test image
curl -o test-component.jpg https://via.placeholder.com/300

# Login to get JWT token
TOKEN=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"faculty@university.edu","password":"faculty123"}' \
  | jq -r '.access_token')

# Upload component with image
curl -X POST http://localhost:5000/api/components \
  -H "Authorization: Bearer $TOKEN" \
  -F "name=Test Component" \
  -F "category=Resistor" \
  -F "quantity=10" \
  -F "location=Lab A" \
  -F "image=@test-component.jpg"
```

Expected response:
```json
{
  "id": 123,
  "name": "Test Component",
  "image_url": "https://lablink-images-prod-2024.s3.us-east-1.amazonaws.com/components/abc-123-def.jpg",
  ...
}
```

### Test 3: Verify Image is Accessible

```bash
# Get the image_url from the response above
IMAGE_URL="https://lablink-images-prod-2024.s3.us-east-1.amazonaws.com/components/abc-123-def.jpg"

# Test if image is publicly accessible
curl -I $IMAGE_URL
```

Expected response:
```
HTTP/1.1 200 OK
Content-Type: image/jpeg
Content-Length: 12345
...
```

### Test 4: Check S3 Bucket Contents

Via AWS Console:
1. Go to S3 → Your bucket
2. Navigate to `components/` folder
3. You should see uploaded images

Via AWS CLI:
```bash
aws s3 ls s3://lablink-images-prod-2024/components/
```

### Test 5: Test Image Deletion

```bash
# Delete the test component
curl -X DELETE http://localhost:5000/api/components/123 \
  -H "Authorization: Bearer $TOKEN"

# Verify image is deleted from S3
curl -I $IMAGE_URL
# Should return 404 Not Found
```

### Test 6: Frontend Upload Test

1. Login to LabLink as faculty
2. Go to Components section
3. Click "Add Component"
4. Fill in details and upload an image
5. Submit the form
6. Verify the component displays with the image
7. Check browser DevTools Network tab - image should load from S3 URL


## Troubleshooting

### Issue: "NoCredentialsError: Unable to locate credentials"

**Cause**: AWS credentials are not configured properly.

**Solutions**:

1. **If using IAM User (access keys):**
   ```bash
   # Verify environment variables are set
   docker-compose exec backend env | grep AWS
   
   # Should show:
   # AWS_S3_BUCKET=lablink-images-prod-2024
   # AWS_REGION=us-east-1
   # AWS_ACCESS_KEY_ID=AKIA...
   # AWS_SECRET_ACCESS_KEY=...
   ```

   If not showing, check your `.env` file and restart:
   ```bash
   docker-compose restart backend
   ```

2. **If using IAM Role (EC2):**
   ```bash
   # Verify IAM role is attached to EC2 instance
   curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
   
   # Should return role name: LabLinkEC2S3Role
   ```

   If not, attach the role via AWS Console:
   - EC2 → Instances → Select instance
   - Actions → Security → Modify IAM role

### Issue: "AccessDenied: Access Denied"

**Cause**: IAM permissions are insufficient.

**Solutions**:

1. **Check IAM policy includes required permissions:**
   - s3:PutObject
   - s3:GetObject
   - s3:DeleteObject
   - s3:ListBucket

2. **Verify bucket policy allows public read:**
   - S3 → Bucket → Permissions → Bucket policy
   - Should have PublicReadGetObject statement

3. **Check bucket is not blocking public access:**
   - S3 → Bucket → Permissions → Block public access
   - Should be OFF

### Issue: "NoSuchBucket: The specified bucket does not exist"

**Cause**: Bucket name is incorrect or bucket is in different region.

**Solutions**:

1. **Verify bucket name:**
   ```bash
   aws s3 ls | grep lablink
   ```

2. **Check bucket region matches AWS_REGION:**
   ```bash
   aws s3api get-bucket-location --bucket lablink-images-prod-2024
   ```

3. **Update .env with correct bucket name and region**

### Issue: Images upload but return 403 Forbidden when accessed

**Cause**: Bucket policy doesn't allow public read access.

**Solution**:

Add bucket policy for public read:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::lablink-images-prod-2024/*"
        }
    ]
}
```

### Issue: CORS errors when uploading from browser

**Cause**: CORS is not configured on S3 bucket.

**Solution**:

Add CORS configuration:
```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": ["ETag"],
        "MaxAgeSeconds": 3000
    }
]
```

### Issue: "SignatureDoesNotMatch" error

**Cause**: System clock is out of sync or incorrect secret key.

**Solutions**:

1. **Sync system clock:**
   ```bash
   # On EC2/Linux
   sudo ntpdate -s time.nist.gov
   
   # Or install and enable NTP
   sudo apt install ntp
   sudo systemctl enable ntp
   sudo systemctl start ntp
   ```

2. **Verify secret access key is correct** (no extra spaces or characters)

### Issue: Slow upload speeds

**Cause**: Large images or network latency.

**Solutions**:

1. **Implement image compression before upload:**
   ```python
   from PIL import Image
   import io
   
   def compress_image(file, max_size=(1024, 1024), quality=85):
       img = Image.open(file)
       img.thumbnail(max_size, Image.Resampling.LANCZOS)
       
       output = io.BytesIO()
       img.save(output, format='JPEG', quality=quality, optimize=True)
       output.seek(0)
       return output
   ```

2. **Use S3 Transfer Acceleration:**
   - Enable on bucket: S3 → Bucket → Properties → Transfer acceleration
   - Update endpoint in code to use accelerated endpoint

3. **Choose S3 region closest to users**

### Issue: High S3 costs

**Cause**: Too many requests or large storage usage.

**Solutions**:

1. **Implement image optimization:**
   - Compress images before upload
   - Use appropriate image formats (WebP, JPEG)
   - Set reasonable size limits

2. **Use S3 Lifecycle policies:**
   ```bash
   # Delete old images after 90 days
   aws s3api put-bucket-lifecycle-configuration \
     --bucket lablink-images-prod-2024 \
     --lifecycle-configuration file://lifecycle.json
   ```

   lifecycle.json:
   ```json
   {
       "Rules": [
           {
               "Id": "DeleteOldImages",
               "Status": "Enabled",
               "Prefix": "components/",
               "Expiration": {
                   "Days": 90
               }
           }
       ]
   }
   ```

3. **Use CloudFront CDN** to reduce S3 GET requests

4. **Monitor usage:**
   - AWS Console → S3 → Bucket → Metrics
   - Set up billing alerts

### Debug Mode

Enable detailed logging:

```python
# In s3_utils.py, add at the top:
import logging

logging.basicConfig(level=logging.DEBUG)
boto3.set_stream_logger('boto3.resources', logging.DEBUG)
```


## Cost Considerations

### S3 Pricing Overview (as of 2024)

**Storage Costs:**
- First 50 TB: $0.023 per GB/month
- Example: 10 GB of images = $0.23/month

**Request Costs:**
- PUT/POST requests: $0.005 per 1,000 requests
- GET requests: $0.0004 per 1,000 requests
- Example: 10,000 image views = $0.004

**Data Transfer:**
- Data IN to S3: Free
- Data OUT to Internet: $0.09 per GB (first 10 TB)
- Example: 100 GB transferred = $9.00

### Cost Estimation for LabLink

**Small Deployment (100 components, 1000 users):**
- Storage: 2 GB images = $0.05/month
- Requests: 50,000 views = $0.02/month
- Transfer: 10 GB = $0.90/month
- **Total: ~$1/month**

**Medium Deployment (1000 components, 10,000 users):**
- Storage: 20 GB images = $0.46/month
- Requests: 500,000 views = $0.20/month
- Transfer: 100 GB = $9.00/month
- **Total: ~$10/month**

**Large Deployment (10,000 components, 100,000 users):**
- Storage: 200 GB images = $4.60/month
- Requests: 5,000,000 views = $2.00/month
- Transfer: 1 TB = $90.00/month
- **Total: ~$97/month**

### Cost Optimization Tips

1. **Use CloudFront CDN:**
   - Reduces S3 GET requests
   - Cheaper data transfer rates
   - Faster global delivery
   - Can reduce costs by 50-70%

2. **Implement Image Optimization:**
   - Compress images before upload
   - Use WebP format (smaller file sizes)
   - Set maximum image dimensions
   - Can reduce storage and transfer by 60-80%

3. **Enable S3 Intelligent-Tiering:**
   - Automatically moves infrequently accessed images to cheaper storage
   - No retrieval fees
   - Saves 40-70% on storage costs

4. **Set Lifecycle Policies:**
   - Archive old images to Glacier
   - Delete unused images automatically
   - Transition to cheaper storage classes

5. **Monitor and Alert:**
   - Set up AWS Budgets
   - Create billing alerts
   - Review Cost Explorer monthly

### Free Tier Benefits

AWS Free Tier (first 12 months):
- 5 GB S3 storage
- 20,000 GET requests
- 2,000 PUT requests
- 15 GB data transfer out

Perfect for development and testing!

### Cost Comparison: S3 vs Local Storage

**Local Storage (EC2 EBS):**
- 100 GB EBS volume: $10/month
- Limited by server capacity
- Requires backups
- Single point of failure

**S3 Storage:**
- 100 GB S3: $2.30/month
- Unlimited scalability
- Built-in redundancy (11 9's durability)
- No backup management needed
- Pay only for what you use

**Recommendation**: S3 is more cost-effective for image storage, especially as your application scales.


## Advanced Features (Optional)

### CloudFront CDN Integration

Improve performance and reduce costs with CloudFront:

1. **Create CloudFront Distribution:**
   - AWS Console → CloudFront → Create distribution
   - Origin domain: `lablink-images-prod-2024.s3.us-east-1.amazonaws.com`
   - Origin access: Public
   - Viewer protocol policy: Redirect HTTP to HTTPS
   - Cache policy: CachingOptimized
   - Create distribution

2. **Update Application to Use CloudFront URLs:**
   ```python
   # In s3_utils.py
   def get_image_url(s3_key):
       cloudfront_domain = os.getenv('CLOUDFRONT_DOMAIN')
       if cloudfront_domain:
           return f"https://{cloudfront_domain}/{s3_key}"
       else:
           bucket = os.getenv('AWS_S3_BUCKET')
           region = os.getenv('AWS_REGION')
           return f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"
   ```

3. **Add to .env:**
   ```bash
   CLOUDFRONT_DOMAIN=d1234567890.cloudfront.net
   ```

### Image Optimization Pipeline

Automatically optimize images on upload:

```python
from PIL import Image
import io

def optimize_image(file, max_width=1200, max_height=1200, quality=85):
    """
    Optimize image before uploading to S3.
    - Resize to max dimensions
    - Compress with specified quality
    - Convert to RGB if needed
    """
    try:
        # Open image
        img = Image.open(file)
        
        # Convert RGBA to RGB if needed
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Resize if larger than max dimensions
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Save to bytes buffer
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        return output
    except Exception as e:
        print(f"Image optimization failed: {e}")
        file.seek(0)  # Reset file pointer
        return file

# Use in upload function:
def upload_image_to_s3(file, original_filename):
    # Optimize before upload
    optimized_file = optimize_image(file)
    
    # ... rest of upload code ...
```

### Presigned URLs for Direct Upload

Allow frontend to upload directly to S3 (bypasses backend):

```python
# Backend endpoint
@component_bp.route('/api/s3/upload-url', methods=['POST'])
@jwt_required()
def get_upload_url():
    """Generate presigned URL for direct S3 upload."""
    from s3_utils import get_s3_upload_url
    
    data = request.get_json()
    filename = data.get('filename')
    content_type = data.get('content_type', 'image/jpeg')
    
    upload_data = get_s3_upload_url(filename, content_type)
    
    if upload_data:
        return jsonify(upload_data), 200
    else:
        return jsonify({'error': 'Failed to generate upload URL'}), 500
```

```javascript
// Frontend usage
async function uploadImageDirectly(file) {
    // Get presigned URL from backend
    const response = await fetch(`${API_BASE_URL}/api/s3/upload-url`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${getToken()}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            filename: file.name,
            content_type: file.type
        })
    });
    
    const uploadData = await response.json();
    
    // Upload directly to S3
    const formData = new FormData();
    Object.keys(uploadData.fields).forEach(key => {
        formData.append(key, uploadData.fields[key]);
    });
    formData.append('file', file);
    
    await fetch(uploadData.url, {
        method: 'POST',
        body: formData
    });
    
    // Return the final URL
    return uploadData.file_url;
}
```

### S3 Event Notifications

Trigger actions when images are uploaded:

1. **Create SNS Topic or Lambda Function**
2. **Configure S3 Event Notification:**
   - S3 → Bucket → Properties → Event notifications
   - Create event notification
   - Event types: PUT, POST
   - Destination: SNS topic or Lambda
3. **Use cases:**
   - Generate thumbnails automatically
   - Scan images for inappropriate content
   - Update database with image metadata
   - Send notifications

### Backup and Versioning

Enable versioning for image recovery:

```bash
# Enable versioning
aws s3api put-bucket-versioning \
    --bucket lablink-images-prod-2024 \
    --versioning-configuration Status=Enabled

# List versions of a file
aws s3api list-object-versions \
    --bucket lablink-images-prod-2024 \
    --prefix components/abc123.jpg
```

### Cross-Region Replication

Replicate images to another region for disaster recovery:

1. **Create destination bucket in another region**
2. **Enable versioning on both buckets**
3. **Create replication rule:**
   - S3 → Source bucket → Management → Replication rules
   - Create replication rule
   - Destination: Other bucket
   - IAM role: Create new role

## Summary

You've successfully integrated AWS S3 with LabLink! Here's what you accomplished:

✅ Created S3 bucket for storing component images
✅ Configured IAM permissions for secure access
✅ Set up environment variables for S3 configuration
✅ Implemented S3 upload/delete functionality in backend
✅ Updated frontend to work with S3 URLs
✅ Tested the integration end-to-end

### Next Steps

1. **Monitor S3 usage** in AWS Console
2. **Set up billing alerts** to avoid unexpected costs
3. **Consider CloudFront CDN** for better performance
4. **Implement image optimization** to reduce costs
5. **Enable versioning** for important images
6. **Review security settings** regularly

### Quick Reference

**Environment Variables:**
```bash
AWS_S3_BUCKET=lablink-images-prod-2024
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...  # Only if using IAM user
AWS_SECRET_ACCESS_KEY=...   # Only if using IAM user
```

**Useful Commands:**
```bash
# List bucket contents
aws s3 ls s3://lablink-images-prod-2024/components/

# Check S3 status
docker-compose exec backend python -c "from s3_utils import is_s3_enabled; print(is_s3_enabled())"

# View S3 costs
aws ce get-cost-and-usage --time-period Start=2024-01-01,End=2024-01-31 --granularity MONTHLY --metrics BlendedCost --filter file://s3-filter.json
```

### Support Resources

- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [Boto3 S3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)
- [AWS S3 Pricing](https://aws.amazon.com/s3/pricing/)
- [AWS Free Tier](https://aws.amazon.com/free/)

---

**Need Help?** Check the [Troubleshooting](#troubleshooting) section or refer to the main [AWS Deployment Guide](DEPLOYMENT_AWS.md).
