# Libraries for developing a client for CAIR

This repository contains the functions needed to develop a client able to connect to the CAIR services.
It is possible to develop a client for almost any device with a keyboard/microphone and a display/speaker.

The repository also contains the functions to develop a client for the SoftBank robots Pepper and NAO.

To build the library:
```
python setup.py bdist_wheel
```

To install the library go inside the created dist folder and run:
```
pip install <name_of_wheelfile.whl>
```

