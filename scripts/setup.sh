#!/bin/bash

# ====== THÔNG TIN NGƯỜI DÙNG NHẬP VÀO ======
REPO_URL="https://github.com/newbiecodeDCV/OpenDeepSearch.git"
PROJECT_DIR="OpenDeepSearch"
CONDA_ENV_NAME="ods_env"
PYTHON_VERSION="3.10"
ENV_FILE=".env"
ENV_EXAMPLE_FILE=".env.example"

# ====== BẮT ĐẦU SCRIPT ======
echo "📦 Bắt đầu cài đặt dự án OpenDeepSearch..."

# 1. Cài đặt Miniconda nếu chưa có
if ! command -v conda &> /dev/null; then
    echo "🔧 Miniconda chưa được cài. Đang tải và cài đặt..."
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
    bash miniconda.sh -b -p $HOME/miniconda
    export PATH="$HOME/miniconda/bin:$PATH"
    echo 'export PATH="$HOME/miniconda/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc
else
    echo "✅ Miniconda đã được cài."
fi

# 2. Clone repository
echo "🔽 Clone repository từ GitHub..."
git clone "$REPO_URL"
cd "$PROJECT_DIR" || { echo "❌ Không tìm thấy thư mục dự án."; exit 1; }

# 3. Tạo và activate Conda environment
echo "📦 Tạo môi trường Conda mới với Python $PYTHON_VERSION..."
conda create -n "$CONDA_ENV_NAME" python="$PYTHON_VERSION" -y
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$CONDA_ENV_NAME"

# 4. Cài đặt torch nếu chưa có
if ! python -c "import torch" &> /dev/null; then
    echo "📥 Cài đặt torch..."
    pip install torch
fi

# 5. Cài đặt dependencies từ requirements.txt
if [ -f requirements.txt ]; then
    echo "📥 Cài đặt dependencies từ requirements.txt..."
    pip install -r requirements.txt
else
    echo "⚠️ Không tìm thấy requirements.txt. Bỏ qua bước cài đặt dependencies."
fi

# 6. Tạo file .env từ mẫu nếu có
if [ -f "$ENV_EXAMPLE_FILE" ]; then
    echo "📝 Tạo file $ENV_FILE từ $ENV_EXAMPLE_FILE..."
    cp "$ENV_EXAMPLE_FILE" "$ENV_FILE"
    echo "👉 Vui lòng chỉnh sửa nội dung file $ENV_FILE nếu cần."
else
    echo "⚠️ Không tìm thấy $ENV_EXAMPLE_FILE. Bỏ qua bước tạo file môi trường."
fi

echo "🎉 Thiết lập hoàn tất. Bạn có thể bắt đầu chạy ứng dụng!"
