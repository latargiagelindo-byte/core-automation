module.exports = {
  apps: [{
    name: "actual-server",
    script: "/opt/node-v22/lib/node_modules/@actual-app/sync-server/build/bin/actual-server.js",
    interpreter: "/opt/node-v22/bin/node",
    args: "--config /opt/core-automation/data/actual/config.json",
    cwd: "/opt/core-automation/data/actual",
    env: {
      PATH: "/opt/node-v22/bin:/usr/local/bin:/usr/bin:/bin",
      NODE_ENV: "production",
      ACTUAL_CONFIG_PATH: "/opt/core-automation/data/actual/config.json"
    },
    max_memory_restart: "350M",
    autorestart: true,
    watch: false
  }]
};
