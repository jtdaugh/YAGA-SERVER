var pm2 = require('pm2');

pm2.connect(function(){
    pm2.start({
       script: 'index.js',
       max_memory_restart: '100M'
    }, function(){
        console.log('starting firenode...');
    });
})