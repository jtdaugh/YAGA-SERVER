//external libs
var celery = $lib.celery;
var db = $lib.db;
var redis = $lib.redis;
var util = $lib.util;

//module declaration
//push handler for firebase events
var push = module.exports = function(firebase_event, cb){

    var data = firebase_event;

    // create basic push candidate info
    var comment_thread = { contents: data.val(), id: data.key() };
    var comment = util.firebase.getLastChild(comment_thread.contents);
    var commenter = comment.username, notif_type = comment.type;

    //push notification control flow
    $async.waterfall([
        
        //push candidate queue-up phase (with error handling!)
        function(cb){ return push.qualifyNotification(comment_thread, commenter, cb); },
        function(result, cb){ return push.prepareRecipientsInfo(comment_thread, commenter, cb); },
        function(recipients, cb){ return push.prepareRecipientNotifications(recipients, commenter, comment_thread.id, notif_type, cb); },
        
        ],
      
        cb
    );
};

push.genericErrorMsg = 'push notification not sent: ';

/* push notification handlers */

// enforce rate limiting policy
push.qualifyNotification = function(thread, commenter, cb){
    
    $async.waterfall([

            //check redis for thread/user push count
            function(callback){ return redis.hgetall(thread.id, callback); },
            function(push_map, callback){
                // no redis hash for this thread, create one and allow push
                if(!push_map) return redis.hset(thread.id, commenter, 1, callback);
                
                //enfore rate limit policy
                var pushes_sent = parseInt(push_map[commenter], 10) || 0;
                if(pushes_sent >= $config.push.limit) return new Error(push.genericErrorMsg+'commenter rate limit exceeded');
                
                return redis.hset(thread.id, commenter, pushes_sent + 1, callback);
            },
        ],
        cb
    );
    
};
push.prepareRecipientsInfo = function(thread, commenter, cb){
    
    var thread_contents = thread.contents;
    if(!thread_contents.length) return cb(new Error(push.genericErrorMsg+'thread is empty'));
    
    var recipients_map = {};
    //map
    thread.contents.forEach(function(comment){
        if(comment.username !== commenter) recipients_map[comment.username] = '';
    });
    //reduce
    var recipients_arr = [];
    for(var user in recipients_map){ recipients_arr.push(user); }
    
    console.log(recipients_arr)
    
    return cb(null, recipients_arr);
    
};
push.prepareRecipientNotifications = function(recipients, commenter, post_id, notif_type, cb){

    var poster_notif = {
        post: { $uuid: post_id },
        message: '',
        emitter: commenter,
        event: notif_type,
        type: 'direct'
    };
    var other_commenters_notif = {
        post: { $uuid: post_id },
        message: '',
        emitter: commenter,
        event: notif_type,
        type: 'list',
        targets: recipients
    };
    
    switch(notif_type){
        case 'comment':
            poster_notif.message = '{emitter} commented on your video';
            other_commenters_notif.message = '{emitter} also commented on {target} video';
            break;
        case 'like':
            poster_notif.message = '{emitter} liked your video';
            other_commenters_notif.targets = []; // only poster gets like notifications
            break;
    }
    
    var notifs = [];
    //if there are qualified recipients, queue push notifications
    notifs.push(poster_notif); // always
    if(other_commenters_notif.targets.length) notifs.push(other_commenters_notif);
    
    return cb(null, notifs);
};
