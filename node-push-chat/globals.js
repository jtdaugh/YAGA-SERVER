//commonly used enough things that I don't feel guilty 
//about injecting into the GLOBALS tend to end up here :)

var GLOBAL_prefix = '$'; // prepended to every global

var globals = [ 
    
    //from node_modules
    'async',
    { name: 'log', value: require('bunyan').createLogger({ name: 'firenode', level: 'debug' }) },
    { name: 'argv', value: require('optimist').argv },
    
    //local modules
    { name: 'config', value: require('./config') },
    { name: 'lib', path: './lib' },
    
    //others
    { name: 'is_new_thread', value: 'false' }
    
];

globals.forEach(function(_global){
   
    var $ = GLOBAL_prefix;
    
    switch(typeof _global){
    
        case 'string': GLOBAL[$+_global] = require(_global); return;
        
        case 'object':
            if(!_global.name) return;
            
            if(_global.value) GLOBAL[$+_global.name] = _global.value;
            if(_global.path) GLOBAL[$+_global.name] = require(_global.path);
            
            return;
            
    }
   
});