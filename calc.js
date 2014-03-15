/******************************************
 *                                        *
 * Simple Node.js Expression Evaluator    *
 * Author: Arthur Vigil                   *
 *                                        *
 ******************************************/
var fs = require('fs'); // needed for file io

// list of operators as a regular expression
var OPERATORS = /[*/+-]/;
// and functions defining each operation in relation to stack of numbers
var OP_EXEC = {
    '*' : function(n) {n.push(n.pop()*n.pop());},
    '/' : function(n) {var y=n.pop(); n.push(n.pop()/y);},
    '+' : function(n) {n.push(n.pop()+n.pop());},
    '-' : function(n) {var y=n.pop(); n.push(n.pop()-y);}}

// add peek to my stack implementation, I hope that's not cheating
Array.prototype.peek = function(){
    return this.slice(-1)[0];
}

// evaluate an expression using number and operator stacks
function evaluate(e){
    var numStack = [];  // number stack
    var opStack = [];   // operator stack

    // initial parsing of expression
    for(var i=0;i<e.length;i++) {
        
        // numbers go on number stack
        if (/\d/.test(e[i])) {
            // but check to see if number spans multiple digits
            var j=i;
            while(/\d/.test(e[j+1])) j++;
            numStack.push(Number(e.slice(i,j+1)));
            i=j;
        }
        
        // push operators onto operator stack
        else if (OPERATORS.test(e[i])) {  // test to see if character is operator
            // always evaluate preceding '/' and '*' since they have priority
            if (opStack.peek() == '*' || opStack.peek() == '/') {
                OP_EXEC[opStack.pop()](numStack);
            }
            opStack.push(e[i]);
        }
        
        // strip out parenthesis using recursion
        else if (e[i]=='(') {
            var j = e.lastIndexOf(')');
            var innerResult = evaluate(e.slice(i+1,j));
            numStack.push(innerResult);
            e = e.slice(j);
            i=0;
        }
        
        // don't know how to handle any other characters, but ignore whitespace
        else if (!/\s/.test(e[i])){ // if character is not whitespace
            process.stderr.write(e + "\nError parsing expression at col:" + (i+1) + "\n");
            process.exit(1);
        }
    }
    
    // evaluate whatever is left after the first pass
    while(numStack.length>1){
        OP_EXEC[opStack.pop()](numStack);
    }
    
    return numStack.pop();
}

function main(){
    // check for proper number of arguments
    if (process.argv.length!=3) {
        process.stdout.write("Simple node.js expression evaluator by Arthur Vigil\n");
        process.stdout.write("Usage: node calc.js <filename>\n");
        process.exit(1);
    }
    
    // read from file and store expression as a string
    var e;
    try{e = fs.readFileSync(process.argv[2]).toString();}
    // or read expression straight from command line for debugging purposes
    catch(err){e=process.argv[2];}
    
    // call expression evaluator
    result = evaluate(e);

    process.stdout.write(result + "\n");
}

main();
