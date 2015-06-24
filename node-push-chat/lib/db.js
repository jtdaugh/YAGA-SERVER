var config = require('../config');
var pg = require('pg');

var db = module.exports = (function(){
    // pg.connect(config.db.conn[process.env.NODE_ENV || 'dev'], function(err, client){
    //     if(err) throw err;
        
    //     console.log('pg connection successful');
    //     db.client = client;
    // });
})();

