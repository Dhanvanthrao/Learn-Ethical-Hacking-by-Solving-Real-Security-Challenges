# [Web 100] Search Box

## Solution

Enter file://www.google.com/etc/flag.txt?

## Deployment

$ docker build -t searchbox .
$ docker run -d -p 4201:80 --name searchbox searchbox
