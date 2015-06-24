//module declaration
var util = module.exports = {};

//firebase util
util.firebase = {};
util.firebase.getLastChild = function(parent){
    
    var last;
    
    parent.forEach(function(child){ // iterate to the end of the list
        last = child;
    });
    
    return last;
    
};