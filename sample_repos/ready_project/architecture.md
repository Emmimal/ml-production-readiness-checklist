# Architecture

feature_store -> train.py -> registry.yaml -> serve.py -> monitor.py -> retrain_trigger.py

Data flows one direction. serve.py is the only declared consumer of the model artifact.
