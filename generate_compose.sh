#!/bin/bash

# ======================
# CONFIGURABLE VARIABLES
# ======================
NUM_RELAYS=${1:-6}
NUM_EXITS=${2:-3}

BASE_DIR=$(pwd)
BUILD_DIR="${BASE_DIR}/build"
COMPOSE_FILE="docker-compose.yml"
UTILS_DIR="${BASE_DIR}/utils"

# ======================
# HELPER FUNCTIONS
# ======================

prepare_build_dirs() {
  rm -rf "$BUILD_DIR"
  mkdir -p "$BUILD_DIR"
  rm -f "$COMPOSE_FILE"
}

create_build_context() {
  local name=$1
  local src=$2
  local dest=$3

  local context="${BUILD_DIR}/${name}"
  mkdir -p "${context}${dest}"
  cp -r "${src}/." "${context}${dest}"

   # Add entrypoint if it exists (not for censor)
  if [[ -f "${src}/entrypoint.sh" ]]; then
    entrypoint_line="ENTRYPOINT [\"${dest}/entrypoint.sh\"]"
  else
    entrypoint_line=''
  fi

  # Basic Dockerfile
  cat <<EOF > "${context}/Dockerfile"
FROM handsonsecurity/seed-ubuntu:large
COPY ./${dest} ${dest}
${entrypoint_line}
CMD ["/bin/bash"]
EOF
}

write_header() {
  echo -e "\nservices:" >> "$COMPOSE_FILE"
}

write_service_block() {
  local name=$1
  local container_name=$2
  local ip=$3
  local net=$4
  local extra=$5

  cat <<EOF >> "$COMPOSE_FILE"
  ${name}:
    build: ./build/${name}
    container_name: ${container_name}
    tty: true
    cap_add:
      - NET_ADMIN
    networks:
      ${net}:
        ipv4_address: ${ip}
${extra}
EOF
}

write_client() {
  create_build_context "client" "${UTILS_DIR}/client" "/volumes"
  write_service_block "client" "client-11.1.0.2" "11.1.0.2" "client_net"
}

write_relays() {
  for i in $(seq 1 $NUM_RELAYS); do
    ip="10.1.0.$((i+1))"
    name="relay${i}"
    create_build_context "$name" "${UTILS_DIR}/relay" "/volumes"
    write_service_block "$name" "${name}-${ip}" "$ip" "tor_net"
  done
}

write_exits() {
  for i in $(seq 1 $NUM_EXITS); do
    ip="10.1.1.${i}"
    name="exit_node${i}"
    create_build_context "$name" "${UTILS_DIR}/exit" "/volumes"
    # Also add shared hidden service certs if present
    mkdir -p "${BUILD_DIR}/${name}/volumes/certs/hidden_service"
    cp -r "${UTILS_DIR}/hidden_service/certs/." "${BUILD_DIR}/${name}/volumes/certs/hidden_service" 2>/dev/null
    write_service_block "$name" "${name}-${ip}" "$ip" "tor_net"
  done
}

write_hidden_service() {
  create_build_context "hidden_service" "${UTILS_DIR}/hidden_service" "/volumes"
  write_service_block "hidden_service" "hidden_service-10.1.2.2" "10.1.2.2" "tor_net"
}

write_censor() {
  local context="${BUILD_DIR}/censor"
  mkdir -p "${context}/censor"
  cp -r "${UTILS_DIR}/censor/." "${context}/censor"
  cp "${UTILS_DIR}/censor/Dockerfile" "${context}"

  cat <<EOF >> "$COMPOSE_FILE"
  censor:
    build: ./build/censor
    container_name: censor-11.1.0.254-10.1.0.253
    cap_add:
      - NET_ADMIN
      - NET_RAW
    networks:
      client_net:
        ipv4_address: 11.1.0.254
      tor_net:
        ipv4_address: 10.1.0.253
    tty: true

EOF
}

write_networks() {
cat <<EOF >> "$COMPOSE_FILE"

networks:
  tor_net:
    name: tor_net-10.1.0.0
    driver: bridge
    ipam:
      config:
        - subnet: 10.1.0.0/16
          gateway: 10.1.0.1

  client_net:
    name: client_net-11.1.0.0
    driver: bridge
    ipam:
      config:
        - subnet: 11.1.0.0/24
          gateway: 11.1.0.1
EOF
}

# ======================
# MAIN EXECUTION
# ======================

prepare_build_dirs
write_header
write_client
write_relays
write_exits
write_hidden_service
write_censor
write_networks

echo "✅ docker-compose.yml generated with $NUM_RELAYS relays and $NUM_EXITS exit nodes."
echo "✅ Docker build contexts are in ./build/"

