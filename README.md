# How to run

1. Run the following shell script in order to generate the `docker-compose.yml` file
```bash
./generate_compose.sh [Number Of Relays | Default: 6] [Number Of Exit Nodes | Default: 3]
```

2. When finished, run the `cleanup.sh` script in order to wipe the `build` directory and `docker-compose.yml` file
```bash
./cleanup.sh
```

The `utils` directory is used to make persistent changes to any container. In it, there are different directories for each type of container present in our environment, and the files inside each directory are copied to the running containers.
