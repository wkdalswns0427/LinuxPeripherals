# x86 Linux socket/WS program

`socket server` --> `socket client` <--> `websocket server`



build command

```shell
for each
docker build -t charsocket .

for networking
docker-compose up --build
```

run command

```shell
docker run --network host charsocket
```


