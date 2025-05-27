
# Network Security - Network Censorship

This project simulates a network censorship environment similar to those found in authoritarian regimes. It models a client located inside a censored country, a hidden service located outside, and a censorship firewall that attempts to detect and block Tor-like communication patterns. The goal is to implement both censorship techniques and strategies for censorship resistance.

## Installation

### Prerequisites

* [`Docker`](https://www.docker.com)
* [`Docker Compose`](https://www.docker.com)

### Installing Docker

The best approach to install `Docker` is to follow the official guide [here](https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-using-the-repository).

Please follow the steps in the **Install using the repository** section.

Next, follow [these](https://docs.docker.com/install/linux/linux-postinstall/) steps to configure Docker access with non-sudo permissions in the **Manage Docker as a non-root user** section.

### Installing Docker Compose

The best approach to install `Docker Compose` is to follow the official guide [here](https://docs.docker.com/compose/install/#install-compose).

## Usage

To start developing, you must build and start the servers and networks:

```bash
./restart.sh
```

Then you can send `tor` messages from the `client` to the `hidden service`:

```bash
./send_tor_message.sh
```

You can also send `webRTC` messages from the `client` to the `hidden service`:

```bash
./send_webRTC_message.sh
```

You can also generate a `docker-compose.yml` file:

```bash
./generate_compose.sh [Number of Relays | Default: 6] [Number of Exit Nodes | Default: 3]
```

When finished, run the `cleanup.sh` script to remove the `build` directory and the `docker-compose.yml` file:

```bash
./cleanup.sh
```

## Project Structure

```
├── censor :: Acts as the firewall or network censor. Monitors network traffic for Tor-like patterns  and blocks traffic or IP addresses accordingly.
├── client :: Simulates a user inside the censored country attempting to send messages to the hidden service using obfuscated packets.
├── true_client :: Simulates a user inside the censored country attempting to send messages to the hidden service.
├── exit :: Represents the final node in the Tor-like relay path that delivers the message to the hidden service.
├── hidden_service :: The destination service located outside the censored region that receives the client’s messages.
├── relay-tor :: Intermediate nodes that help route messages from the client to the hidden service, forming an onion-routing-like path.
└── relay :: Intermediate nodes that help route messages from the client to the hidden service, forming an onion-routing-like path.
```


