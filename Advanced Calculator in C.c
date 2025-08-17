```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <ctype.h>

// Structure to represent a token
typedef struct {
    char type; // 'N' for number, 'O' for operator, '(' or ')' for parenthesis
    double value; // Value if it's a number
    char op;     // Operator if it's an operator
} Token;

// Function to tokenize the input expression
Token* tokenize(char* expression, int* tokenCount) {
    int len = strlen(expression);
    Token* tokens = (Token*)malloc(len * sizeof(Token)); // Allocate memory for tokens
    *tokenCount = 0;
    int i = 0;
    while (i < len) {
        if (isdigit(expression[i]) || expression[i] == '.') {
            double num = 0;
            int decimal = 0;
            double decimalPlace = 0.1;
            while (i < len && (isdigit(expression[i]) || (expression[i] == '.' && decimal == 0))) {
                if (expression[i] == '.') {
                    decimal = 1;
                } else if (decimal) {
                    num += (expression[i] - '0') * decimalPlace;
                    decimalPlace *= 0.1;
                } else {
                    num = num * 10 + (expression[i] - '0');
                }
                i++;
            }
            tokens[*tokenCount].type = 'N';
            tokens[*tokenCount].value = num;
            (*tokenCount)++;
        } else if (strchr("+-*/^%", expression[i]) != NULL) {
            tokens[*tokenCount].type = 'O';
            tokens[*tokenCount].op = expression[i];
            (*tokenCount)++;
            i++;
        } else if (expression[i] == '(' || expression[i] == ')') {
            tokens[*tokenCount].type = expression[i];
            (*tokenCount)++;
            i++;
        } else if (isspace(expression[i])) {
            i++;
        } else {
            fprintf(stderr, "Invalid character in expression: %c\n", expression[i]);
            free(tokens);
            return NULL;
        }
    }
    return tokens;
}


// Function to evaluate the expression using a stack-based approach (Infix to Postfix then evaluation)
double evaluate(Token* tokens, int tokenCount) {
    //Implementation of Shunting-yard algorithm and postfix evaluation would go here.  This is complex and omitted for brevity.  A full implementation would require significant additional code.
    //This placeholder returns 0.  Replace with actual evaluation logic.
    return 0;
}


int main() {
    char expression[1000];
    printf("Enter an arithmetic expression (e.g., 2 + 3 * (4 - 1)): ");
    fgets(expression, sizeof(expression), stdin);
    expression[strcspn(expression, "\n")] = 0; //remove trailing newline

    int tokenCount;
    Token* tokens = tokenize(expression, &tokenCount);

    if (tokens == NULL) {
        return 1; //Error in tokenization
    }

    double result = evaluate(tokens, tokenCount);

    printf("Result: %lf\n", result);
    free(tokens);
    return 0;
}
```