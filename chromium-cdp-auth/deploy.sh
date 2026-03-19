#!/bin/sh

# Function to check if mkfs.erofs is available
check_mkfs_erofs() {
    if command -v mkfs.erofs &>/dev/null; then
        echo "mkfs.erofs is already installed."
        return 0
    else
        echo "mkfs.erofs is not installed."
        return 1
    fi
}

# Function to install erofs-utils package
install_erofs_utils() {
    if command -v apt-get &>/dev/null; then
        echo "Detected Ubuntu/Debian-based system. Installing erofs-utils..."
        sudo apt update
        sudo apt install -y erofs-utils
    elif command -v dnf &>/dev/null; then
        echo "Detected Fedora-based system. Installing erofs-utils..."
        sudo dnf install -y erofs-utils
    elif command -v yum &>/dev/null; then
        echo "Detected CentOS/RHEL-based system. Installing erofs-utils..."
        sudo yum install -y erofs-utils
    else
        echo "Unsupported package manager. Please install erofs-utils manually."
        exit 1
    fi
}

# Stop execution on errors
set -e

check_mkfs_erofs
if [ $? -ne 0 ]; then
    install_erofs_utils
fi

cd chromium-cdp/

# Build the root file system
rm -rf ./.rootfs || true

docker build -t chromium-cdp .
docker rm cnt-chromium-cdp || true
docker create --name cnt-chromium-cdp chromium-cdp /bin/sh
docker cp cnt-chromium-cdp:/ ./.rootfs

rm initrd || true
mkfs.erofs --all-root -d2 -E noinline_data initrd ./.rootfs

# Deploy an instance with a volume for persistent token storage
INSTANCE_NAME="${INSTANCE_NAME:-chromium-cdp}"
VOLUME_NAME="${VOLUME_NAME:-${INSTANCE_NAME}-data}"

# Create volume for token database (if it doesn't already exist)
kraft cloud volume create --size 64 --name "$VOLUME_NAME" 2>/dev/null || \
    echo "Volume '$VOLUME_NAME' already exists"

# Deploy the instance
kraft cloud deploy -M 4096 -p 443:8080 . --rootfs-type erofs \
    -e BOOTSTRAP_ADMIN_TOKEN="${BOOTSTRAP_ADMIN_TOKEN}" \
    -e DB_PATH="/app/data/tokens.db" \
    -v "$VOLUME_NAME:/app/data"
