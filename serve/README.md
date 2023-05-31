# How to serve

* The serving code is based on [Gradio](https://gradio.app) and largely adapted from [Vicuna](https://github.com/lm-sys/FastChat/) repository.

1. Run the controller
```
python3 -m serve.controller
```

2. Run the model worker
```
python3 -m serve.model_worker --model-path $MODEL_PATH --port 21002 --worker-address=http://localhost:21002 --model-name=SelFee-13b
```

3. Run the web server
```
python3 -m serve.gradio_web_server --share
```
