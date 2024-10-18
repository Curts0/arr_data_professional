from inspect import getsource
from IPython.display import Code

def explain_code(func):
    """Helper function to break up the code.
    
    See `annualize` func as an example.
    Looks for comment blocks of # {number} and
    yields that specific block to break it down a bit better
    in a notebook output.
    """
    yield Code(func.__doc__, language= 'text')
    c = getsource(func).replace(func.__doc__, "")
    for x in range(1, 99):
        code_block = c[c.find(f"# {x}") : c.find(f"# {x+1}")]
        if len(code_block) > 0:
            yield Code(code_block, language= 'python3')
        else:
            break