#!/bin/bash
# Setup storage directories for document uploads with proper permissions

set -e

echo "🗂️  Setting up storage directories..."

# Create upload directories
mkdir -p uploads
mkdir -p tmp/uploads

# Set permissions (read/write for owner, read for group)
chmod 755 uploads
chmod 755 tmp/uploads

echo "✅ Upload directory created: ./uploads"
echo "✅ Temporary directory created: ./tmp/uploads"

# Create .gitkeep files to preserve directories in git
touch uploads/.gitkeep
touch tmp/uploads/.gitkeep

echo "✅ Storage directories initialized successfully!"
echo ""
echo "Directory structure:"
echo "  uploads/        - Persistent storage for uploaded documents"
echo "  tmp/uploads/    - Temporary storage during upload processing"
echo ""
echo "Next steps:"
echo "  1. Configure UPLOAD_DIR in .env file"
echo "  2. Ensure proper backup strategy for ./uploads directory"
echo "  3. For production, consider using S3-compatible storage"
