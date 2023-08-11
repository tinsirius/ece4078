# ece4078
Support files for ECE4078 Practicals

You can no longer install with `pythhon3 setup.py install`. Here is how you can install manually

```
python3 setup.py sdist
cd dist
pip install ...tar.gz
```

This repo is also hosted on PyPi, however, it will not always get the newest fix :P, and I did not put all of the dependencies in the `install_requires` tag so use it at your own risk!
```
python3 -m pip install ece4078
```
