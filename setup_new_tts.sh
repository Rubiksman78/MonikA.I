apt-get install sox libsndfile1 ffmpeg
pip install wget text-unidecode pynini==2.1.4
python -m pip install git+https://github.com/NVIDIA/NeMo.git@$BRANCH#egg=nemo_toolkit[all]
wget https://raw.githubusercontent.com/NVIDIA/NeMo/main/nemo_text_processing/install_pynini.sh
bash install_pynini.sh