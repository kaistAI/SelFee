# How to serve

1. Run the controller
```
python3 -m serve.controller
```

2. Run the model worker
```
python3 -m serve.model_worker --model-path $MODEL_PATH --port 21002 --worker-address=http://localhost:21002 --model-name=selfee-13b
```

3. Run the web server
```
python3 -m serve.gradio_web_server --share
```
