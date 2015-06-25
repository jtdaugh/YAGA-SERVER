var config = $config;

var client = require('./client').createClient({
    CELERY_BROKER_URL: config.celery.conn,
    CELERY_RESULT_BACKEND: 'amqp'
});

var celery = module.exports = {
    queuePushNotifications: function(notifs, cb) {
        notifs.forEach( function(notif){ client.call( 'yaga.tasks.NotificationTask', ['FirebaseNotification'] , {kwargs: notif} ); } );
        
        return cb(null);
    }
};
