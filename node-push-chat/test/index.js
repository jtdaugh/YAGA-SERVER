require('../globals');

var should = require('should');
var config = require('../config');

var firenode; // main app

var firebase = require('firebase');
var firedev;

// mock events
var mock_event = { first: 'thing' };
var mock_thread = {
    thread1: {
        comment1: { type: 'comment', comment: 'this rules!', username: 'dan' },
        comment2: { type: 'comment', comment: 'pretty cool!', username: 'dylan' }
    }
};
var mock_push_event = {
    _val: [
        { comment: 'nice', type: 'comment', username: 'dan', val: function(){ return this} },
        { comment: 'this rules!', type: 'comment', username: 'dylan', val: function(){ return this} } 
    ],
    _key: 'MOCK_EVENT',
    val: function(){ return this._val },
    key: function(){ return this._key; },
};
mock_push_event.forEach = function(iter){
    mock_push_event._val.forEach(function(elem){
        iter(elem);
    });
}

describe('firenode', function(){
    
    before(function(done){ // load a new dev connection
        firedev = new firebase(config.firebase.conn.dev);
        
        firedev.child('events').once('value',function(events){
            if(events.child('mock_event').exists()){
                firedev.child('events').child('mock_event').remove(done);
            }
            else return done();
        });
    });
    
    //firebase tests
    it('should connect to firebase', function(){
       var firebase = require('firebase');
       var conn = new firebase(config.firebase.conn.dev);
       
       conn.toString().should.equal(config.firebase.conn.dev);
    });
    it('should receive child_added events', function(done){
        var events = firedev.child('events');
        var loaded = false;
        
        $async.series([
                function(cb){
                    events.on('child_added', function(data){
                        if(!loaded) return;
                        
                        data.val().should.eql(mock_event);
                        done();
                    });
                    events.once('value', function(){
                        loaded = true;
                        cb(null);
                    })
                }
            ],
            
            function(err){
                events.child('mock_event').set(mock_event);
            }
        );
    });
    it('should receive child_changed events', function(done){
        var events = firedev.child('events');
        var loaded = false;
        
        $async.series([
                function(cb){
                    events.on('child_changed', function(data){
                        if(!loaded) return;
                        
                        data.val().should.have.property('first').equal('second');
                        done();
                    });
                    events.once('value', function(){ // called after initial db load
                        loaded = true;
                        cb(null);
                    });
                }
            ],
            
            function(err){
                events.child('mock_event').set(mock_event);
                events.child('mock_event').child('first').set('second');
            }
        );
        
    });
    
    //push notification handler tests
    it('should queue a new push event', function(done){
        
        var push = require('../push');
        
        $async.waterfall([
                function(cb){ return $lib.redis.del(mock_push_event.key(), cb) }, // reset rate limit
                function(res, cb){ return push(mock_push_event, cb) }
            ],
            
            function(err, notifs){
                console.log(err, notifs);
                
                should.not.exist(err);
                
                notifs.should.have.lengthOf(2);
                done();
            }
            
        );
        
    });
    
    //complete app tests
    // it('should receive a child_changed event and queue a push notification', function(done){
    //     var events = firenode.child('events');
    //     var loaded = false;
        
    //     $async.series([
    //             function(cb){
    //                 events.on('child_changed', function(data){
    //                     if(!loaded) return;
                        
                        
    //                     done();
    //                 });
    //                 events.once('value', function(){ // called after initial db load
    //                     loaded = true;
    //                     cb(null);
    //                 });
    //             }
    //         ],
            
    //         function(err){
    //             events.child('mock_event').set(mock_thread);
    //         }
    //     );
        
    // });
    
    after(function(done){
        firedev.child('events').once('value',function(events){
            if(events.child('mock_event').exists()){
                firedev.child('events').child('mock_event').remove(done);
            }
            else return done();
        });
    });
    
});