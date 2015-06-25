var config = module.exports = {};

config.env = {
    RABBITMQ_BIGWIG_RX_URL: process.env.RABBITMQ_BIGWIG_RX_URL || '',
    REDISCLOUD_URL: process.env.REDISCLOUD_URL || 'redis://127.0.0.1:6379'
}

config.celery = {
    conn: config.env.RABBITMQ_BIGWIG_RX_URL
};

config.redis = {
    conn: config.env.REDISCLOUD_URL
}

config.firebase = {
    conn:{
        dev: 'https://yagadev.firebaseio.com/',
        prod: 'https://yaga.firebaseio.com/'
    }
};

config.db = {
    conn:{
        dev: 'postgres://pg:password@localhost/users',
        prod: ''
    }
};

config.push = {
    limit: 2, // limit per ttl
    ttl: 300  // 5 minutes / 300 seconds
}
