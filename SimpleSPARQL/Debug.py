from PrettyQuery import prettyquery

class Debug() :
    def __init__(self) :
        self.reset()

    def reset(self) :
        self.str = ""
        self.block_id = 0
        self.block_depth = 0

    def log(self, str, endline='<br>') :
        self.str += str + endline

    def p(self, *args) :
        self.log('<xmp>' + ' '.join([
            prettyquery(arg) for arg in args
        ]) + '</xmp>', '')

    def open_block(self, title) :
        """ this is used to generate HTML debug output.  Reset the
        output first by calling debug_reset, then make the compile
        call, then get the output by calling debugp"""

        self.str += """
            <div class="logblock">
            <div class="logblock-title" id="block-title-%d">%s</div>
            <div class="logblock-body" id="block-body-%d" style="display:none">
        """ % (self.block_id, title, self.block_id)
        self.block_id += 1
        self.block_depth += 1

    def close_block(self) :
        self.str += """</div></div>"""
        self.block_depth -= 1
                    
         
class DebugNop() :
    def nop(*args, **kwargs) : pass
    reset = log = p = ps = open_block = close_block = nop
    str = ''
