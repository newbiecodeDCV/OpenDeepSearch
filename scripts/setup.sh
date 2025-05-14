#!/bin/bash

echo " Bắt đầu cài đặt "

# 1. Cài đặt Miniconda
echo "🔧 Miniconda chưa được cài. Đang tải và cài đặt..."
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda
export PATH="$HOME/miniconda/bin:$PATH"
echo 'export PATH="$HOME/miniconda/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# 2. Tạo và activate Conda environment
echo "📦 Tạo môi trường Conda mới với Python 3.10"
conda create -n "ods_env" python="3.10" -y
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "ods_env"

# 3. Cài đặt torch
echo "📥 Cài đặt torch..."
pip install torch


# 4. Cài đặt dependencies từ requirements.txt
echo "📥 Cài đặt dependencies "
pip install -e .
pip install -r requirements.txt


echo "🎉 Thiết lập hoàn tất.!"
