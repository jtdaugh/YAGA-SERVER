/*
  iFireNode - apple push notification proxy for firebase events
*/

require('./globals'); // init globals

//external libs
var firebase = require('firebase'); // firebase.io driver

//module declaration
var firenode = module.exports = {
    root: new firebase( $config.firebase.conn[ process.env.NODE_ENV || 'dev' ] ),
    lib: $lib, // common resources
    push: require('./push') // push notification sub-module
};


/* pipe firebase listeners to push notifications */

//firebase data streams
firenode.events = firenode.root.child('events');

//handle new comments and likes
$log.info('firenode loading stored events...');
//begins stored event loading
firenode.events.on('child_added', handle_firebase_event);
firenode.events.on('child_changed', handle_firebase_event);

//keeps state of incoming data streams
//value event is called after initial stored event loading
firenode.events.once('value', function(){
    // all previously created comment threads have been received
    $is_new_thread = 'true';
    $log.info('...stored event loading complete');
    $log.info('firenode listening for new firebase events from '+firenode.root.toString()); 
    
});

function handle_firebase_event(data){ // main routine for incoming firebase events
    if($is_new_thread !== 'true') return; // this is an old thread or old comment, ignore
    
    $log.debug('event',data.key(),data.val());
    
    $async.waterfall([
            
            function(cb){ return firenode.push(data, cb) },
            function(notifs, cb){ 
                $log.info( { notifs: notifs }, 'queueing push notification');
                return firenode.lib.celery.queuePushNotifications(notifs, cb) 
            }
            
        ],
        
        function(err){
            if(err) return $log.error(err);
            
            $log.info('queued push notification');
        }
    );
    
}


//repl (for debugging, just "node index.js --repl (or -r for short)")
//the firenode object is provided in context
if($argv.repl || $argv.r){
    var repl = require('repl');
    var r = repl.start({
        prompt: '>'
    });
    r.context.firenode = firenode;
}
