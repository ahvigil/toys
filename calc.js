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
    
    e = e.trim(); // clean up if necessary
    
    // initial parsing of expression
    while(e.length>0) {
        // numbers go on number stack
        if (/\d/.test(e[0])) {
            // but check to see if number spans multiple digits
            var j=0;
            while(/\d/.test(e[j])) j++;
            numStack.push(Number(e.slice(0,j)));
            e=e.slice(j);
        }
        
        // push operators onto operator stack
        else if (OPERATORS.test(e[0])) {  // test to see if character is operator
            // always evaluate preceding '/' and '*' since they have priority
            if (opStack.peek() == '*' || opStack.peek() == '/') {
                OP_EXEC[opStack.pop()](numStack);
            }
            opStack.push(e[0]);
            e=e.slice(1);
        }
        
        // strip out parenthesis using recursion
        else if (e[0]=='(') {
            // match opening and closing parens
            var k = e.indexOf('(', 1);
            var j = e.indexOf(')', 1);
            while(k!=-1 && k<j){
                k= e.indexOf('(', k+1);
                j = e.indexOf(')', j+1);
            }

            var innerResult = evaluate(e.slice(1,j));
            numStack.push(innerResult);
            e = e.slice(j+1);
        }
        
        // don't know how to handle any other characters, but ignore whitespace
        else if (!/\s/.test(e[0])){ // if character is not whitespace
            process.stderr.write(e + "\nError parsing expression :" + e + "\n");
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
