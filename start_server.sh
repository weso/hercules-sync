if [-f "herc_sync/bin/activate"]
then
  echo Virtual env is already created.
else
  virtualenv herc_sync
fi

source herc_sync/bin/activate

pip install -r requirements.txt

python wsgi.py
