# Hash Executor

- Author: Maxime Arthaud < maxime@arthaud.me >
- Type: pwn

## Description

Yo bro',

I made this small program.
Tell me if you can break it.
Use your imagination.

nc localhost 5555

## Files provided to the challengers

- hash_executor

## Build the docker image

`make build`

## Run the docker container

`make run`

## Get the provided files

`make export`

## Update the flag

Update `src/flag` then `make build`

## Show container logs

`make logs`

## Clean

* `make clean` removes the container and the provided files
* `make clean-all` removes the container, the docker image and the provided files
