# [Web 50] Evaluation

## How It Works

Pretty much just open command injection. They have to cat flag.php

## Deployment

$ docker build -t evaluation .
$ docker run -d -p 4202:80 --name evaluation evaluation
