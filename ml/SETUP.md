## Setup
The following instructions assumes that you have the miniconda package manager installed.
```
conda create -y --name artifice python==3.9
conda activate artifice
pip install -r requirements.in
pip uninstall transformers
pip install adapter-transformers==3.2.1
```