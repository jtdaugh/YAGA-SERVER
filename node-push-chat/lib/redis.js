var config = $config;
var _redis = require('redis');
var _parse = require('url').parse;

var redis = module.exports = createRedisClient();

function createRedisClient() {
    var url = _parse(config.redis.conn),
        port = url.port,
        host = url.hostname,
        options = {
            detect_buffers: true
        };

        if (url.auth) {
            options.auth_pass = url.auth.split(':')[1];
        }

    return _redis.createClient(port, host, options);
}
